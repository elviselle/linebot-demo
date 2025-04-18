from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FollowEvent, PostbackEvent, TextMessage, TextSendMessage, FlexSendMessage, TemplateSendMessage
import os
import requests
#from bs4 import BeautifulSoup
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 從環境變數讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
RASA_BOT_IP = os.getenv('RASA_BOT_IP')
btn_message_template="""
{
  "type": "carousel",
  "contents": [
    {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "https://vos.line-scdn.net/bot-designer-template-images/event/brown-card.png",
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "backgroundColor": "#E3E3E3"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
          {
            "type": "text",
            "text": "預約 - 明天",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "text",
            "text": "4/23 (星期三)",
            "size": "md",
            "wrap": true
          },
          {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "10:30",
                  "data": "action=book&date=04-23&time=10:30",
                  "displayText": "我要預約 4/23 10:30"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "13:00",
                  "data": "action=book&date=04-23&time=13:00",
                  "displayText": "我要預約 4/23 13:00"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "15:00",
                  "data": "action=book&date=04-23&time=15:00",
                  "displayText": "我要預約 4/23 15:00"
                },
                "style": "primary",
                "height": "md"
              }
            ]
          }
        ]
      }
    },
    {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "https://vos.line-scdn.net/bot-designer-template-images/event/cony-card.png",
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "backgroundColor": "#E3E3E3"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
          {
            "type": "text",
            "text": "預約 - 後天",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "text",
            "text": "4/24 (星期四)",
            "size": "md",
            "wrap": true
          },
          {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "10:30",
                  "data": "action=book&date=04-24&time=10:30",
                  "displayText": "我要預約 4/24 10:30"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "13:00",
                  "data": "action=book&date=04-24&time=13:00",
                  "displayText": "我要預約 4/24 13:00"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "15:00",
                  "data": "action=book&date=04-24&time=15:00",
                  "displayText": "我要預約 4/24 15:00"
                },
                "style": "primary",
                "height": "md"
              }
            ]
          }
        ]
      }
    },
    {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "https://vos.line-scdn.net/bot-designer-template-images/event/sally-card.png",
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
          {
            "type": "text",
            "text": "預約 - 大後天",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "text",
            "text": "4/25 (星期五)",
            "size": "md",
            "wrap": true
          },
          {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "10:30",
                  "data": "action=book&date=04-25&time=10:30",
                  "displayText": "我要預約 4/25 10:30"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "13:00",
                  "data": "action=book&date=04-25&time=13:00",
                  "displayText": "我要預約 4/25 13:00"
                },
                "style": "primary",
                "height": "md"
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "15:00",
                  "data": "action=book&date=04-25&time=15:00",
                  "displayText": "我要預約 4/25 15:00"
                },
                "style": "primary",
                "height": "md"
              }
            ]
          }
        ]
      }
    }
  ]
}
"""
btn_msg_dict = json.loads(btn_message_template)

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

#    btn_msg = TemplateSendMessage.new_from_json_dict(btn_msg_dict)
    btn_msg = FlexSendMessage(
        alt_text="預約時段選擇",
        contents=btn_msg_dict)

#    reply_msg = f'你說了：{incoming_msg}'
#    line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=reply_msg)
#    )

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
    postback_data = event.postback.data
    logger.info(f'接收到 postback: {postback_data}')

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

