from rest_framework import viewsets
from rest_framework.response import Response

from prints.serializers import PrintTaskSerializer

from prints.models import PrintTask


class PrintTaskViewset(viewsets.ModelViewSet):
    queryset = PrintTask.objects.all()
    serializer_class = PrintTaskSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            document = serializer.validated_data['document']
            owner = serializer.validated_data['owner']
            new_document = PrintTask(document=document, owner=owner)
            new_document.save()
            # TO PRINT PUB/SUB
            return Response(status=200, data={'msg': 'Task started successfully.'})
        except Exception as e:
            return Response(status=400, data={'msg': str(e)})


class SubscriberViewset(viewsets.ViewSet):
    def create(self, request):
        return Response(status=200, data=request.data)
