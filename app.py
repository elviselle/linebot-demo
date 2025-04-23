import os
from datetime import datetime
import logging
from flask import Flask, request, abort
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

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 從環境變數讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


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

        google_calendar = GoogleCalendarOperation()
        availables_hours, has_booked, booked_hours = (
            google_calendar.get_upcoming_events()
        )

        if has_booked:
            booked_hours_str = ""
            for booked_hour in booked_hours.keys():
                booked_hours_str += f"{booked_hour}：{', '.join(booked_hour + " " + booked_hours[booked_hour])}\n"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"你已經預約過了，預約時間為：{booked_hours_str}，若您想更改預約時間，請來電02-33445566有專人為您改期唷！"
                ),
            )
            return

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
            for hour in hours:
                box = LineBotMessageTemplate().get_message_template(
                    LineBotMessageTemplate.TYPE_BOX
                )
                box["contents"][0]["action"]["label"] = hour
                box["contents"][0]["action"][
                    "data"
                ] = f"action=book&date={available_hour}&time={hour}"
                box["contents"][0]["action"][
                    "data"
                ] = f"action=book&date={available_hour}&time={hour}"
                box["contents"][0]["action"]["displayText"] = f"我要預約 {mm_dd} {hour}"
                box["contents"][0]["contents"][0]["text"] = hour

                bubble["body"]["contents"][2]["contents"].append(box)

            carousel["contents"].append(bubble)

        flex_msg = FlexSendMessage(alt_text="預約時段選擇", contents=carousel)
        logger.info(f"FlexSendMessage: {flex_msg.as_json_dict()}")

        line_bot_api.reply_message(event.reply_token, flex_msg)


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
        google_calendar = GoogleCalendarOperation()
        google_calendar.create_event(
            display_name, user_id, parts["date"], parts["time"]
        )

        # 可以根據 data 做不同邏輯


#    if postback_data == 'book_haircut':
#        line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text="你選擇了預約剪髮 💇‍♂️")
#        )
#    elif postback_data == 'check_service':
#        line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text="以下是我們的服務項目 💈")
#        )

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
