from django.urls import path
from .views import *


urlpatterns = [
    path('user/', UserProfileAPIView.as_view(), name='user_list'),
]