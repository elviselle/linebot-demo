from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
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

    response = requests.post(url, json=data)

    # 顯示 Rasa 回應內容
    for r in response.json():
        reply_msg = r.get("text")
        logger.info("Bot 說：" + reply_msg)

#    reply_msg = f'你說了：{incoming_msg}'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)

