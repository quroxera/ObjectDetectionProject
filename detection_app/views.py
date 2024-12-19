from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UploadImageForm, RegistrationForm
from .models import UploadedImage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import cv2
import numpy as np
import os
from django.conf import settings

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant",
           "sheep", "sofa", "train", "tvmonitor"]

def home_view(request):
    return render(request, 'home.html')

@login_required
def dashboard_view(request):
    images = UploadedImage.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'images': images})

@login_required
def add_image_view(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.user = request.user
            img.save()
            return redirect('dashboard')
    else:
        form = UploadImageForm()
    return render(request, 'add_image_feed.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Ошибка авторизации")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь можете войти.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

@login_required
def process_image_view(request, image_id):
    img_obj = get_object_or_404(UploadedImage, id=image_id, user=request.user)
    if not img_obj.processed:
        prototxt = os.path.join(settings.BASE_DIR, 'model', 'MobileNetSSD_deploy.prototxt')
        model = os.path.join(settings.BASE_DIR, 'model', 'MobileNetSSD_deploy.caffemodel')
        net = cv2.dnn.readNetFromCaffe(prototxt, model)

        original_path = img_obj.original_image.path
        image = cv2.imread(original_path)

        if image is None:
            print("Не удалось открыть изображение по пути:", original_path)
            return redirect('dashboard')

        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300,300)), 0.007843, (300,300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        max_conf = 0
        best_box = None
        best_class = None

        for i in range(detections.shape[2]):
            confidence = detections[0,0,i,2]
            if confidence > max_conf:
                idx = int(detections[0,0,i,1])
                if idx < len(CLASSES):
                    best_class = CLASSES[idx]
                    max_conf = confidence
                    box = detections[0,0,i,3:7] * np.array([w,h,w,h])
                    (startX, startY, endX, endY) = box.astype("int")
                    best_box = (startX, startY, endX, endY)

        if best_class and best_class != 'background':
            cv2.rectangle(image, (best_box[0], best_box[1]), (best_box[2], best_box[3]), (0,255,0), 2)

            # Генерируем имя для обработанного файла
            processed_filename = f"processed_{img_obj.id}.jpg"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'detected', processed_filename)
            cv2.imwrite(processed_path, image)

            # Обновляем поле image, которое загружено в uploads/detected
            img_obj.image.name = f"uploads/detected/{processed_filename}"
            img_obj.detected_class = best_class
            img_obj.confidence = float(max_conf)
            (img_obj.x1, img_obj.y1, img_obj.x2, img_obj.y2) = best_box
            img_obj.processed = True
            img_obj.save()
        else:
            img_obj.detected_class = "Object not found"
            img_obj.confidence = 0.0
            img_obj.processed = True
            img_obj.save()

    return redirect('dashboard')

@login_required
def delete_image_view(request, image_id):
    img_obj = get_object_or_404(UploadedImage, id=image_id, user=request.user)
    img_obj.delete()
    return redirect('dashboard')