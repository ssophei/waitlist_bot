from playwright.sync_api import sync_playwright
import re
import time
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()

# COURSE_URL = "https://classes.berkeley.edu/content/2026-fall-cyplan-101-001-lec-001"
COURSE_URL = "https://classes.berkeley.edu/content/2026-fall-econ-136-001-lec-001"
CHECK_EVERY_SECONDS = 300
already_alerted = False

def get_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(COURSE_URL, wait_until="networkidle")
        html = page.content()
        browser.close()
        return html

def check_waitlist():
    html = get_page_html()

    waitlisted_match = re.search(r"Waitlisted:<\/strong> (\d+)", html)
    max_match = re.search(r"Waitlist Max:<\/strong> (\d+)", html)
    class_title = re.search(r'class="sf--title--name">([a-zA-Z]* \d+)', html).group(1).strip()

    if not waitlisted_match or not max_match:
        print("Could not find waitlist info.")
        return

    waitlisted = int(waitlisted_match.group(1))
    waitlist_max = int(max_match.group(1))

    print(f"{waitlisted}/{waitlist_max} waitlisted")

    if waitlisted < waitlist_max:
        print("Spot opened!")
    return waitlisted, waitlist_max, class_title

def send_email(waitlisted, waitlist_max, class_title):
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
        f"Course Listing: {COURSE_URL}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

# while True:
#     waitlisted, waitlist_max = check_waitlist()

#     if waitlisted < waitlist_max and not already_alerted:
#         send_email(waitlisted, waitlist_max)
#         already_alerted = True
#         print("Email sent!")

#     if waitlisted >= waitlist_max:
#         already_alerted = False

#     time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    waitlisted, waitlist_max, class_title = check_waitlist()
    send_email(waitlisted, waitlist_max, class_title)