from django.db.models import Max

from google.cloud import pubsub_v1, dialogflow
from background_task import background
from datetime import datetime
from random import randrange
import json
import requests
import time
import os

from users.models import User
from prints.models import PrintTask
from project.settings import FB_PAGE_ACCESS_TOKEN

STICKERS_LIBRARY = ['https://scontent.xx.fbcdn.net/v/t39.1997-6/p100x100/48653455_1881528101957318_5475416122180239360_n.png?_nc_cat=1&ccb=1-3&_nc_sid=ac3552&_nc_ohc=gkv__YCFaiYAX8b7ylz&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&tp=30&oh=959f1c20c52c78358f24070deb1967e5&oe=60ACE525',
                    'https://scontent.xx.fbcdn.net/v/t39.1997-6/p100x100/48538314_1881529725290489_4180406868809613312_n.png?_nc_cat=1&ccb=1-3&_nc_sid=ac3552&_nc_ohc=CbmuGmJIrEcAX_hwYok&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&tp=30&oh=d90cdcaa1bf42cc3e2b9fd69fe6fecb3&oe=60ABD165',
                    'https://scontent.xx.fbcdn.net/v/t39.1997-6/p100x100/69960455_2417677485144144_1149699544695439360_n.png?_nc_cat=1&ccb=1-3&_nc_sid=ac3552&_nc_ohc=cToB3EQi1CUAX-_6Mhq&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&tp=30&oh=cda64c9a0da8caf9c870d2553a13723b&oe=60AB2185']


