from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# ID in database is auto create

class User(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/%Y/%m')

class Category(models.Model):
    name = models.CharField(max_length=100,null=False, unique=True)

    def __str__(self):
        return self.name

# Tạo model dùng cho cho nhiều class khác kế thừa đến
class MyModelBase(models.Model):
    subject = models.CharField(max_length=255, null=False)
    # đường dẫn lưu ảnh Media_ROOT + upload_to
    image = models.ImageField(upload_to='courses/%Y/%m', default=None)
    created_date = models.DateTimeField(auto_now_add=True) # mỗi lần add thì nó sẽ tự độn auto_now_add
    updated_date = models.DateTimeField(auto_now=True) # mỗi lần update thì nó sẽ tự động auto_now
    active = models.BooleanField(default=True) # Mặc định là true khi tạo ra
    
    class Meta: 
        abstract = True

class Course(MyModelBase):
    class Meta:
        # unique_together: trong 1 Course table không được trùng subject và category
        unique_together = ('subject', 'category')
        # ordering = ['-id'] là sắp xếp giảm dần theo ID
        ordering = ['-id']
    
    description = models.TextField(null=True, blank=True)
    # on_delete=models.SET_NULL là khi delete category thì Course item của nó vẫn còn nhưng được set là null, vì vậy ta phải bật null=True lên
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.subject

class Lesson(MyModelBase):
    class Meta:
        unique_together = ('subject', 'course')
    
    content = models.TextField()
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)