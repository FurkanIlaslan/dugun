from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Media
from .forms import MediaForm
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import uuid
from collections import defaultdict
import zipfile
from django.http import HttpResponse
import os
import io

# Create your views here.

@login_required
def media_list(request):
    media = Media.objects.select_related('user').filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'media_app/media_list.html', {'media': media})

@login_required
def gallery(request):
    grouped = defaultdict(list)
    for m in Media.objects.select_related('user').all().order_by('-uploaded_at'):
        grouped[m.batch_id or m.id].append(m)
    gallery_batches = list(grouped.values())
    paginator = Paginator(gallery_batches, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'media_app/gallery.html', {
        'gallery_batches': page_obj,
        'page_obj': page_obj
    })

@login_required
def media_upload(request):
    show_thanks = False
    redirect_to_gallery = False
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        if form.is_valid() and files:
            batch_id = str(uuid.uuid4())
            for f in files:
                media = Media(
                    user=request.user,
                    file=f,
                    title=form.cleaned_data['title'],
                    media_type=form.cleaned_data['media_type'],
                    batch_id=batch_id
                )
                media.save()
            show_thanks = True
            redirect_to_gallery = True
            form = MediaForm()  # Formu sıfırla
    else:
        form = MediaForm()
    return render(request, 'media_app/media_upload.html', {'form': form, 'show_thanks': show_thanks, 'redirect_to_gallery': redirect_to_gallery})

@login_required
def media_edit(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if media.user != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            updated_media = form.save(commit=False)
            if 'file' in request.FILES and request.FILES['file']:
                updated_media.file = request.FILES['file']
            updated_media.save()
            
            # Cache'i temizle
            cache.clear()
            
            return redirect('gallery')
    else:
        form = MediaForm(instance=media)
    return render(request, 'media_app/media_edit.html', {'form': form, 'media': media})

@login_required
def media_delete(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if media.user != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        if media.batch_id:
            # Aynı batch_id'ye sahip tüm medyaları sil
            Media.objects.filter(user=request.user, batch_id=media.batch_id).delete()
        else:
            media.delete()
        # Cache'i temizle
        cache.clear()
        return redirect('gallery')
    return render(request, 'media_app/media_delete_confirm.html', {'media': media})

@cache_page(60 * 5)  # 5 dakika cache
@login_required
def user_gallery(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    media = Media.objects.select_related('user').filter(user=user).order_by('-uploaded_at')
    
    # Sayfalama
    paginator = Paginator(media, 20)  # Her sayfada 20 medya
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'media_app/user_gallery.html', {
        'media': page_obj,
        'gallery_user': user,
        'page_obj': page_obj
    })

@login_required
def download_all_media(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    # Tüm medyaları al (optimize edilmiş sorgu)
    media_files = Media.objects.select_related('user').all()
    
    # ZIP dosyası oluştur
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for media in media_files:
            if os.path.exists(media.file.path):
                # Dosya adını kullanıcı_adı_medya_id_başlık şeklinde yap
                file_name = f"{media.user.username}_{media.id}_{media.title}{os.path.splitext(media.file.name)[1]}"
                zip_file.write(media.file.path, file_name)
    
    # ZIP dosyasını döndür
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="tum_medyalar.zip"'
    return response

@user_passes_test(lambda u: u.is_superuser)
def download_user_media(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    media_files = Media.objects.select_related('user').filter(user=user)
    
    if not media_files.exists():
        return HttpResponse('Bu kullanıcıya ait medya bulunamadı.', content_type='text/plain')
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for media in media_files:
            if os.path.exists(media.file.path):
                file_name = f"{media.user.username}_{media.id}_{media.title}{os.path.splitext(media.file.name)[1]}"
                zip_file.write(media.file.path, file_name)
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_medyalari.zip"'
    return response
