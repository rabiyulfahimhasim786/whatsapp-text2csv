from django.urls import path 
from  . import views 

urlpatterns = [
    path('index/',views.index, name='index'),
    path('getDatapoint/',views.getDatapoint, name='getDatapoint'),
    path('upload/', views.upload_txt, name='upload_txt'),
]