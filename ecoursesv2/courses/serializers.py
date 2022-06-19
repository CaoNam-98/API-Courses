from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Course, Lesson, Tag, Action, Rating, LessonView, Comment, User

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


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


# Cho LessonDetailSerializer kế thừa LessonSerializer
class LessonDetailSerializer(LessonSerializer):
    # Many=True là để lấy ra nhiều item
    tags = TagSerializer(many=True)
    class Meta:
        model = LessonSerializer.Meta.model
        # Lúc gọi thế này thì sẽ bao gồm các fields của LessonSerializer + ['content', 'tags']
        # ["id", "subject", "image", "created_date", "updated_date", "course"] + ['content', 'tags']
        # Viết thế này nghĩa là tags = [{id: value, name: value}]
        fields = LessonSerializer.Meta.fields + ['content', 'tags']

class ActionSerializer(ModelSerializer):
    class Meta:
        model = Action
        fields = ["id", "type", "created_date"]

class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "rate", "created_date"]

class LessonViewSerializer(ModelSerializer):
    class Meta:
        model = LessonView
        fields = ["id", "views", "lesson"]


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content", "created_date", "updated_date"]


class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        #  join_date là trường có bên trong kế thừa
        fields = ["id", "first_name", "last_name", "username", "password", "email", "date_joined"]

        # Ta thêm cái này nhằm chỉ để write chứ không cho phép trả ra password cho client
        extra_kwargs = {
            'password': { 'write_only': 'true'}
        }

    # hashing password bằng cách overwrite lại phương thức create của ModelSerializer
    # validated_data là một dict gồm có các key là các trường trong fields (id, first_name,...) và values là các giá trị mà mình truyền lên cho nó
    def create(self, validated_data):
        # {
        #     "username": "bc",
        #     "password": "123",
        #     "...": "...."
        # }
        # Khi sử dụng User(**validated_data) = User(password="123", username="bc", ...)

        # Lệnh này dùng để khởi tạo một đối tượng user
        user = User(**validated_data)
        # Lệnh này dùng để băm password ra
        user.set_password(user.password)
        user.save()
        return user