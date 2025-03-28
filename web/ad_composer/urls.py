from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/account-names', views.get_account_names, name='account-names'),
    path('fetch-url/', views.fetch_url, name='fetch-url'),
    path('api/personalize', views.personalize_content, name='personalize'),
    path('api/company-info/', views.get_company_info, name='get_company_info'),
    path('api/batch-personalize/', views.start_batch_personalization, name='batch-personalize'),
]