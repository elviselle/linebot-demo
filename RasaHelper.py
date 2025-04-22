import os
import requests
from flask import Flask, request, abort
import logging

class RasaHelper:
    # Initialize logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    RASA_BOT_IP = os.getenv('RASA_BOT_IP')

    # Define the Rasa server URL
    RASA_SERVER_URL =  "http://"+RASA_BOT_IP+":5005/webhooks/rest/webhook"  # 根據你的 Rasa server 調整


    def __init__(self):
        """
        Initialize the RasaHelper class.
        """
        pass

    def send_message(self, message):
        """
        Send a message to the Rasa server.

        Args:
            message (str): The message to send.
        """

        # Placeholder for sending a message to the Rasa server
        logger.info(f"Sending message to Rasa: {message}")

        data = {
            "sender": "linebot",           # 送到Rasa端的使用者ID
            "message": message             # 送給Rasa的訊息
        }

        response = requests.post(url, json=data)

        response_str = ""
        # 顯示 Rasa 回應內容
        for r in response.json():
            reply_msg = r.get("text")
            logger.info("Rasa Bot 回傳：" + reply_msg)
            response_str += reply_msg + "\n"
        
        return response_str


