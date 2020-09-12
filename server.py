# -*- coding: utf-8 -*-

# ./ngrok http -host-header "localhost:5000" 5000

from __future__ import unicode_literals

import os
import sys
import json
from datetime import datetime
from NewsCheck import NewsCheck
from NewsCrawler import NewsCrawler

from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

class Config(object):
    JOBS=[
        {
            'id':'job',
            'func':'__main__:schedule',
            'trigger':'cron',
            'minute':30
        }
    ]
def schedule():
    crawler = NewsCrawler()
    crawler.execute()
    time_report(False)
    public_opinion(False)

app = Flask(__name__)
app.config.from_object(Config())
nc = NewsCheck()

# get channel_secret and channel_access_token from your environment variable
channel_secret = 'cc8c2c127d323d07a40a475fc1d675cf'
channel_access_token = '2ldtOWb0RABlahQDXWRHCjU3yuRMEVW4AQBT45foU1ckuifHUWaK5BCOYmOu3PDgEetZ9qeP+6UhbyL1eMeVc/AXglPK3SNCn6QGv+X2OExvbtSOeTh0FNkE1Er7065aCoqBrZJf/TshX7JtRTmLlgdB04t89/1O/w1cDnyilFU='


line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


def time_report(isreply, request=None):
    now = datetime.now().strftime("%b %d %Y %H:%M:%S")
    message = '現在時間：' + now + '\n'

    warnings, warn_links = nc.check_keyword()
    for warn in warnings:
        message = message + warn + '\n' + warn_links[warnings.index(warn)] + '\n'
    if len(warnings) == 0:
        message += '\n抱歉～這段時間我們沒有收到任何緊急的新聞'

    if isreply:
        reply(request, message)
    else:
        push('text', message)


def public_opinion(isreply, request=None):
    counts = nc.check_emotion()
    message = '這段時間我們蒐集到了：\n正面新聞 ' + str(counts['pos']) + ' 篇\n負面新聞 ' + str(counts['neg']) + ' 篇'
    if isreply:
        reply(request, message)
    else:
        push('text', message)
    # push('image')


def new_word(request, new):
    result = nc.new_word(new)
    if result == 'Duplicate':
        reply(request, '關鍵字已存在！')
    else:
        reply(request, '關鍵字新增成功！')


def reply(request, message):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message)
            )

def push(type, message=None):
    users = read_user()
    for user in users:
        if type == 'text':
            line_bot_api.push_message(user, TextSendMessage(text=message))
        elif type == 'image':
            line_bot_api.push_message(user, ImageSendMessage(
                                            original_content_url='https://ibb.co/tmQFrYc',
                                            preview_image_url='https://ibb.co/tmQFrYc'
                                        ))


def collect_user(new_user):
    user_path = os.path.join('data', 'user.json')
    with open(user_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
    if new_user not in users:
        users.append(new_user)
    with open(user_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False)


def read_user():
    user_path = os.path.join('data', 'user.json')
    with open(user_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
    return users


@app.route("/callback", methods=['POST'])
def callback():
    # get request body as text
    body = request.get_data(as_text=True)
    message = json.loads(body)
    user = message['events'][0]['source']['userId']
    collect_user(user)
    message = message['events'][0]['message']['text']
    if message == '報時':
        time_report(True, request)
    elif message == '輿情':
        public_opinion(True, request)
    elif '關鍵字 ' in message:
        new = message.split(' ')[1]
        new_word(request, new)
    else:
        reply(request, '沒有這個指令喔～')
    return 'OK'


@app.route("/test")
def test():
    return 'test ok~~~'


if __name__ == "__main__":
    scheduler=APScheduler()  # 例項化APScheduler
    scheduler.init_app(app)  # 把任務列表放進flask
    scheduler.start() # 啟動任務列表

    app.debug = True
    app.run()


