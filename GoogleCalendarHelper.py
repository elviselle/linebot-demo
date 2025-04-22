from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import base64
import json
import pytz
from datetime import datetime, timedelta

class GoogleCalendarOperation:

    tz = pytz.timezone("Asia/Taipei")
    BOOK_EVENT_TEMPLATE = {
        'summary': '【預約】$name$，來自 LINE官方帳號',
        'location': 'Line官方帳號',
        'description': 'user_id: $user_id$',
        'start': {
            'dateTime': '$start_time$',
            'timeZone': 'Asia/Taipei',
        },
        'end': {
            'dateTime': '$end_time$',
            'timeZone': 'Asia/Taipei',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 240},
            ],
        },
    }

    def __init__(self):
        SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_KEY')
        SERVICE_ACCOUNT_KEY += "=="
        CALENDAR_ID = os.getenv('CALENDAR_ID')
        SUBJECT_EMAIL = os.getenv('SUBJECT_EMAIL')

        self.service_account_key = SERVICE_ACCOUNT_KEY
        self.calendar_id = CALENDAR_ID
        self.subject_email = SUBJECT_EMAIL
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.credentials = self._create_credentials()
        self.service = self._create_service()

    def _create_credentials(self):
        decoded_bytes = base64.b64decode(self.service_account_key.encode("utf-8"))
        decoded_text = decoded_bytes.decode("utf-8")
        keyfile_dict = json.loads(decoded_text)
        credentials = service_account.Credentials.from_service_account_info(
            keyfile_dict, scopes=self.scopes
        )
        if self.subject_email:
            credentials = credentials.with_subject(self.subject_email)
        return credentials

    def _create_service(self):
        return build('calendar', 'v3', credentials=self.credentials)

    def list_calendars(self):
        calendar_list = self.service.calendarList().list().execute()
        return calendar_list.get('items', [])

    def create_event(self, username, user_id, date_str, time_str):
        # 合併成一個 datetime
        dt_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        start_time = self.tz.localize(dt_naive)
        end_time = start_time + timedelta(hours=2)

        event = self.BOOK_EVENT_TEMPLATE.copy()
        event['summary'] = event['summary'].replace("$name$", username, 1)
        event['description'] = event['description'].replace("$user_id$", user_id, 1)
        event['start']['dateTime'] = start_time.isoformat()
        event['end']['dateTime'] = end_time.isoformat()

        created_event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        return created_event


# Initialize the GoogleCalendarOperation class
# calendar_id = "your_calendar_id_here"  # Replace with your calendar ID
# subject_email = "your_subject_email_here"  # Replace with your subject email if needed
#google_calendar = GoogleCalendarOperation()

# Test listing calendars
#print("Listing calendars:")
#calendars = google_calendar.list_calendars()
#for calendar in calendars:
#    print(f"Name: {calendar['summary']}, ID: {calendar['id']}")

# Test creating an event
#print("\nCreating an event:")

#created_event = google_calendar.create_event("Elvis Wang", "U1234567890", "2025-04-23", "14:00")
#print(f"Event created: {created_event.get('htmlLink')}")