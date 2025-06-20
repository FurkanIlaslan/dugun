# Generated by Django 4.2.23 on 2025-06-19 22:25

from django.db import migrations, models
import media_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('media_app', '0002_media_batch_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='media',
            options={'ordering': ['-uploaded_at']},
        ),
        migrations.AlterField(
            model_name='media',
            name='file',
            field=models.FileField(upload_to=media_app.models.media_upload_path),
        ),
        migrations.AddIndex(
            model_name='media',
            index=models.Index(fields=['user', '-uploaded_at'], name='media_app_m_user_id_7ac0a1_idx'),
        ),
        migrations.AddIndex(
            model_name='media',
            index=models.Index(fields=['batch_id'], name='media_app_m_batch_i_28f47e_idx'),
        ),
        migrations.AddIndex(
            model_name='media',
            index=models.Index(fields=['media_type'], name='media_app_m_media_t_a8679b_idx'),
        ),
    ]
