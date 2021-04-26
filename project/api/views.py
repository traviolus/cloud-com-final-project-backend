from rest_framework import viewsets
from rest_framework.response import Response
from google.cloud import pubsub_v1
import json

from prints.serializers import PrintTaskSerializer

from prints.models import PrintTask
from users.models import User
from api.tasks import update_user_current_state


class PrintTaskViewset(viewsets.ModelViewSet):
    queryset = PrintTask.objects.all()
    serializer_class = PrintTaskSerializer

    def publish_message_printer(message):
        publisher_client = pubsub_v1.PublisherClient()
        topic_name = 'projects/cloud-comp-final-project/topics/paas-printing-queue'
        future = publisher_client.publish(topic_name, message.encode())
        print('future: ' + future.result())

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            document = serializer.validated_data['document']
            owner = serializer.validated_data['owner']
            new_document = PrintTask(document=document, owner=owner)
            new_document.save()
            owner_object = User.objects.get(pk=new_document.owner_id)
            message_to_printer = {
                'print_id': new_document.task_id,
                'printer_id': 'printer1',
                'file_url': new_document.document.url,
                'file_name': document.name,
                'user_name': f'{owner_object.first_name} {owner_object.last_name}'
            }
            PrintTaskViewset.publish_message_printer(json.dumps(message_to_printer))
            update_user_current_state(owner_object.user_id, 'QUEUEING')
            return Response(status=200, data={'msg': 'Task started successfully.'})
        except Exception as e:
            return Response(status=400, data={'msg': str(e)})

    def partial_update(self, request, *args, **kwargs):
        print_obj = PrintTask.objects.filter(pk=kwargs['pk']).values()[0]
        if request.data['status'] == 2:
            update_user_current_state(print_obj['owner_id'], 'PRINTING')
        for key in request.data:
            if key in print_obj:
                print_obj[key] = request.data[key]
        new_obj = PrintTask(**print_obj)
        new_obj.save()
        return Response(status=200, data=print_obj)


class PrinterSubscriberViewset(viewsets.ViewSet):
    def create(self, request):

        return Response(status=200, data=request.data)
