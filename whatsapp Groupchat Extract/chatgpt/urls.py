from django.urls import path
from .views import (ChatView, ChatUpdateDeleteApiView, GptView, GptUpdateDeleteApiView)
from . import views
# from .views import CustomChatView

urlpatterns = [
    # path('chatgpt/', views.ChatView,  name='chatgpt'),
    path('', views.index,  name='index'),
    path('chat/', ChatView.as_view()),
    path('chat/<int:pk>/', ChatUpdateDeleteApiView.as_view()),
    # path('myview/', CustomChatView.as_view(), name='my-view'),
    path('gpt/', GptView.as_view()),
    path('gpt/<int:pk>/', GptUpdateDeleteApiView.as_view()),
]
