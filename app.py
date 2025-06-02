import os
import datetime
import random
import time
import schedule
import threading
from functools import wraps
import uuid

from flask import (Flask, render_template, url_for, request, redirect, session,
                   jsonify, flash)
from pymongo import MongoClient
from bson import ObjectId
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "a_very_secret_random_string_for_flask_session" # Hardcoded secret key
app.static_folder = 'static'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=8)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/" # Hardcoded MongoDB URI
DB_NAME = "HR"
HRC_COLLECTION_NAME = "HRC"
BANNER_COLLECTION_NAME = "banners"
GALLERY_COLLECTION_NAME = "gallery_photos"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
hrc_collection = db[HRC_COLLECTION_NAME]
banner_collection = db[BANNER_COLLECTION_NAME]
gallery_collection = db[GALLERY_COLLECTION_NAME]

# Pexels API Key & Video Directory
PEXELS_API_KEY = "W77xGNmh0HTU8txp4Q3gRTcXQ1LTLMMTwDdSrBhLbFVDuCWgHUTFWldK" # Hardcoded Pexels API Key - REPLACE THIS WITH YOUR ACTUAL KEY
VIDEO_DIR = os.path.join(app.static_folder, 'videos')
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# File Upload Configuration
BANNER_UPLOAD_FOLDER_REL = 'banners'
BANNER_UPLOAD_FOLDER_ABS = os.path.join(app.static_folder, BANNER_UPLOAD_FOLDER_REL)
app.config['BANNER_UPLOAD_FOLDER'] = BANNER_UPLOAD_FOLDER_ABS
if not os.path.exists(app.config['BANNER_UPLOAD_FOLDER']):
    os.makedirs(app.config['BANNER_UPLOAD_FOLDER'])

GALLERY_UPLOAD_FOLDER_REL = 'gallery_images'
GALLERY_UPLOAD_FOLDER_ABS = os.path.join(app.static_folder, GALLERY_UPLOAD_FOLDER_REL)
app.config['GALLERY_UPLOAD_FOLDER'] = GALLERY_UPLOAD_FOLDER_ABS
if not os.path.exists(app.config['GALLERY_UPLOAD_FOLDER']):
    os.makedirs(app.config['GALLERY_UPLOAD_FOLDER'])

# --- Pexels Video Functions ---
def get_time_of_day():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: return "morning fields"
    elif 12 <= hour < 17: return "afternoon city"
    elif 17 <= hour < 22: return "evening beach"
    else: return "night forest"

def download_pexels_video(query):
    file_name = f"{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.mp4"
    file_path = os.path.join(VIDEO_DIR, file_name)
    
    if os.path.exists(file_path):
        return os.path.join('videos', file_name)

    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE": # Check if default placeholder is still there
        print("Pexels API Key is missing or is the default placeholder. Please replace it with your actual key. Skipping video download.")
        return None
        
    headers = {'Authorization': PEXELS_API_KEY}
    random_page = random.randint(1, 3)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&page={random_page}&orientation=landscape"
    
    try:
        print(f"Pexels: Querying for '{query}' on page {random_page}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        videos_data = response.json()
        videos = videos_data.get('videos')
        
        if videos:
            selected_video_info = random.choice(videos)
            video_files = selected_video_info.get('video_files', [])
            
            video_link = next((vf['link'] for vf in video_files if vf.get('quality') == 'hd' and vf.get('file_type') == 'video/mp4' and vf.get('height', 0) >= 1080), None)
            if not video_link: video_link = next((vf['link'] for vf in video_files if vf.get('quality') == 'sd' and vf.get('file_type') == 'video/mp4' and vf.get('height', 0) >= 720), None)
            if not video_link: video_link = next((vf['link'] for vf in video_files if vf.get('file_type') == 'video/mp4'), None)
            if not video_link and video_files: video_link = video_files[0].get('link')

            if video_link:
                print(f"Pexels: Attempting to download video from {video_link} for query '{query}'")
                video_response = requests.get(video_link, stream=True, timeout=45)
                video_response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=1024*1024):
                        f.write(chunk)
                print(f"Pexels: Downloaded video '{file_name}' successfully.")
                return os.path.join('videos', file_name)
            else:
                print(f"Pexels: No suitable video file link found for query '{query}'. Video files received: {video_files}")
        else:
            print(f"Pexels: No videos found for query '{query}'. API response: {videos_data}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Pexels: Request failed for query '{query}': {e}")
        return None
    except Exception as e:
        print(f"Pexels: An error occurred during video download for query '{query}': {e}")
        return None

