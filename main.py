from playwright.sync_api import sync_playwright
import re
import time
import json
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()

STATE_FILE = "state.json"

def load_courses():
    with open("courses.json", "r") as f:
        return json.load(f) 

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def already_sent(state, url):
    return state.get(url) == "sent"

def mark_sent(state, url):
    state[url] = "sent"

def get_page_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()
        return html

def check_waitlist(url):
    html = get_page_html(url)

    waitlisted_match = re.search(r"Waitlisted:<\/strong> (\d+)", html)
    max_match = re.search(r"Waitlist Max:<\/strong> (\d+)", html)
    # class_title = re.search(r'class="sf--title--name">([a-zA-Z]* \d+)', html).group(1).strip()

    if not waitlisted_match or not max_match:
        print("Could not find waitlist info.")
        return

    waitlisted = int(waitlisted_match.group(1))
    waitlist_max = int(max_match.group(1))

    print(f"{waitlisted}/{waitlist_max} waitlisted")

    if waitlisted < waitlist_max:
        print("Spot opened!")
    return waitlisted, waitlist_max

def send_email(class_title, url, waitlisted, waitlist_max):
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    TO_EMAIL = os.getenv("TO_EMAIL")

    msg = EmailMessage()
    msg["Subject"] = f"{class_title} Waitlist Status Update"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    msg.set_content(
        f"A position on the {class_title} waitlist has been made available.\n\n"
        f"Waitlisted: {waitlisted} \nWaitlist Max: {waitlist_max}\n"
        f"Course Listing: {url}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

def remove_stale_state_entries(state, courses):
    valid_urls = {course["url"] for course in courses}
    return {url: value for url, value in state.items() if url in valid_urls}

if __name__ == "__main__":
    courses = load_courses()
    state = load_state()

    state = remove_stale_state_entries(state, courses)

    for course in courses:
        title = course["title"]
        url = course["url"]

        if already_sent(state, url):
            print(f"Already sent for {title}. Skipping.")
            continue

        waitlisted, waitlist_max = check_waitlist(url)

        if waitlisted < waitlist_max:
            send_email(title, url, waitlisted, waitlist_max)
            mark_sent(state, url)
            print(f"Email sent for {title}.")

    save_state(state)