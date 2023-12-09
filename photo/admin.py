from django.contrib import admin
from photo.models import Photo
## 1.后台管理系统的使用
## 2.需要创建超级管理员的账号和密码
## 3. 根路由urls.py中添加：path('admin/',admin.site.urls),
## 4.访问后台管理系统http://127.0.0.1:8000/admin/

admin.site.register(Photo) #* 第一步
