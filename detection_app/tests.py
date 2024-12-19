from django.test import TestCase
from django.contrib.auth.models import User
from .models import UploadedImage

class SimpleTest(TestCase):
    def test_upload_image_model(self):
        user = User.objects.create(username='testuser')
        img = UploadedImage.objects.create(user=user, image='test.jpg')
        self.assertEqual(img.user.username, 'testuser')
        self.assertFalse(img.processed)