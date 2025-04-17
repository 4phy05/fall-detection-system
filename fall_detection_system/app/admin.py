from django.contrib import admin
from .models import CustomUser

# Register your models here.

admin.site.register(CustomUser)  # 注册模型，使其出现在后台
