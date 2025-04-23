import json
import os
import logging


class LineBotMessageTemplate:

    TYPE_CALENDAR_AVAILABLE_TIME: str = "calendar_available"
    TYPE_BUBBLE: str = "calendar_bubble"
    TYPE_BOX: str = "calendar_box"
    WEBHOOD_DOMAIN = os.getenv("WEBHOOD_DOMAIN")

    # Initialize logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def get_message_template(self, message_type):
        msg_dict = {}

        # logging.info(f"webhook domain: {self.WEBHOOD_DOMAIN}")

        if message_type == self.TYPE_CALENDAR_AVAILABLE_TIME:
            msg_dict = {"type": "carousel", "contents": []}
        elif message_type == self.TYPE_BUBBLE:
            bubble = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "WEBHOOD_DOMAIN/static/imgs/LJ_Salon_Banner.png",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "backgroundColor": "#FFEAE0",
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "lg",
                    "contents": [
                        {
                            "type": "text",
                            "text": "預約 - 明天(4/23 星期三)",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FF6F61",
                        },
                        {
                            "type": "text",
                            "text": "可預約時段：",
                            "size": "md",
                            "color": "#666666",
                            "wrap": "true",
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [],
                        },
                    ],
                },
            }
            msg_dict = bubble
        elif message_type == self.TYPE_BOX:
            box = {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#FFAA88",
                        "cornerRadius": "md",
                        "action": {
                            "type": "postback",
                            "label": "10:30",
                            "data": "action=book&date=2025-04-23&time=10:30",
                            "displayText": "我要預約 4/23 10:30",
                        },
                        "paddingAll": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "10:30",
                                "align": "center",
                                "weight": "bold",
                                "size": "lg",
                                "color": "#ffffff",
                            }
                        ],
                    }
                ],
            }
            msg_dict = box
        return msg_dict


"""bubble =
{
    "type": "bubble",
    "hero": {
        "type": "image",
        "url": "WEBHOOD_DOMAIN/static/imgs/LJ_Salon_Banner.png",
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "backgroundColor": "#FFEAE0"
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "lg",
        "contents": [
            {
                "type": "text",
                "text": "預約 - 明天(4/23 星期三)",
                "weight": "bold",
                "size": "xl",
                "color": "#FF6F61"
            },
            {
                "type": "text",
                "text": "可預約時段：",
                "size": "md",
                "color": "#666666",
                "wrap": true
            },
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFAA88",
                    "cornerRadius": "md",
                    "action": {
                    "type": "postback",
                    "label": "10:30",
                    "data": "action=book&date=04-23&time=10:30",
                    "displayText": "我要預約 4/23 10:30"
                    },
                    "paddingAll": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "10:30",
                        "align": "center",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#ffffff"
                    }
                    ]
                }
            }
        ]
    }
}"""

"""box = {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
        {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFAA88",
            "cornerRadius": "md",
            "action": {
            "type": "postback",
            "label": "10:30",
            "data": "action=book&date=2025-04-23&time=10:30",
            "displayText": "我要預約 4/23 10:30"
            },
            "paddingAll": "md",
            "contents": [
            {
                "type": "text",
                "text": "10:30",
                "align": "center",
                "weight": "bold",
                "size": "lg",
                "color": "#ffffff"
            }
            ]
        }
    ]
}"""
