from django.urls import path 
from  . import views 

urlpatterns = [
    path('index/',views.index, name='index'),
    path('getDatapoint/',views.getDatapoint, name='getDatapoint'),
    path('upload/', views.upload_txt, name='upload_txt'),
    path('', views.upload_txt, name='upload_txt'),
    path('retrieve/',views.retrieve,name="retrieve"),
    path('edit/<int:id>',views.edit,name="edit"),
    path('update/<int:id>',views.update,name="update"),
    path('delete/<int:id>',views.delete,name="delete"),
]