from rest_framework import routers
from api.views import PrintTaskViewset, PrinterSubscriberViewset
from api.tasks import get_messages, get_update_status_from_printer
import threading

router = routers.DefaultRouter()
router.register(r'tasks', PrintTaskViewset)
router.register(r'printer_subscriber', PrinterSubscriberViewset, basename='Subscriber')

threads = list()
t_1 = threading.Thread(target=get_messages)
t_2 = threading.Thread(target=get_update_status_from_printer)
threads.append(t_1)
threads.append(t_2)
t_1.start()
t_2.start()