# --- Scheduler ---
def delete_old_videos():
    now = datetime.datetime.now()
    deleted_count = 0
    try:
        if not os.path.exists(VIDEO_DIR):
            print(f"Video directory {VIDEO_DIR} not found. Skipping cleanup.")
            return
        for filename in os.listdir(VIDEO_DIR):
            if not filename.lower().endswith('.mp4'):
                continue
            file_path = os.path.join(VIDEO_DIR, filename)
            if os.path.isfile(file_path):
                try:
                    parts = filename.rsplit('_', 1)
                    file_date_str = None
                    if len(parts) == 2 and len(parts[1]) == 12 and parts[1][:8].isdigit() and parts[1].endswith('.mp4'):
                        file_date_str = parts[1][:8]
                    
                    if file_date_str:
                        file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d')
                    else:
                        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if (now.date() - file_date.date()).days > 0: 
                        os.remove(file_path)
                        print(f"Scheduler: Deleted old video '{filename}' (date: {file_date.strftime('%Y-%m-%d')}).")
                        deleted_count +=1
                except ValueError:
                    print(f"Scheduler: Could not parse date from '{filename}', using modification time.")
                    file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if (now - file_mod_time).days >= 1:
                         os.remove(file_path)
                         print(f"Scheduler: Deleted old video by mod time '{filename}'.")
                         deleted_count +=1
                except Exception as e:
                    print(f"Scheduler: Error processing or deleting video '{filename}': {e}")
        if deleted_count > 0:
            print(f"Scheduler: Video cleanup complete. Deleted {deleted_count} old videos.")
        else:
            print("Scheduler: No old videos found to delete.")
    except Exception as e:
        print(f"Scheduler: An error occurred during video cleanup: {e}")


# --- CARD_STRUCTURES Definition ---
CARD_STRUCTURES = {
    "Office Rules": {
        "fields": {"rule": "text"},
        "labels": {"rule": "Rule Description"}
    },
    "Upcoming Events": {
        "fields": {"event_name": "text", "event_date": "date"},
        "labels": {"event_name": "Event Name", "event_date": "Date"}
    },
    "Birthdays This Week": {
        "fields": {"employee_name": "text", "birthday_date": "date"},
        "labels": {"employee_name": "Employee Name", "birthday_date": "Birthday Date"}
    },
    "Anniversaries": {
        "fields": {"names": "text", "anniversary_date": "date"},
        "labels": {"names": "Names (e.g., John & Jane)", "anniversary_date": "Anniversary Date"}
    },
    "Quick Links": {
        "fields": {"link_name": "text", "link_url": "url"},
        "labels": {"link_name": "Link Display Name", "link_url": "URL (include http/https or #anchor)"}
    },
    "Leave Portal": {
        "fields": {"link_name": "text", "link_url": "url"},
        "labels": {"link_name": "Portal Link Name", "link_url": "URL (include http/https or #anchor)"}
    },
    "Social Media Highlights": {
        "fields": {"text": "textarea"},
        "labels": {"text": "Highlight Content / Update"}
    },
    "Career Opportunities": {
        "fields": {"job_title": "text", "department": "text", "details_url": "url"},
        "labels": {"job_title": "Job Title", "department": "Department (Optional)", 
                     "details_url": "Link to Details (Optional, include http/https or #anchor)"}
    },
    "Word from HR": {
        "fields": {"text": "textarea"},
        "labels": {"text": "Message from HR"}
    },
    "Quick Reminders": {
        "fields": {"reminder": "text"},
        "labels": {"reminder": "Reminder Text"}
    },
    "Upcoming Holidays": {
        "fields": {"holiday_name": "text", "holiday_date": "date"},
        "labels": {"holiday_name": "Holiday Name", "holiday_date": "Date"}
    },
    "Legacy Gallery Info": { 
        "fields": {"info": "text"},
        "labels": {"info": "Legacy Information (data[11] placeholder)"}
    },
    "Rewards & Recognitions": { 
        "fields": {"employee_name":"text", "employee_title":"text", "award":"text"},
        "labels": {"employee_name":"Employee Name", "employee_title":"Title/Department", "award":"Recognition/Award Details"}
    },
    "Fun Facts": { 
        "fields": {"fact": "textarea"},
        "labels": {"fact": "Fun Fact"}
    }
}


