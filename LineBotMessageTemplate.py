class LineBotMessageTemplate:

    TYPE_CALENDAR_AVAILABLE_TIME: str = "calendar_available"

    def __init__(self):
        pass
    def get_message_template(self, message_type):
        msg_dict = {}
        
        if message_type == self.TYPE_CALENDAR_AVAILABLE_TIME:

            btn_message_template = """
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
                        "backgroundColor": "#FFEAE0"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "lg",
                        "contents": [
                        {
                            "type": "text",
                            "text": "預約 - 明天",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FF6F61"
                        },
                        {
                            "type": "text",
                            "text": "4/23 (星期三)",
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
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#FFAA88",
                                "cornerRadius": "md",
                                "action": {
                                "type": "postback",
                                "label": "13:00",
                                "data": "action=book&date=04-23&time=13:00",
                                "displayText": "我要預約 4/23 13:00"
                                },
                                "paddingAll": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "13:00",
                                    "align": "center",
                                    "weight": "bold",
                                    "size": "lg",
                                    "color": "#ffffff"
                                }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#FFAA88",
                                "cornerRadius": "md",
                                "action": {
                                "type": "postback",
                                "label": "15:00",
                                "data": "action=book&date=04-23&time=15:00",
                                "displayText": "我要預約 4/23 15:00"
                                },
                                "paddingAll": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "15:00",
                                    "align": "center",
                                    "weight": "bold",
                                    "size": "lg",
                                    "color": "#ffffff"
                                }
                                ]
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
                        "backgroundColor": "#FFEAE0"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "lg",
                        "contents": [
                        {
                            "type": "text",
                            "text": "預約 - 後天",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FF6F61"
                        },
                        {
                            "type": "text",
                            "text": "4/24 (星期四)",
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
                                "data": "action=book&date=04-24&time=10:30",
                                "displayText": "我要預約 4/24 10:30"
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
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#FFAA88",
                                "cornerRadius": "md",
                                "action": {
                                "type": "postback",
                                "label": "15:00",
                                "data": "action=book&date=04-24&time=15:00",
                                "displayText": "我要預約 4/24 15:00"
                                },
                                "paddingAll": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "15:00",
                                    "align": "center",
                                    "weight": "bold",
                                    "size": "lg",
                                    "color": "#ffffff"
                                }
                                ]
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
                            "text": "預約 - 大後天",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FF6F61"
                        },
                        {
                            "type": "text",
                            "text": "4/25 (星期五)",
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
                                "label": "15:00",
                                "data": "action=book&date=04-25&time=15:00",
                                "displayText": "我要預約 4/25 15:00"
                                },
                                "paddingAll": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "15:00",
                                    "align": "center",
                                    "weight": "bold",
                                    "size": "lg",
                                    "color": "#ffffff"
                                }
                                ]
                            }
                            ]
                        }
                        ]
                    }
                    }
                ]
                }
                """
            msg_dict = json.loads(btn_message_template)    

        return msg_dict