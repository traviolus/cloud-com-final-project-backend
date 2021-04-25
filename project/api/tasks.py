from google.cloud import pubsub_v1, dialogflow
from background_task import background
from datetime import datetime
import json

from users.models import User
from prints.models import PrintTask


def detect_intent_text(session_id, text, project_id='cloud-comp-final-project', language_code='th'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    print("Session path: {}".format(session))
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    print("Query text: {}".format(response.query_result.query_text))
    print(
        "Detected intent: {} (confidence: {})".format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence,
        )
    )
    print("Fulfillment text: {}".format(response.query_result.fulfillment_text))


def process_message(message):
    data = json.loads(message.data.decode())
    message.ack()

    sender = data['sender']['id']
    try:
        user_obj = User.objects.get(facebook_id=sender)
    except User.DoesNotExist:
        print(f'User not found in the system [{sender}]')
        return

    sender = f'{user_obj.first_name} {user_obj.last_name}'
    attachments = data['message'].get('attachments', None)
    if attachments:
        for attachment in attachments:
            if 'sticker_id' in attachment['payload']:
                print(f'{sender} sent a sticker')
                return
            file_url = attachment['payload']['url']
            if attachment['type'] == 'image':    
                print(f'{sender} sent a photo [{file_url}]')
                return
            if attachment['type'] == 'file':
                print(f'{sender} sent a file [{file_url}]')
                return
            print(f'{sender} sent an invalid attachment')
            return

    text = data['message'].get('text', None)
    if not text:
        print('Invalid message')
        return
    print(f'{sender} says: {text}')
    detect_intent_text(1, text)
    return


def process_status_update(message):
    data = json.loads(message.data.decode())
    print(data)
    message.ack()
    print_obj = PrintTask.objects.filter(pk=data['print_id']).values()[0]
    if data['status'] == 'success':
        print_obj['status'] = 3
        new_obj = PrintTask(**print_obj)
        new_obj.save()


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