from flask import Flask, render_template, url_for
from pymongo import MongoClient
import requests
import os
import datetime
import random

app = Flask(__name__)
app.static_folder = 'static'

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
DB_NAME = "HR"
COLLECTION_NAME = "HRC"

# Pexels API Key
PEXELS_API_KEY = "W77xGNmh0HTU8txp4Q3gRTcXQ1LTLMMTwDdSrBhLbFVDuCWgHUTFWldK"

# Video Directory
VIDEO_DIR = os.path.join(app.static_folder, 'videos')
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Banner Collection
BANNER_COLLECTION_NAME = "banners"
banner_collection = db[BANNER_COLLECTION_NAME]

# Banner Schema
banner_schema = {
    "image_path": str,
    "title": str,
    "description": str,
    "created_at": datetime.datetime.now()
}

def get_time_of_day():
    now = datetime.datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "morning sky"
    elif 12 <= hour < 17:
        return "afternoon landscape"
    elif 17 <= hour < 22:
        return "evening buildings"
    else:
        return "night sky"

def download_pexels_video(query):
    file_name = f"{query}.mp4"
    file_path = os.path.join(VIDEO_DIR, file_name)
    if os.path.exists(file_path):
        return file_path
    headers = {'Authorization': PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        videos = response.json()['videos']
        if videos:
            video_files = videos[0]['video_files']
            hd_video = next((vf for vf in video_files if vf['quality'] == 'hd' and vf['file_type'] == 'video/mp4'), None)
            if not hd_video:
                hd_video = next((vf for vf in video_files if vf['quality'] == 'sd' and vf['file_type'] == 'video/mp4'), None)
            if not hd_video:
                hd_video = next((vf for vf in video_files if vf['file_type'] == 'video/mp4'), video_files[0])
            video_url = video_files[0]['link']
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return file_path
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import requests
import datetime
import random
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/banners'
app = Flask(__name__)
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    time_of_day = get_time_of_day()
    video_path = download_pexels_video(time_of_day)
    if video_path:
        video_filename = os.path.basename(video_path)
    else:
        video_filename = "rain.mp4" # Default video

    # Fetch data from MongoDB on every request
    data = list(collection.find())
    banners = list(banner_collection.find())
    # Pass data to the template
    return render_template("hero2.html", data=data, video_filename=video_filename, banners=banners)

@app.route('/upload_banner', methods=['POST'])
def upload_banner():
    if 'banner_image' not in request.files:
        return "No file part"
    file = request.files['banner_image']
    if file.filename == '':
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Store banner information in MongoDB
        banner_data = {
            "image_path": file_path,
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "created_at": datetime.datetime.now()
        }
        banner_collection.insert_one(banner_data)
        return redirect(url_for('index'))

import time
import schedule

def delete_old_videos():
    now = datetime.datetime.now()
    for filename in os.listdir(VIDEO_DIR):
        file_path = os.path.join(VIDEO_DIR, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_creation_time).days >= 1:
                os.remove(file_path)
                print(f"Deleted old video: {filename}")

schedule.every().day.at("00:00").do(delete_old_videos)

import threading

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
@app.route("/api/banners")
def get_banners():
    banners = list(banner_collection.find())
    # Convert ObjectId to string for JSON serialization
    for banner in banners:
        banner['_id'] = str(banner['_id'])
    return jsonify(banners)

from flask import jsonify


@app.route("/api/banners/<banner_id>")
def get_banner(banner_id):
    banner = banner_collection.find_one({"_id": ObjectId(banner_id)})
    if banner:
        banner['_id'] = str(banner['_id'])
        return jsonify(banner)
    else:
        return jsonify({"message": "Banner not found"}), 404

from bson import ObjectId


@app.route("/api/banners", methods=['POST'])
def create_banner():
    if 'banner_image' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['banner_image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Store banner information in MongoDB
        title = request.form.get('title')
        description = request.form.get('description')
        if not title or not description:
            return jsonify({"message": "Title and description are required"}), 400

        banner_data = {
            "image_path": file_path,
            "title": title,
            "description": description,
            "created_at": datetime.datetime.now()
        }
        banner_id = banner_collection.insert_one(banner_data).inserted_id
        banner = banner_collection.find_one({"_id": banner_id})
        banner['_id'] = str(banner['_id'])
        return jsonify(banner), 201


@app.route("/api/banners/<banner_id>", methods=['DELETE'])
def delete_banner(banner_id):
    banner = banner_collection.find_one({"_id": ObjectId(banner_id)})
    if not banner:
        return jsonify({"message": "Banner not found"}), 404

    image_path = banner['image_path']
    try:
        os.remove(image_path)
    except OSError as e:
        print(f"Error deleting image: {e}")
        return jsonify({"message": "Error deleting image"}), 500

    banner_collection.delete_one({"_id": ObjectId(banner_id)})
    return jsonify({"message": "Banner deleted successfully"}), 200

app.run(debug=True, port=5001)
