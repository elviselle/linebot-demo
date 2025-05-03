import os
from datetime import datetime
import logging
from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    TemplateSendMessage,
)
from LineBotMessageTemplate import LineBotMessageTemplate
from GoogleCalendarHelper import GoogleCalendarOperation
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app_config = None
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 從環境變數讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
HOME_URL = os.getenv("HOME_URL")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

staffs = []
time_sheets = []
booking_day_range = 3

google_calendar = None


import requests

def cronjob():
    # 發送 GET 請求
    try:
        response = requests.get(HOME_URL)
        logger.info(f"成功請求 {url}，狀態碼：{response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"請求出錯：{e}")


# 把 / 導到 static/home.html
@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'home.html')

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    logger.info(f"使用者 ID: {user_id}")
    logger.info(f"使用者說: {user_message}")

    incoming_msg = event.message.text

    # 以後可以改發送請求到 Rasa server

    if "營業時間" in incoming_msg:
        return

    elif "取消" in incoming_msg:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="需要取消預約嗎？請打電話📞 02-33445566，我們會有專人幫您處理唷😊"
            ),
        )
        return

    elif "預約" in incoming_msg:

        bookded_events = google_calendar.query_upcoming_events_by_user(user_id)
        if len(bookded_events) > 0:
            booked_hours_str = ""
            for booked_event in bookded_events:
                booked_hours_str += (
                    f"{datetime.fromisoformat(booked_event).strftime('%m-%d %H:%M')}、"
                )

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"你已經預約過了，預約時間為：{booked_hours_str} 若您想更改預約時間，請來電02-33445566有專人為您改期唷！"
                ),
            )
            return

        availables_hours, has_booked, booked_hours = (
            google_calendar.get_upcoming_events(user_id)
        )
        carousel = LineBotMessageTemplate().get_message_template(
            LineBotMessageTemplate.TYPE_CALENDAR_AVAILABLE_TIME
        )

        # 2. 判斷星期幾（回傳中文）
        weekday_map = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]

        for available_hour in availables_hours.keys():
            mm_dd = datetime.strptime(available_hour, "%Y-%m-%d").strftime("%m/%d")
            weekday = weekday_map[
                datetime.strptime(available_hour, "%Y-%m-%d").weekday()
            ]

            bubble = LineBotMessageTemplate().get_message_template(
                LineBotMessageTemplate.TYPE_BUBBLE
            )
            bubble["hero"]["url"] = bubble["hero"]["url"].replace(
                "WEBHOOD_DOMAIN", os.getenv("WEBHOOD_DOMAIN")
            )
            bubble["body"]["contents"][0]["text"] = f"預約 {mm_dd} {weekday}"
            hours = availables_hours[available_hour]
            nowstr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for hour in hours:
                box = LineBotMessageTemplate().get_message_template(
                    LineBotMessageTemplate.TYPE_BOX
                )
                box["contents"][0]["action"]["label"] = hour
                box["contents"][0]["action"][
                    "data"
                ] = f"action=book&date={available_hour}&time={hour}&issue_time={nowstr}"
                # box["contents"][0]["action"]["displayText"] = f"我要預約 {mm_dd} {hour}"
                box["contents"][0]["contents"][0]["text"] = hour

                bubble["body"]["contents"][2]["contents"].append(box)

            carousel["contents"].append(bubble)

        flex_msg = FlexSendMessage(alt_text="預約時段選擇", contents=carousel)
        # logger.info(f"FlexSendMessage: {flex_msg.as_json_dict()}")

        line_bot_api.reply_message(event.reply_token, flex_msg)

    elif "排休:" in incoming_msg:
        parts = [item for item in incoming_msg.split(":")]
        staff = parts[1].strip()
        dueoffs = google_calendar.query_offdue_staff_this2month(staff)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=staff
                + "的排休時間為：\n"
                + ", ".join([dueoff for dueoff in dueoffs])
            ),
        )


# 處理 follow 事件
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name
    picture = profile.picture_url

    logger.info(f"新朋友加入！user_id: {user_id}, 名字: {name}")

    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=f"{name}，歡迎你加我好友 👋")
    )


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name

    postback_data = event.postback.data
    logger.info(f"接收到 postback: {postback_data}")

    if postback_data.startswith("action=book"):
        parts = dict(item.split("=") for item in postback_data.split("&"))

        # check issue_time < 5分鐘
        issue_time = datetime.strptime(parts["issue_time"], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - issue_time).total_seconds() > 300:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="按鈕效期已過，請重新點選單的「我要預約」"),
            )
            return

        nowstr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        confirm_dict = confirm_dict = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "你確定要預約"
                        + parts["date"]
                        + " "
                        + parts["time"]
                        + " 嗎？",
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "postback",
                                    "label": "是",
                                    "data": "action=confirm&date="
                                    + parts["date"]
                                    + "&time="
                                    + parts["time"]
                                    + "&issue_time="
                                    + nowstr,
                                    "displayText": "是",
                                },
                                "style": "primary",
                                "color": "#FFAA88",
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "否",
                                    "text": "否",
                                },
                                "style": "secondary",
                            },
                        ],
                    },
                ],
            },
        }

        flex_msg = FlexSendMessage(
            alt_text="確認預約",
            contents=confirm_dict,
        )
        # logger.info(f"FlexSendMessage: {flex_msg.as_json_dict()}")
        line_bot_api.reply_message(event.reply_token, flex_msg)

        # google_calendar = GoogleCalendarOperation()
        # google_calendar.create_event(
        #     display_name, user_id, parts["date"], parts["time"]
        # )

        # 可以根據 data 做不同邏輯

    elif postback_data.startswith("action=confirm"):
        parts = dict(item.split("=") for item in postback_data.split("&"))

        # check issue_time < 5分鐘
        issue_time = datetime.strptime(parts["issue_time"], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - issue_time).total_seconds() > 300:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="按鈕效期已過，請重新點選單的「我要預約」"),
            )
            return

        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=f"後台預約中..."),
        )
        google_calendar = GoogleCalendarOperation()
        created_event = google_calendar.create_event(
            display_name, user_id, parts["date"], parts["time"]
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"預約成功！您預約的時段為 {datetime.strptime(parts['date'], '%Y-%m-%d').strftime('%m/%d')} {parts['time']}，期待為您服務！若您要取消或改期，請來電02-33445566，我們會有專人為您處理唷😊"
            ),
        )

# 初始化非阻塞的背景調度器
scheduler = BackgroundScheduler()

# 設定一個每 1 分鐘執行的任務
scheduler.add_job(cronjob, 'interval', minutes=10)

# 啟動調度器
scheduler.start()


if __name__ == "__main__":
    google_calendar = GoogleCalendarOperation()
    app_config = google_calendar.get_config_event()

    staffs = app_config["staffs"]
    time_sheets = app_config["timesheets"]
    booking_day_range = app_config["bookingdayrange"]

    logger.info(f"staffs: {staffs}")
    logger.info(f"time_sheets: {time_sheets}")
    logger.info(f"booking_day_range: {booking_day_range}")

    google_calendar = GoogleCalendarOperation(time_sheets)

    app.run(host="0.0.0.0", port=5000)