# --- Main App Route ---
@app.route("/")
def index():
    time_of_day_query = get_time_of_day()
    video_rel_path = download_pexels_video(time_of_day_query)
    video_filename_for_template = video_rel_path if video_rel_path else 'videos/default_bg.mp4'

    raw_hrc_data = list(hrc_collection.find())
    main_dashboard_data_processed = []
    expected_titles_ordered = list(CARD_STRUCTURES.keys())
    cards_by_title_from_db = {card.get('title'): card for card in raw_hrc_data if card.get('title')}

    for title in expected_titles_ordered:
        card = cards_by_title_from_db.get(title)
        if card:
            card['_id'] = str(card['_id'])
            if 'data' in card and isinstance(card['data'], list):
                for item in card['data']:
                    if isinstance(item, dict) and '_id' in item:
                        item['_id'] = str(item['_id'])
            main_dashboard_data_processed.append(card)
        else:
            print(f"Warning: Card with title '{title}' not found in DB. Adding placeholder for template index.")
            main_dashboard_data_processed.append({
                "_id": str(ObjectId()), 
                "title": title, # Keep the title for admin form generation even if no data
                "data": []
            })
            
    banners = list(banner_collection.find().sort("created_at", -1))
    for banner in banners: banner['_id'] = str(banner['_id'])

    gallery_photos = list(gallery_collection.find().sort("created_at", -1))
    for photo in gallery_photos: photo['_id'] = str(photo['_id'])
    
    return render_template(
        "hero2.html",
        data=main_dashboard_data_processed,
        video_filename=video_filename_for_template,
        banners=banners,
        gallery_photos=gallery_photos,
        admin_logged_in=session.get('admin_logged_in', False),
        CARD_STRUCTURES_FOR_TEMPLATE=CARD_STRUCTURES if session.get('admin_logged_in', False) else None
    )

