from django.urls import path 
from  . import views 
from core.views import (Product_view, SnippetList)

from django.urls import re_path
urlpatterns = [
    path('index/',views.index, name='index'),
    path('getDatapoint/',views.getDatapoint, name='getDatapoint'),
    path('upload/', views.upload_txt, name='upload_txt'),
    path('', views.upload_txt, name='upload_txt'),
    # path('retrieve/',views.retrieve,name="retrieve"),
    path('edit/<int:id>',views.edit,name="edit"),
    path('update/<int:id>',views.update,name="update"),
    path('delete/<int:id>',views.delete,name="delete"),
    path('search/',views.search, name="search"),
    path('retrieve/', Product_view.as_view(), name="retrieve"),
    path('status/<int:id>/', views.status, name='status'),
    re_path(r'snippets/$', SnippetList.as_view(), name='snippet-list'),
    path('snippets/', SnippetList.as_view(), name="snippet"),
    # path('locations/', views.locations, name="locations"),
]