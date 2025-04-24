import os
import base64
import json
import pytz
import logging
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendarOperation:

    # Initialize logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    tz = pytz.timezone("Asia/Taipei")

    BOOK_EVENT_TEMPLATE = {
        "summary": "【預約】$name$，來自 LINE官方帳號",
        "location": "店內消費",
        "description": "user_id: $user_id$",
        "start": {
            "dateTime": "$start_time$",
            "timeZone": "Asia/Taipei",
        },
        "end": {
            "dateTime": "$end_time$",
            "timeZone": "Asia/Taipei",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 240},
            ],
        },
    }

    def __init__(self):
        SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY")
        SERVICE_ACCOUNT_KEY += "=="
        CALENDAR_ID = os.getenv("CALENDAR_ID")
        SUBJECT_EMAIL = os.getenv("SUBJECT_EMAIL")

        self.service_account_key = SERVICE_ACCOUNT_KEY
        self.calendar_id = CALENDAR_ID
        self.subject_email = SUBJECT_EMAIL
        self.scopes = ["https://www.googleapis.com/auth/calendar"]
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
        return build("calendar", "v3", credentials=self.credentials)

    def list_calendars(self):
        calendar_list = self.service.calendarList().list().execute()
        return calendar_list.get("items", [])

    def create_event(self, username, user_id, date_str, time_str):
        # 合併成一個 datetime
        dt_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        start_time = self.tz.localize(dt_naive)
        end_time = start_time + timedelta(hours=2)

        event = self.BOOK_EVENT_TEMPLATE.copy()
        event["summary"] = event["summary"].replace("$name$", username, 1)
        event["description"] = event["description"].replace("$user_id$", user_id, 1)
        event["start"]["dateTime"] = start_time.isoformat()
        event["end"]["dateTime"] = end_time.isoformat()

        created_event = (
            self.service.events()
            .insert(calendarId=self.calendar_id, body=event)
            .execute()
        )
        # self.logger.info(f"Created Event: {created_event}")
        return created_event

    def get_config_event(self):
        events_result = (f
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin="2020-01-01T00:00:00+08:00",
                timeMax="2020-01-01T01:00:00+08:00",
                q="Config",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        app_config = {}
        for event in events:
            event_start = event["start"].get("dateTime", event["start"].get("date"))
            event_end = event["end"].get("dateTime", event["end"].get("date"))
            event_summary = event.get("summary", "No Title")
            event_description = event.get("description", "No Description")
            self.logger.info(
                f"Event: {event_summary}, Start: {event_start}, End: {event_end}, Description: {event_description}"
            )
            try:
                app_config = json.loads(event_description)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode event description as JSON: {e}")
                app_config = {}
        return app_config

    def get_upcoming_events(self, user_id, days=3):

        has_booked = False
        hours = ["10:00", "13:00", "15:00", "17:00"]
        available_hours = {}
        booked_hours = {}
        now = datetime.now(self.tz)
        for i in range(1, days + 1):
            day_availables = []
            day_booked = []
            for hour in hours:
                day = now + timedelta(days=i)
                dt_naive = datetime.strptime(
                    f"{day.strftime('%Y-%m-%d')} {hour}", "%Y-%m-%d %H:%M"
                )
                start_time = self.tz.localize(dt_naive)
                end_time = start_time + timedelta(hours=2)

                events_result = (
                    self.service.events()
                    .list(
                        calendarId=self.calendar_id,
                        timeMin=start_time.isoformat(),
                        timeMax=end_time.isoformat(),
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = events_result.get("items", [])
                for event in events:
                    event_start = event["start"].get(
                        "dateTime", event["start"].get("date")
                    )
                    event_end = event["end"].get("dateTime", event["end"].get("date"))
                    event_summary = event.get("summary", "No Title")
                    event_description = event.get("description", "No Description")
                    if user_id in event_description:
                        day_booked.append(hour)
                        has_booked = True
                    self.logger.info(
                        f"Event: {event_summary}, Start: {event_start}, End: {event_end}, Description: {event_description}"
                    )
                if len(events) < 2:
                    day_availables.append(hour)
            available_hours[day.strftime("%Y-%m-%d")] = day_availables
            booked_hours[day.strftime("%Y-%m-%d")] = day_booked
        self.logger.info(f"Available hours: {available_hours}")
        return available_hours, has_booked, booked_hours

    def query_upcoming_events_by_user(self, user_id, days=3):
        booked_hours = []
        tomorrow = datetime.now(self.tz) + timedelta(days=1)
        start_time = tomorrow.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        end_time = (
            (tomorrow + timedelta(days=(days - 1)))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .isoformat()
        )

        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                q=user_id,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        for event in events_result.get("items", []):
            event_start = event["start"].get("dateTime", event["start"].get("date"))
            event_end = event["end"].get("dateTime", event["end"].get("date"))
            event_summary = event.get("summary", "No Title")
            event_description = event.get("description", "No Description")
            booked_hours.append(event_start)
            # if user_id in event_description:
            #     self.logger.info(
            #         f"Event: {event_summary}, Start: {event_start}, End: {event_end}, Description: {event_description}"
            #     )
        return booked_hours


# Initialize the GoogleCalendarOperation class
# calendar_id = "your_calendar_id_here"  # Replace with your calendar ID
# subject_email = "your_subject_email_here"  # Replace with your subject email if needed
# google_calendar = GoogleCalendarOperation()
# google_calendar.get_upcoming_events()

# Test listing calendars
# print("Listing calendars:")
# calendars = google_calendar.list_calendars()
# for calendar in calendars:
#    print(f"Name: {calendar['summary']}, ID: {calendar['id']}")

# Test creating an event
# print("\nCreating an event:")

# created_event = google_calendar.create_event("Elvis Wang", "U1234567890", "2025-04-23", "14:00")
# print(f"Event created: {created_event.get('htmlLink')}")
