import argparse
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

# 建議從環境變數讀取，這裡直接寫方便展示
LINE_CHANNEL_ACCESS_TOKEN = "你的 Channel access token"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 設置命令行參數
def get_user_input():
    parser = argparse.ArgumentParser(description="Send message to specific user")
    parser.add_argument("user_id", type=str, help="User ID of the target user")
    parser.add_argument("message", type=str, help="Message to send")
    return parser.parse_args()

def send_message_to_user(user_id, message):
    # 發送訊息
    line_bot_api.push_message(
        to=user_id,
        messages=TextSendMessage(text=message)
    )
    print(f"Message sent to user: {user_id}")

if __name__ == "__main__":
    # 從命令行獲取 user_id 和 message
    args = get_user_input()
    
    # 發送訊息
    send_message_to_user(args.user_id, args.message)

