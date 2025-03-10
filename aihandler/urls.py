from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetAllProduct.as_view(), name='index'),
    path('chat/', views.ChatCommerceService.as_view(), name='chat'),
]