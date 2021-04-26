from rest_framework import serializers
from prints.models import PrintTask


class PrintTaskSerializer(serializers.ModelSerializer):
    def get_status(self, obj):
        return obj.get_status_display() 

    status = serializers.SerializerMethodField()


    class Meta:
        model = PrintTask
        fields = '__all__'
