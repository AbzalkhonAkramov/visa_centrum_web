from django.urls import path

from . import views

urlpatterns = [
    path("", views.vacancy_list, name="vacancy_list"),
    path("<slug:slug>/", views.vacancy_detail, name="vacancy_detail"),
]
