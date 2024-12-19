import os

from django.db import models
from django.contrib.auth.models import User

class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='uploads/original')
    image = models.ImageField(upload_to='uploads/detected')
    processed = models.BooleanField(default=False)
    detected_class = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    x1 = models.IntegerField(blank=True, null=True)
    y1 = models.IntegerField(blank=True, null=True)
    x2 = models.IntegerField(blank=True, null=True)
    y2 = models.IntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} by {self.user.username}"

    def delete(self, *args, **kwargs):
        if self.original_image and os.path.isfile(self.original_image.path):
            os.remove(self.original_image.path)
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)