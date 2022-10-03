from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('overview', views.overview, name='overview'),

    path('about', views.about, name='about'),

    path('contact', views.contact, name='contact'),

    path('copyright', views.copyright, name='copyright'),

]
