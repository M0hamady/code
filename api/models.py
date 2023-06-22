from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User,Group,Permission

from django.conf import settings
from django.core.files.storage import FileSystemStorage
class CustomUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    profile_pic = models.ImageField(upload_to='profiles/profile_pics', blank=True, null=True)
    def save_profile_pic(self, request):
        if request.method == 'POST' and request.FILES.get('profile_pic'):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(f"{request.user.username}/{profile_pic.name}", profile_pic)
            uploaded_file_url = fs.url(filename)
            # Build the absolute URL of the uploaded image
            absolute_url = request.build_absolute_uri(uploaded_file_url)
            return absolute_url
        
