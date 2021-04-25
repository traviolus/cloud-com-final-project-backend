from rest_framework import routers
from api.views import PrintTaskViewset, SubscriberViewset

router = routers.DefaultRouter()
router.register(r'tasks', PrintTaskViewset)
router.register(r'subscriber', SubscriberViewset, basename='Subscriber')