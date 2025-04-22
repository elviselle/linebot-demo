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

    def old_testing_code(self):
        # 這裡是舊的測試代碼，保留以供參考
        # 你可以在這裡添加一些測試代碼來驗證功能
        
        # 建立授權
        #SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = './google-service-account-key/bot-reservation-calandcar-d4b08b7cf015.json'
        CALENDAR_ID = "33c461e46a5dc03899db2fcc80feb217380a5671d30fa5bc6290deb1481e6719@group.calendar.google.com"

        SERVICE_ACCONT_KEY = os.getenv('SERVICE_ACCOUNT_KEY')
        SERVICE_ACCONT_KEY += "=="
        decoded_bytes = base64.b64decode(SERVICE_ACCONT_KEY.encode("utf-8"))
        decoded_text = decoded_bytes.decode("utf-8")

        keyfile_dict = json.loads(decoded_text)

        print("還原後：", decoded_text)

        credentials = service_account.Credentials.from_service_account_info(
            keyfile_dict, scopes=SCOPES)

        # 指定代理哪個使用者（要先分享行事曆給這個 service account）
        delegated_credentials = credentials.with_subject('bot-service-account@bot-reservation-calandcar.iam.gserviceaccount.com')

        # 建立 calendar API client
        # service = build('calendar', 'v3', credentials=delegated_credentials)
        service = build('calendar', 'v3', credentials=credentials)

        calendar_entry = {
            'id': CALENDAR_ID
        }


        #service.calendarList().insert(body=calendar_entry).execute()
        #print("✅ 已加入該行事曆到 service account 的清單")


        # 呼叫 CalendarList.list 取得所有行事曆
        calendar_list = service.calendarList().list().execute()
        #print(calendar_list)

        # 印出行事曆名稱與 ID
        for calendar_entry in calendar_list['items']:
            print(f"Name: {calendar_entry['summary']}")
            print(f"Description: {calendar_entry['description']}")
            print(f"ID: {calendar_entry['id']}")
            print('---')


        event = {
            'summary': '👩‍🎤 美容預約 - Alice',
            'location': '台中市西屯區某路',
            'description': 'VIP顧客指定設計師Kiki',
            'start': {
                'dateTime': '2025-04-22T14:00:00+08:00',
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': '2025-04-22T15:00:00+08:00',
                'timeZone': 'Asia/Taipei',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # === 5. 建立事件 ===
        # created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        # print(f"✅ 已建立事件：{created_event.get('htmlLink')}")


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