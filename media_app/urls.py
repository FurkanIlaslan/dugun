from django.urls import path
from . import views

urlpatterns = [
    path('', views.media_list, name='media_list'),
    path('upload/', views.media_upload, name='media_upload'),
    path('gallery/', views.gallery, name='gallery'),
    path('edit/<int:pk>/', views.media_edit, name='media_edit'),
    path('delete/<int:pk>/', views.media_delete, name='media_delete'),
    path('user/<int:user_id>/', views.user_gallery, name='user_gallery'),
    path('download_all/', views.download_all_media, name='download_all_media'),
    path('download_user_media/<int:user_id>/', views.download_user_media, name='download_user_media'),
] 