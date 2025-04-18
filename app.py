from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FollowEvent, TextMessage, TextSendMessage, FlexSendMessage
import os
import requests
#from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 從環境變數讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
RASA_BOT_IP = os.getenv('RASA_BOT_IP')
flex_message_template="""{
  "type": "template",
  "altText": "this is a buttons template",
  "template": {
    "type": "buttons",
    "title": "Select the Reservation time",
    "text": "Last Order : PM 9:00",
    "actions": [
      {
        "type": "message",
        "label": "PM 6:00",
        "text": "PM 6:00"
      },
      {
        "type": "message",
        "label": "PM 7:00",
        "text": "PM 7:00"
      },
      {
        "type": "message",
        "label": "PM 8:00",
        "text": "PM 8:00"
      },
      {
        "type": "message",
        "label": "PM 9:00",
        "text": "PM 9:00"
      }
    ]
  }
}"""

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

    url = "http://"+RASA_BOT_IP+":5005/webhooks/rest/webhook"  # 根據你的 Rasa server 調整

    data = {
        "sender": "test_user",        # 自訂使用者 ID
        "message": incoming_msg             # 使用者發的訊息
    }

#    response = requests.post(url, json=data)

#    # 顯示 Rasa 回應內容
#    for r in response.json():
#        reply_msg = r.get("text")
#        logger.info("Bot 說：" + reply_msg)

    flex_msg = FlexSendMessage(
        alt_text='這是一個Flex訊息',
        contents=flex_message_json
    )

#    reply_msg = f'你說了：{incoming_msg}'
#    line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=reply_msg)
#    )

    line_bot_api.reply_message(flex_msg)

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

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)

