"""runnify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from users.views import splash, login_view, logout_view, signup_view, about_view
from playlists.views import playlist_view, create_playlist_view, home, delete_view, publish_view, connect_to_spotify_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("home", home),
    path("login", login_view, name="login"),
    path("signup", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path("about", about_view, name="about"),
    path("delete", delete_view, name="delete"),
    path("publish", publish_view, name="publish"),
    path("create/<str:id>", create_playlist_view, name="create"),
    path("spotifyconnect", connect_to_spotify_view, name="spotifyconnect"),
    path("", splash, name="splash"),
    path('playlist/<str:id>', playlist_view, name="playlist view")
]
