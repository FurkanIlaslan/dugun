from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from datetime import datetime

def media_upload_path(instance, filename):
    # Dosya yolunu tarih bazında organize et
    date_path = instance.uploaded_at.strftime('%Y/%m/%d') if instance.uploaded_at else datetime.now().strftime('%Y/%m/%d')
    return os.path.join('uploads', date_path, filename)

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Fotoğraf'),
        ('video', 'Video'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=media_upload_path)
    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    batch_id = models.CharField(max_length=36, blank=True, db_index=True)

    def __str__(self):
        return f"{self.title} ({self.media_type})"

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['media_type']),
        ]
