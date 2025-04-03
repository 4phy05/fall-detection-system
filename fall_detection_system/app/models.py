from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    # 如果需要添加额外的字段，可以在这里添加
    pass
