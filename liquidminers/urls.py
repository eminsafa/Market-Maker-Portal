"""liquidminers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LoginView

from . import views

from liquidminers.views import *

urlpatterns = [

    path('initialization/', views.initialization, name='initialization'),
    path('engine/', views.engine, name='engine'),
    path('admin/dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),

    path('', views.home, name='index'),
    path('home/', views.home, name='home'),
    path('markets/', views.markets, name='markets'),
    path('bot/', views.new_bot, name='bot'),
    path('new_bot/', views.new_bot, name='new_bot'),
    path('settings/', views.settings, name='settings'),
    path('login/', LoginView.as_view(template_name='pages/login.html'), name="login"),
    path('register/', views.register, name='register'),
    path('admin/panel', views.home, name='admin_panel'),
    path('logout/', views.user_logout, name='logout'),

    path('stats/', views.stats, name='stats'),

    path('api/cancel_order', views.api_cancel_order, name='api_cancel_order'),

    path('exchange_monitor/', views.exchange_monitor, name='exchange_monitor'),   # @todo hide on prod
    path('exchange_monitor/cancel_order', views.cancel_admin_order, name='cancel_monitor_order'),   # @todo hide on prod
    path('exchange_monitor/create_admin_order', views.create_admin_order, name='create_monitor_order'),   # @todo hide on prod
    path('test/', views.test, name='test'),                                 # @todo hide on prod
    path('uc/', views.under_construction, name='under_construction'),                                 # @todo hide on prod

    # Static Pages
    path('wiki', views.home, name='wiki'),
    path('terms_of_use', views.home, name='terms_of_use'),
    path('privacy_policy', views.home, name='privacy_policy'),
    path('contact_us', views.home, name='contact_us'),
    path('faqs', views.home, name='faqs'),
    path('how_to_start', views.home, name='how_to_start'),

]
