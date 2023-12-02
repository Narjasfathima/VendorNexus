from django.urls import path

from vendor.consumers import MetricConsumer

websocket_urlpatterns = [
    path('ws/path_name/', MetricConsumer.as_asgi()), # Using asgi
]