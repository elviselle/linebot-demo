from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import requests
from bs4 import BeautifulSoup
import logging

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

    print(f"使用者 ID: {user_id}")
    print(f"使用者說: {user_message}")

    incoming_msg = event.message.text
    reply_msg = f'你說了：{incoming_msg}'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )

if __name__ == "__main__":
    # 要爬的網址
    url = "http://34.44.29.177:8080/"

    # 發送 GET 請求
    response = requests.get(url)

    # 如果成功
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string
        print("網頁標題是：", title)
        logger.info("網頁標題是："+title)
    else:
        print("無法取得網頁，狀態碼：", response.status_code)
        logger.info("無法取得網頁，狀態碼："+response.status_code)

    app.run(host='0.0.0.0', port=5000)

