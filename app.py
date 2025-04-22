import os
import requests
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FollowEvent, PostbackEvent, TextMessage, TextSendMessage, FlexSendMessage, TemplateSendMessage
from LineBotMessageTemplate import LineBotMessageTemplate
from GoogleCalendarHelper import GoogleCalendarOperation

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 從環境變數讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')



line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

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
      line_bot_api.reply_message(event.reply_token, TextSendMessage(text="需要取消預約嗎？請打電話📞 02-33445566，我們會有專人幫您處理唷😊"))
      return

    elif "預約" in incoming_msg:
      
      google_calendar = GoogleCalendarOperation()
      google_calendar.get_upcoming_events()

      btn_msg = FlexSendMessage(
          alt_text="預約時段選擇",
          contents=LineBotMessageTemplate().get_message_template(LineBotMessageTemplate.TYPE_CALENDAR_AVAILABLE_TIME)
      )
      # logger.info(f"FlexSendMessage: {btn_msg.as_json_dict()}")

      line_bot_api.reply_message(event.reply_token, btn_msg)

# 處理 follow 事件
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name
    picture = profile.picture_url

    logger.info(f"新朋友加入！user_id: {user_id}, 名字: {name}")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{name}，歡迎你加我好友 👋")
    )

@handler.add(PostbackEvent)
def handle_postback(event):
  user_id = event.source.user_id
  profile = line_bot_api.get_profile(user_id)
  display_name = profile.display_name

  postback_data = event.postback.data
  logger.info(f'接收到 postback: {postback_data}')

  if postback_data.startswith('action=book'):
    parts = dict(item.split('=') for item in postback_data.split('&'))  
    google_calendar = GoogleCalendarOperation()
    google_calendar.create_event(display_name, user_id, '2025-'+parts['date'], parts['time']) 

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

    app.run(host='0.0.0.0', port=5000)

