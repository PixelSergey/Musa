from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("next/", views.next, name="next"),
    path("delete/", views.delete, name="delete"),
    path("stop/", views.stop, name="stop"),
]
