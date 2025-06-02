# Database Plan for hero2.html

This document outlines the plan for structuring the data from `hero2.html` into a MongoDB database.

**Database Name:** `HR`

**Collection Name:** `HRC`

## Collections and Fields

*   **`office_rules`:**
    *   `rule` (String): Each office rule.
*   **`upcoming_events`:**
    *   `event_name` (String): The name of the event.
    *   `event_date` (String): The date of the event.
*   **`birthdays`:**
    *   `employee_name` (String): The name of the employee.
    *   `birthday_date` (String): The birthday date.
*   **`anniversaries`:**
    *   `names` (String): The names of the people celebrating the anniversary.
    *   `anniversary_date` (String): The anniversary date.
*   **`quick_links`:**
    *   `link_name` (String): The name of the link.
    *   `link_url` (String): The URL of the link.
*   **`leave_portal_links`:**
    *   `link_name` (String): The name of the link.
    *   `link_url` (String): The URL of the link.
*   **`social_media_highlights`:**
    *   `text` (String): The text content of the social media highlight.
*   **`career_opportunities`:**
    *   `job_title` (String): The title of the job.
*   **`word_from_hr`:**
    *   `text` (String): The text content from HR.
*   **`quick_reminders`:**
    *   `reminder` (String): Each quick reminder.
*   **`upcoming_holidays`:**
    *   `holiday_name` (String): The name of the holiday.
    *   `holiday_date` (String): The date of the holiday.
*   **`photo_gallery`:**
    *   `image_url` (String): The URL of the image.
*   **`rewards_recognitions`:**
    *   `employee_name` (String): The name of the employee.
    *   `employee_title` (String): The title of the employee.
    *   `award` (String): The award received by the employee.

*   **`banners`:**
    *   `image_path` (String): The path to the banner image.
    *   `title` (String): The title of the banner.
    *   `description` (String): The description of the banner.
    *   `created_at` (DateTime): The date and time the banner was created.