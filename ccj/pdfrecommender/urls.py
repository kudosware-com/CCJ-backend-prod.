from django.contrib import admin
from django.urls import path
from .views import search_pdf_view, index

urlpatterns = [
    path('', index, name='index'),
    path('search/<str:expression>/', search_pdf_view),
]