from rest_framework import routers
from api.views import PrintTaskViewset

router = routers.DefaultRouter()
router.register(r'tasks', PrintTaskViewset)