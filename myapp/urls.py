from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('overview', views.overview, name='overview'),

    path('about', views.about, name='about'),

    path('contact', views.contact, name='contact'),

    path('copyright', views.copyright, name='copyright'),

    path('404', views.error_404_view, name='404'),

    path('beststocks', views.beststocks, name='beststocks'),

    path('worststocks', views.worststocks, name='worststocks'),

]
