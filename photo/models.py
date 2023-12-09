from django.db import models
from django.utils.timezone import now

class Photo(models.Model):
    image   = models.ImageField(upload_to='photo/%Y%m%d/')
    created = models.DateTimeField(default=now)

    def __str__(self):
        return self.image.name

    class Meta:
        ordering = ('-created',)
## 注意：
## 模型创建好后需要迁移（就是将数据迁移到数据库的过程） 生成迁移文件：python manage.py makemigrations  执行迁移：python manage.py migrate