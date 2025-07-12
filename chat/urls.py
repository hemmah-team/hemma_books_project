from django.urls import path

from .views import getConversations, getMessages, sendMessage

urlpatterns = [
    path("conversations/", getConversations),
    path("messages/", getMessages),
    path("send/", sendMessage),
]
