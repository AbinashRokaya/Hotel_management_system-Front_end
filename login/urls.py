"""
URL configuration for login project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from log import views
from django.conf.urls.static import static
from django.conf import settings

from log.views import policy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.SignupPage,name="signup"),
    path('home/',views.HomePage,name='home'),
    path('login/',views.LoginPage,name='login'),
    path('logout/',views.LogoutPage,name='logout'),
    path('room/<int:id>',views.room,name='room'),
    path('hotel/', views.hotel, name='hotel'),
    path('payment/<int:id>/<int:day>/<int:room>', views.payment, name='payment'),
    path('reservation/<int:id>', views.reservation, name='reservation'),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('term_of_use/',views.term,name='term'),
    path('policy/',views.policy,name="policy"),
    path('environment-policy/',views.environment,name='environment'),
    path('news/',views.blog,name='blog'),
    path('guest/',views.guest,name='guest'),
    path('porfile/',views.porfile,name='porfile')

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
