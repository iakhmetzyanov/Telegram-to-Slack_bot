# -*- coding: utf-8 -*-
import requests
import datetime
import sys
import json
import os

os.environ["PYTHONIOENCODING"]='utf-8'
mychatid=''
token=''
webhook_url='https://hooks.slack.com/services/'
slack_channel="#"
slack_username=""
slack_emoji=""

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset, 'allowed_updates': 'channel_post'}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None
        return last_update

nau_bot = BotHandler(token)
now = datetime.datetime.now()

def main():
    new_offset = None

    while True:

        nau_bot.get_updates(new_offset)
        last_update = nau_bot.get_last_update()

#print json to debug
        print(str(now) +' ' +json.dumps(last_update))
        if isinstance(last_update, list):
                last_update_id = last_update[-1]['update_id']
        elif last_update == None:
                continue
        else:


#private chat conversation jsons parse
         try:
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']
            last_chat_name = last_update['message']['chat']['first_name']
            nau_bot.send_message(last_chat_id, '{}, I am just a simple text transfer bot!'.format(last_chat_name))
         except:
            print('Its not a private message')

#channel chat conversation parse
         try:
            last_update_id = last_update['update_id']
            last_channel_text = last_update['channel_post']['text']
            last_chat_id = last_update['channel_post']['chat']['id']
            last_channel_name = last_update['channel_post']['chat']['username']

#send plaintext message to slack
            payload={'text': last_update['channel_post']['text'], 'channel': slack_channel, 'username': slack_username, "icon_emoji": slack_emoji}
            try:
                response = requests.post(
                    webhook_url, data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code != 200:
                    raise ValueError(
                        'Request to slack returned an error %s, the response is:\n%s'
                        % (response.status_code, response.text)
                    )
            except:
                print(str(now)+' '+'Sending data to slack fails')
         except:
            print('Its not a private message')

#manage offset, I assume there is only one offset
         new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
