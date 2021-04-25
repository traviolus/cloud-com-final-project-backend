from google.cloud import pubsub_v1, dialogflow
from background_task import background
from datetime import datetime
import json
import requests
import time
import os

from users.models import User
from prints.models import PrintTask


def detect_intent_text(session_id, text, project_id='cloud-comp-final-project', language_code='th'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text


def process_message(message):
    data = json.loads(message.data.decode())
    message.ack()

    sender_id = data['sender']['id']
    try:
        user_obj = User.objects.get(facebook_id=sender_id)
    except User.DoesNotExist:
        print(f'User not found in the system [{sender_id}]')
        return

    sender_name = f'{user_obj.first_name} {user_obj.last_name}'
    attachments = data['message'].get('attachments', None)
    if attachments:
        for attachment in attachments:
            # CHECK IF USER IS CORRECT STATE
            if 'sticker_id' in attachment['payload']:
                print(f'{sender_name} sent a sticker')
                return
            file_url = attachment['payload']['url']
            if attachment['type'] == 'image':    
                print(f'{sender_name} sent a photo [{file_url}]')
                file_download_response = requests.get(file_url)
                ext = file_download_response.headers['content-type'].split('/')[-1]
                filename = f'temp_files/{time.time()}.{ext}'
                with open(filename, 'wb') as f:
                    for chunk in file_download_response.iter_content(1024):
                        f.write(chunk)
                owner = user_obj
                files = {
                    'document': (f'user_{owner.user_id}/{filename}', open(filename, 'rb')),
                    'owner': (None, owner.user_id)
                }
                response = requests.post('http://localhost:8000/api/tasks/', files=files).json()
                os.remove(filename)
                return
            if attachment['type'] == 'file':
                print(f'{sender_name} sent a file [{file_url}]')
                return
            print(f'{sender_name} sent an invalid attachment')
            return

    text = data['message'].get('text', None)
    if not text:
        print('Invalid message')
        ## SEND MESSAGE BACK TO USER {ERROR}
        return
    print(f'{sender_name} says: {text}')
    intent = detect_intent_text(sender_id, text)
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