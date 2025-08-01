"""
URL configuration for ParkSpaceHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from core.views.users_view import UserView
from core.views.parking_spot_view import ParkingSpotAPIView, parking_spot_view

urlpatterns = [
    path('', UserView.as_view(), name='home'),               
    path('user/', UserView.as_view(), name='user_list'),     
    path('user/signup/', UserView.as_view(), name='signup'), 
    
    # ✅ HTML render view
    path('parking-spots/', parking_spot_view, name='parking-spot-view'),

    # ✅ API endpoint
    path('api/parking-spots/', ParkingSpotAPIView.as_view(), name='parking-spot-api'),
]

