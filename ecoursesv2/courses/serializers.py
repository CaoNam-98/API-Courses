from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Course, Lesson

# CategorySerializer kế thừa model ModelSerializer 
class CategorySerializer(ModelSerializer): 
    class Meta:
        model = Category
        fields = "__all__"

class CourSerializer(ModelSerializer):
    image = SerializerMethodField()

    # course chính là cái khoá học hiện tại (1 course) => mục đích khi bấm đường dẫn image thì hiện ra ảnh
    def get_image(self, course):
        request = self.context['request']
        # Lấy ra name của image của course
        name = course.image.name
        # Kiểm trả tên của image có chứa static hay không
        if name.startswith("static/"):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        
        # request.build_absolute_uri để tự động build ra đường dẫn full cho client
        return request.build_absolute_uri(path)

    class Meta:
        model = Course
        fields = ["id", "subject", "image", "created_date", "category"]

class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "subject", "image", "created_date", "updated_date", "course"]