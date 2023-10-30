from django.contrib import admin
from django.urls import path,include
from . import views
from main.views import  SearchView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('',views.index,name='index'),
    path('movies/<int:id>',views.movies,name='movies'),
    path('seat/<int:id>',views.seat,name='seat'),
    path('booked',views.booked,name='booked'),
    path('ticket/<int:id>',views.ticket,name='ticket'),
    path('download-ticket/<int:id>/', views.download_ticket, name='download_ticket'),
    path('search/', SearchView.as_view(),name='search'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)