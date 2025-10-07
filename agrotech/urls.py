"""
URL configuration for agrotech project.

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
from agrotech import views
from .views import yield_prediction_view

urlpatterns = [
    path('', views.home, name='home'),
    path('index.html', views.home, name='index_html'),
    path("admin/", admin.site.urls),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='services'),
    path('contact/', views.contact, name='contact'),
    path('signin/', views.service, name='signin'),
    path('test/', views.test, name='test'),
    path('fertilizer/', views.fertilizer, name='fertilizer'),
    path('insurance/', views.insurance, name='insur'),
    path('buy/', views.buy, name='buy'),
    path("predict/", views.predict_plant_disease, name="predict"),
    path('pune_apmc_table/', views.pune_apmc_table, name='apmc_rates'),
    path("apmc/scraper/", views.pune_apmc_scraper, name="pune_apmc_scraper"),
    path("apmc/history/", views.pune_apmc_history, name="pune_apmc_history"),
    path('weather/', views.weather_dashboard, name='weather_dashboard'),
    path("recommend/", views.fertilizer_recommendation, name="fertilizer_recommend"),
    path('remove/<int:city_id>/', views.remove_city, name='remove_city'),
    path('yield-predict/', yield_prediction_view, name="yield_predict"),
    path('tts_audio/', views.tts_audio, name='tts_audio'),


]