# --- Admin Authentication ---
ADMIN_USERNAME = "admin" # Hardcoded admin username
ADMIN_PASSWORD = "yoursecurepassword" # Hardcoded admin password - CHANGE THIS IMMEDIATELY

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access this functionality.', 'warning')
            next_url = request.script_root + request.path
            if request.query_string:
                next_url += '?' + request.query_string.decode('utf-8')
            return redirect(url_for('login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        if username == "admin" and password == "password":
            session['admin_logged_in'] = True
            session.permanent = True
            flash('Login successful!', 'success')
            next_url = request.args.get('next')
            if next_url and (next_url.startswith('/') or next_url.startswith(request.url_root)):
                 return redirect(next_url)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    # Ensure you have a 'login.html' in your 'templates' folder
    return render_template('login.html') 

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- Admin Actions ---
@app.route('/admin_action/add_banner', methods=['POST'])
@login_required
def add_banner_action():
    anchor = '#banners_section'
    if 'banner_image' not in request.files:
        flash('No image file part provided.', 'danger')
    else:
        file = request.files['banner_image']
        title = request.form.get('banner_title')
        description = request.form.get('banner_description')

        if file.filename == '': flash('No image selected for upload.', 'danger')
        elif not title or not description: flash('Banner title and description are required.', 'danger')
        elif file:
            filename = secure_filename(file.filename)
            try:
                save_path = os.path.join(app.config['BANNER_UPLOAD_FOLDER'], filename)
                file.save(save_path)
                banner_data = {
                    "image_path": os.path.join(BANNER_UPLOAD_FOLDER_REL, filename), "title": title, 
                    "description": description, "created_at": datetime.datetime.now(datetime.timezone.utc)
                }
                banner_collection.insert_one(banner_data)
                flash('Banner added successfully!', 'success')
            except Exception as e:
                flash(f'Error saving banner: {e}', 'danger')
    return redirect(url_for('index') + anchor)

@app.route('/admin_action/delete_banner/<banner_id_str>', methods=['POST'])
@login_required
def delete_banner_action(banner_id_str):
    anchor = '#banners_section'
    try:
        banner = banner_collection.find_one_and_delete({"_id": ObjectId(banner_id_str)})
        if banner:
            if banner.get('image_path'):
                abs_image_path = os.path.join(app.static_folder, banner['image_path'])
                if os.path.exists(abs_image_path):
                    try: os.remove(abs_image_path)
                    except OSError as e: flash(f"Error deleting image file '{banner['image_path']}': {e}", 'warning')
            flash('Banner deleted successfully!', 'success')
        else: flash('Banner not found.', 'danger')
    except Exception as e: flash(f"Error deleting banner: {e}", 'danger')
    return redirect(url_for('index') + anchor)

@app.route('/admin_action/add_gallery_photo', methods=['POST'])
@login_required
def add_gallery_photo_action():
    anchor = '#gallery_section'
    if 'gallery_image' not in request.files:
        flash('No image file provided for gallery.', 'danger')
    else:
        file = request.files['gallery_image']
        caption = request.form.get('gallery_caption', '')
        if file.filename == '': flash('No image selected for gallery upload.', 'danger')
        elif file:
            filename = secure_filename(file.filename)
            try:
                save_path = os.path.join(app.config['GALLERY_UPLOAD_FOLDER'], filename)
                file.save(save_path)
                photo_data = {
                    "image_url": os.path.join(GALLERY_UPLOAD_FOLDER_REL, filename), "caption": caption,
                    "created_at": datetime.datetime.now(datetime.timezone.utc)
                }
                gallery_collection.insert_one(photo_data)
                flash('Gallery photo added successfully!', 'success')
            except Exception as e: flash(f'Error saving gallery photo: {e}', 'danger')
    return redirect(url_for('index') + anchor)

@app.route('/admin_action/delete_gallery_photo/<photo_id_str>', methods=['POST'])
@login_required
def delete_gallery_photo_action(photo_id_str):
    anchor = '#gallery_section'
    try:
        photo = gallery_collection.find_one_and_delete({"_id": ObjectId(photo_id_str)})
        if photo:
            if photo.get('image_url'):
                abs_image_path = os.path.join(app.static_folder, photo['image_url'])
                if os.path.exists(abs_image_path):
                    try: os.remove(abs_image_path)
                    except OSError as e: flash(f"Error deleting image file '{photo['image_url']}': {e}", 'warning')
            flash('Gallery photo deleted successfully!', 'success')
        else: flash('Gallery photo not found.', 'danger')
    except Exception as e: flash(f"Error deleting gallery photo: {e}", 'danger')
    return redirect(url_for('index') + anchor)

@app.route('/admin_action/add_hrc_item/<card_id_str>', methods=['POST'])
@login_required
def add_hrc_item_action(card_id_str):
    anchor = f'#card_admin_{card_id_str}'
    try: card_obj_id = ObjectId(card_id_str)
    except Exception: flash("Invalid Card ID.", 'danger'); return redirect(url_for('index'))

    card_doc = hrc_collection.find_one({"_id": card_obj_id})
    if not card_doc: flash("Card not found.", 'danger'); return redirect(url_for('index'))

    card_title = card_doc.get("title")
    if not card_title or card_title not in CARD_STRUCTURES:
        flash(f"Admin Error: Card title '{card_title}' is misconfigured or not in CARD_STRUCTURES. Cannot add item.", 'danger')
        return redirect(url_for('index') + anchor)

    structure_info = CARD_STRUCTURES[card_title]
    new_item_data = {"_id": str(uuid.uuid4())}
    is_valid = True

    for field_name, field_type in structure_info["fields"].items():
        value = request.form.get(field_name)
        label_text = structure_info["labels"].get(field_name, field_name.replace('_', ' ').capitalize())
        is_optional = "optional" in label_text.lower()

        if not value and not is_optional:
            if field_type in ["text", "textarea", "url"] and not (field_type == "url" and value == "#"): # Allow '#' for URLs if needed for optional links
                flash(f"Field '{label_text}' is required for '{card_title}'. Value received: '{value}'", 'danger')
                is_valid = False; break
        
        if field_type == 'url' and value and value != "#" and not (value.startswith(('http://', 'https://', '/'))): # Allow relative paths starting with /
            flash(f"Field '{label_text}' for '{card_title}' must be a valid URL (e.g., http://example.com), an anchor (#section), or a relative path (/page).", 'danger')
            is_valid = False; break
        
        new_item_data[field_name] = value.strip() if isinstance(value, str) else value

    if is_valid:
        result = hrc_collection.update_one(
            {"_id": card_obj_id},
            {"$push": {"data": new_item_data}}
        )
        if result.modified_count > 0:
            flash(f"Item added to '{card_title}' successfully.", 'success')
        else:
            flash(f"Failed to add item to '{card_title}'. Please try again.", 'danger')
            
    return redirect(url_for('index') + anchor)

@app.route('/admin_action/delete_hrc_item/<card_id_str>/<item_id_str>', methods=['POST'])
@login_required
def delete_hrc_item_action(card_id_str, item_id_str):
    anchor = f'#card_admin_{card_id_str}'
    try: card_obj_id = ObjectId(card_id_str)
    except Exception: flash("Invalid Card ID.", 'danger'); return redirect(url_for('index'))
    
    if not item_id_str:
        flash("Item ID missing, cannot delete.", 'danger')
        return redirect(url_for('index') + anchor)

    result = hrc_collection.update_one(
        {"_id": card_obj_id},
        {"$pull": {"data": {"_id": item_id_str}}}
    )
    if result.modified_count > 0: flash("Item deleted successfully.", 'success')
    else: flash("Item not found in card or could not be deleted. It might have already been removed.", 'warning')
    return redirect(url_for('index') + anchor)

# --- Initial Data Setup Helper ---
def ensure_initial_data():
    print("Verifying initial data structure and HRC card order...")
    
    default_video_path = os.path.join(VIDEO_DIR, 'default_bg.mp4')
    if not os.path.exists(default_video_path):
        print(f"Warning: Default background video {default_video_path} not found. Please add one, or ensure Pexels download works and PEXELS_API_KEY is set.")

    expected_card_titles_in_order = list(CARD_STRUCTURES.keys())

    if hrc_collection.count_documents({}) == 0:
        print("HRC collection is empty. Creating initial cards in specified order...")
        for title in expected_card_titles_in_order:
            if title in CARD_STRUCTURES:
                structure_def = CARD_STRUCTURES[title]
                sample_item_data = {"_id": str(uuid.uuid4())}
                for field, f_type in structure_def["fields"].items():
                    # Pre-fill with more specific sample data
                    if field == "rule": sample_item_data[field] = "Maintain a clean workspace."
                    elif field == "event_name": sample_item_data[field] = "Quarterly Review Meeting"
                    elif field == "event_date": sample_item_data[field] = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                    elif field == "employee_name": sample_item_data[field] = "Jamie Oliver"
                    elif field == "birthday_date": sample_item_data[field] = (datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
                    elif field == "names": sample_item_data[field] = "Sales Team (Target Achieved)"
                    elif field == "anniversary_date": sample_item_data[field] = (datetime.date.today() + datetime.timedelta(days=20)).strftime("%Y-%m-%d")
                    elif field == "link_name": sample_item_data[field] = "IT Support Portal"
                    elif field == "link_url": sample_item_data[field] = "#support"
                    elif field == "text" and title == "Social Media Highlights": sample_item_data[field] = "Our new product launch was a success! #Innovation"
                    elif field == "job_title": sample_item_data[field] = "Marketing Specialist"
                    elif field == "department" and title == "Career Opportunities": sample_item_data[field] = "Marketing"
                    elif field == "details_url" and title == "Career Opportunities": sample_item_data[field] = "#careers/marketing"
                    elif field == "text" and title == "Word from HR": sample_item_data[field] = "Please update your emergency contact details in the HR portal."
                    elif field == "reminder": sample_item_data[field] = "Team lunch this Friday at 1 PM."
                    elif field == "holiday_name": sample_item_data[field] = "Long Weekend Ahead"
                    elif field == "holiday_date": sample_item_data[field] = (datetime.date.today() + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
                    elif field == "info" and title == "Legacy Gallery Info": sample_item_data[field] = "This card is a placeholder for data[11] if needed. You can remove it from CARD_STRUCTURES and ensure_initial_data if not used."
                    elif field == "award" and title == "Rewards & Recognitions": sample_item_data[field] = "Innovator of the Quarter"
                    elif field == "employee_title" and title == "Rewards & Recognitions": sample_item_data[field] = "Engineering Lead"
                    elif field == "fact": sample_item_data[field] = "A group of flamingos is called a 'flamboyance'."
                    else: sample_item_data[field] = f"Sample data for {field}"
                
                hrc_collection.insert_one({"title": title, "data": [sample_item_data]})
                print(f"  Created card: {title}")
            else:
                # This case should ideally not be hit if expected_card_titles_in_order is derived from CARD_STRUCTURES
                print(f"  Warning: Title '{title}' in expected order not found in CARD_STRUCTURES. Skipping initial card creation.")
    else:
        print("HRC collection not empty. Verifying existing cards against CARD_STRUCTURES order and ensuring item _ids...")
        for title in expected_card_titles_in_order:
            card_doc = hrc_collection.find_one({"title": title})
            if not card_doc:
                print(f"  Warning: Expected card '{title}' (based on CARD_STRUCTURES order) not found in DB. This may affect data[N] indexing in the template. Consider creating it or ensuring all expected cards exist.")
            elif "data" in card_doc and isinstance(card_doc["data"], list):
                updated_data_list = []
                needs_db_update = False
                for item in card_doc["data"]:
                    if isinstance(item, dict):
                        if "_id" not in item or not isinstance(item["_id"], str):
                            item["_id"] = str(uuid.uuid4())
                            needs_db_update = True
                        # Ensure all defined fields exist in item, add as None if missing
                        if title in CARD_STRUCTURES:
                             for field_name_in_struct in CARD_STRUCTURES[title]["fields"]:
                                 if field_name_in_struct not in item:
                                     item[field_name_in_struct] = None
                                     # needs_db_update = True # Could be too aggressive, only add if necessary
                    else: # Item is not a dict
                        if title == "Office Rules" and isinstance(item, str):
                            print(f"  Converting string item in '{title}' to dict: '{item}'")
                            item = {"rule": item, "_id": str(uuid.uuid4())}
                            needs_db_update = True
                        else:
                           print(f"  Warning: Item in '{title}' is not a dictionary and not 'Office Rules' string. Structure: {item}")
                    updated_data_list.append(item)
                
                if needs_db_update:
                    hrc_collection.update_one({"_id": card_doc["_id"]}, {"$set": {"data": updated_data_list}})
                    print(f"  Updated items structure in '{title}' for consistency.")
    
    default_banner_img_path = os.path.join(app.static_folder, BANNER_UPLOAD_FOLDER_REL, "default_banner.png")
    if not os.path.exists(default_banner_img_path): print(f"Warning: Default banner image not found at {default_banner_img_path}")
    if banner_collection.count_documents({}) == 0:
        banner_collection.insert_one({
            "image_path": os.path.join(BANNER_UPLOAD_FOLDER_REL, "default_banner.png"),
            "title": "Welcome Aboard!", "description": "Discover what's new and exciting.",
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }); print("Created initial default banner.")

    default_gallery_img_path = os.path.join(app.static_folder, GALLERY_UPLOAD_FOLDER_REL, "default_gallery.jpg")
    if not os.path.exists(default_gallery_img_path): print(f"Warning: Default gallery image not found at {default_gallery_img_path}")
    if gallery_collection.count_documents({}) == 0:
        gallery_collection.insert_one({
            "image_url": os.path.join(GALLERY_UPLOAD_FOLDER_REL, "default_gallery.jpg"), "caption": "Our Awesome Team",
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }); print("Created initial default gallery photo.")
    print("Initial data setup/verification complete.")


if __name__ == "__main__":
    ensure_initial_data()

    schedule.every().day.at("02:30").do(delete_old_videos) # Adjusted time
    def run_scheduler():
        print("Background scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(50) # Check frequency

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print(f"Scheduler thread status: {'Alive' if scheduler_thread.is_alive() else 'Not Alive'}")

    print(f"Flask app starting. Admin user: '{ADMIN_USERNAME}', PEXELS_API_KEY configured: {'Yes' if PEXELS_API_KEY and PEXELS_API_KEY != 'YOUR_PEXELS_API_KEY_HERE' else 'NO - Using placeholder or missing!'}")
    app.run(debug=True, port=5001)