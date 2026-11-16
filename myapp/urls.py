from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("overview", views.overview, name="overview"),
    path("about", views.about, name="about"),
    path("privacy", views.privacy, name="privacy"),
    path("404", views.error_404_view, name="404"),
    path("beststocks", views.beststocks, name="beststocks"),
    path("worststocks", views.worststocks, name="worststocks"),
    path("shortsqueeze", views.shortsqueeze, name="shortsqueeze"),
    path("api/quote", views.live_quote, name="live_quote"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("sw.js", views.service_worker, name="service_worker"),
]
