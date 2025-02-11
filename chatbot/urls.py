from django.urls import path
from .views import chatbot_home, chatbot_response

urlpatterns = [
    path('', chatbot_home, name='chatbot_home'),  # Chatbot UI
    path('get-response/', chatbot_response, name='chatbot_response'),
]
