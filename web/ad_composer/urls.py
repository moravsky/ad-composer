from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/account-names', views.get_account_names, name='account-names'),
    path('fetch-url/', views.fetch_url, name='fetch-url'),
    path('api/personalize', views.personalize_content, name='personalize'),
]