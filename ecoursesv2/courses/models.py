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
    tags = models.ManyToManyField('Tag', related_name="lessons", blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ActionBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    # Bài viết nào
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    # Người tạo
    # creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta: 
        abstract = True

class Action(ActionBase):
    # range(3) nghĩa là sẽ sinh ra 1 dải 0,1,2 => LIKE=0, HAH=1 HEART=2
    LIKE, HAHA, HEART = range(3)
    ACTIONS = [
        # LIKE là lưu xuống CSDL, like là trả về cho front-end
        (LIKE, 'like'),
        (HAHA, 'haha'),
        (HEART, 'heart')
    ]
    # Type sẽ lưu ở dạng số trong DB do ta đã range(3) rồi
    type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)

class Rating(ActionBase):
    rate = models.PositiveSmallIntegerField(default=0)


class LessonView(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    # Nếu lesson bị xoá thì view của nó cũng bị xoá luôn
    # Một bài học chỉ có 1 số lượng view chứ không quan tâm đến người dùng thì dùng OneToOneField là duy nhất
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField()
    # Comment này phải link với bài học nào đó
    # Khi Lesson bị xoá thì comment cũng bị xoá
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    # Khi user bị xoá thì toàn bộ comment cũng bị xoá theo luôn
    # creator = models.ForeignKey(User,  on_delete=models.CASCADE)
    # Thời gian update, create
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content