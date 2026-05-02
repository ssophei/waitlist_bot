# Berkeley Waitlist Notification Bot

This bot checks selected Berkeley course pages and sends an email notification when a waitlist spot opens.

## Setup

### 1. Get App Password

Use a non-UC Berkeley affiliated Google account for the steps below. 
1. Go to: https://myaccount.google.com/  
2. In the search bar, type **"App passwords"**  
3. Select **App passwords**  
4. Add a new app (you can name it anything, e.g. "Waitlist Bot")  
5. Copy the generated **16-character app password**

Use this value for `EMAIL_APP_PASSWORD` in your GitHub secrets.

### 2. Add Github Secrets

You must be working in a fork of this repository in order to add your own secrets. Once forked, go to: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

```env
EMAIL_ADDRESS=example@gmail.com
EMAIL_APP_PASSWORD=aaaa aaaa aaaa aaaa
TO_EMAIL=example@gmail.com
```
| Secret               | Description                                       |
| -------------------- | ------------------------------------------------- |
| `EMAIL_ADDRESS`      | Gmail address used to send notifications          |
| `EMAIL_APP_PASSWORD` | Gmail app password for the sending email          |
| `TO_EMAIL`           | Email address that should receive waitlist alerts |

### 3. Add courses to `courses.json`

Edit `courses.json` and add each course you want to track:

```json
[
  {
    "title": "CYPLAN 101",
    "url": "https://classes.berkeley.edu/content/2026-fall-cyplan-101-001-lec-001"
  }
]
```
The bot will run automatically after each push and every 10 minutes to check for open waitlist spots.

 **Note:** GitHub Actions schedules are not exact. Runs occur on fixed UTC intervals (`:00, :10, :20, ...`) and may be delayed by a few minutes. If needed, you can manually trigger the bot from the **Actions** tab using `workflow_dispatch`.

## How it Works

The bot runs automatically through GitHub Actions. It checks the course URLs in `courses.json`. If a course has an open waitlist spot, it sends an email alert to `TO_EMAIL`.