def detect_intent_text(session_id, text, project_id='cloud-comp-final-project', language_code='th'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text


def send_message_to_facebook(facebook_id, message, sticker=False):
    endpoint = 'https://graph.facebook.com/v10.0/me/messages?access_token=' + FB_PAGE_ACCESS_TOKEN
    if sticker:
        payload = {
            'messaging_type': 'RESPONSE',
            'recipient': {
                'id': facebook_id
            },
            'message': {
                'attachment': {
                    'type': 'image',
                    'payload': {
                        'url': message
                    }
                }
            }
        }
    else:
        payload = {
            'messaging_type': 'RESPONSE',
            'recipient': {
                'id': facebook_id
            },
            'message': {
                'text': message
            }
        }
    max_try = 5
    while True:
        max_try += 1
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            break
        if max_try == 5:
            break
        time.sleep(5)
    return


def update_user_current_state(user_id, new_state):
    user_dict = User.objects.filter(pk=user_id).values()[0]
    user_dict['current_state'] = new_state
    print(user_dict)
    new_obj = User(**user_dict)
    new_obj.save()  
    return


def process_message(message):
    data = json.loads(message.data.decode())
    message.ack()

    sender_id = data['sender']['id']
    try:
        user_obj = User.objects.get(facebook_id=sender_id)
    except User.DoesNotExist:
        # NON REGIS CASE
        text = data['message'].get('text', None)
        if not text:
            print('Invalid message')
            send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
            return
        print(f'User not found in the system [{sender_id}] says: {text}')

        intent = detect_intent_text(sender_id, text)
        result_type, result_text = intent[1], intent[4:]

        if result_type in ['r', 'w']:
            send_message_to_facebook(sender_id, result_text)
            return

        if result_type == 'p':
            send_message_to_facebook(sender_id, 'กรุณาลงทะเบียนก่อนเริ่มใช้งานค่ะ')
            return

        if result_type == 'e':
            try:
                user_input_id = int(text)
            except ValueError:
                send_message_to_facebook(sender_id, 'รหัสพนักงานไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
                return
            try:
                query_user = User.objects.get(employee_id=user_input_id)
            except User.DoesNotExist:
                send_message_to_facebook(sender_id, 'ไม่พบข้อมูลพนักงาน กรุณาลองใหม่อีกครั้งค่ะ')
                return
            if query_user.facebook_id:
                send_message_to_facebook(sender_id, 'ผู้ใช้นี้ถูกใช้งานไปแล้วหรือไม่ถูกต้อง กรุณาแอดมินค่ะ')
                return
        
            send_message_to_facebook(sender_id, f'ยินดีต้อนรับคุณ {query_user.first_name} {query_user.last_name} สามารถสั่งพิมพ์งานได้เลยค่ะ')
            query_user.current_state = 'IDLE'
            query_user.facebook_id = sender_id
            query_user.save()
            return

        send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')            
        return

    sender_name = f'{user_obj.first_name} {user_obj.last_name}'
    attachments = data['message'].get('attachments', None)
    if attachments:
        for attachment in attachments:
            if 'sticker_id' in attachment['payload']:
                print(f'{sender_name} sent a sticker [{attachment}]')
                send_message_to_facebook(sender_id, STICKERS_LIBRARY[randrange(0, 3)], sticker=True)
                continue

            file_url = attachment['payload']['url']
            
            if attachment['type'] == 'image':
                print(f'{sender_name} sent a photo [{file_url}]')
                if user_obj.current_state != 'PROMPT_PRINT':
                    print(f'Current state is not ready to print [{user_obj.current_state}]')
                    send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
                    continue
                file_download_response = requests.get(file_url)
                ext = file_download_response.headers['content-type'].split('/')[-1]
                filename = f'temp_files/{time.time()}.{ext}'
                with open(filename, 'wb') as f:
                    for chunk in file_download_response.iter_content(1024):
                        f.write(chunk)
                files = {
                    'document': (f'user_{user_obj.user_id}/{filename}', open(filename, 'rb')),
                    'owner': (None, user_obj.user_id)
                }
                response = requests.post('http://localhost:8000/api/tasks/', files=files).json()
                os.remove(filename)
                send_message_to_facebook(sender_id, 'ระบบได้รับภาพเรียบร้อยแล้ว กรุณารอสักครู่นะคะ')

                continue

            if attachment['type'] == 'file':
                print(f'{sender_name} sent a file [{file_url}]')
                if user_obj.current_state != 'PROMPT_PRINT':
                    print(f'Current state is not ready to print [{user_obj.current_state}]')
                    send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
                    continue
                file_download_response = requests.get(file_url)
                ext = file_download_response.headers['content-type'].split('/')[-1]
                ext = 'docx' if ext == 'vnd.openxmlformats-officedocument.wordprocessingml.document' else ext
                filename = f'temp_files/{time.time()}.{ext}'
                with open(filename, 'wb') as f:
                    for chunk in file_download_response.iter_content(1024):
                        f.write(chunk)
                files = {
                    'document': (f'user_{user_obj.user_id}/{filename}', open(filename, 'rb')),
                    'owner': (None, user_obj.user_id)
                }
                response = requests.post('http://localhost:8000/api/tasks/', files=files).json()
                os.remove(filename)
                send_message_to_facebook(sender_id, 'ระบบได้รับไฟล์เรียบร้อยแล้ว กรุณารอสักครู่นะคะ')

                continue

            print(f'{sender_name} sent an invalid attachment')
            continue
        return

    text = data['message'].get('text', None)
    if not text:
        print('Invalid message')
        send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
        return
    print(f'{sender_name} says: {text}')

    if user_obj.current_state == 'PROMPT_REGIS':
        try:
            user_input_id = int(text)
        except ValueError:
            send_message_to_facebook(sender_id, 'รหัสพนักงานไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
            return
        try:
            query_user = User.objects.get(employee_id=user_input_id)
        except User.DoesNotExist:
            send_message_to_facebook(sender_id, 'ไม่พบข้อมูลพนักงาน กรุณาลองใหม่อีกครั้งค่ะ')
            return
        if query_user.facebook_id:
            query_user.current_state = 'NON_REGIS'
            query_user.save()
            send_message_to_facebook(sender_id, 'ผู้ใช้นี้ถูกใช้งานไปแล้วหรือไม่ถูกต้อง กรุณาแอดมินค่ะ')
            return
        
        query_user.current_state = 'IDLE'
        query_user.facebook_id = sender_id
        query_user.save()
        send_message_to_facebook(sender_id, 'ยินดีต้อนรับ สามารถสั่งพิมพ์งานได้เลยค่ะ')
        return
        


    intent = detect_intent_text(sender_id, text)
    result_type, result_text = intent[1], intent[4:]

    if result_type == 'v' and user_obj.current_state in ['IDLE', 'QUEUEING', 'PRINTING']:
        text_printstate_map = {'Queuing': 'ไฟล์ของคุณอยู่ในคิวพิมพ์ค่ะ', 'Printing': 'ไฟล์ของคุณกำลังพิมพ์อยู่ค่ะ', 'Done': 'ไม่มีงานพิมพ์ที่ค้างอยู่ค่ะ'}
        latest_printtask_obj = PrintTask.objects.filter(owner_id=user_obj.user_id).order_by('-task_id')[0]
        send_message_to_facebook(sender_id, text_printstate_map[latest_printtask_obj.get_status_display()])
        return

    if result_type == 'p' and user_obj.current_state == 'IDLE':
        update_user_current_state(user_obj.user_id, 'PROMPT_PRINT')
        send_message_to_facebook(sender_id, result_text)
        return

    if result_type in ['w', 'e']:
        send_message_to_facebook(sender_id, result_text)
        return

    send_message_to_facebook(sender_id, 'คำสั่งไม่ถูกต้อง กรุณาลองใหม่อีกครั้งค่ะ')
    return


def process_status_update(message):
    data = json.loads(message.data.decode())
    message.ack()
    print_obj = PrintTask.objects.filter(pk=data['print_id']).values()[0]
    if data['status'] == 'success':
        print_obj['status'] = 3
        new_obj = PrintTask(**print_obj)
        new_obj.save()
        # SEND MESSAGE BACK SUCCESS
        user_obj = User.objects.get(user_id=new_obj.owner_id)
        send_message_to_facebook(user_obj.facebook_id, 'งานพิมพ์ของคุณเสร็จเรียบร้อยแล้วค่ะ')
        update_user_current_state(user_obj.user_id, 'IDLE')
        return


def get_messages():
    subscription_name = 'projects/cloud-comp-final-project/subscriptions/django-backend-pull'
    with pubsub_v1.SubscriberClient() as subscriber:
        future = subscriber.subscribe(subscription_name, process_message)
        future.result()


def get_update_status_from_printer():
    subscription_name = 'projects/cloud-comp-final-project/subscriptions/paas-post-printing-sub'
    with pubsub_v1.SubscriberClient() as subscriber:
        future = subscriber.subscribe(subscription_name, process_status_update)
        future.result()