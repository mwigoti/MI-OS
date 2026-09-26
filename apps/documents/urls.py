"""
MwohaOS Documents URL Configuration
"""
from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list_view, name="list"),
    path("upload/", views.document_upload_view, name="upload"),
    path("<int:pk>/download/", views.document_download_view, name="download"),
    path("<int:pk>/delete/", views.document_delete_view, name="delete"),
]
