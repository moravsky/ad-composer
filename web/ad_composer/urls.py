from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fetch-url/', views.fetch_url, name='fetch-url'),
]