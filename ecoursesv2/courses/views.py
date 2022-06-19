from telnetlib import STATUS
from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions 
from .models import Category, Course, Lesson, LessonView, Tag, Action, Rating, Comment, User
from rest_framework.decorators import action
from django.http import Http404
# Để trong () để có thể xuống dòng
from .serializers import ( CategorySerializer, 
CourSerializer, 
LessonSerializer, 
LessonDetailSerializer,
ActionSerializer,
RatingSerializer,
LessonViewSerializer,
CommentSerializer, 
UserSerializer
)
from rest_framework.response import Response
from .paginator import BasePaginator
from django.db.models import F
from rest_framework.views import APIView
# setting này sẽ địa diện cho toàn bộ setting ở bên trong setting của ecoursesv2
from django.conf import settings

# Create your views here.
# API get danh sách tất cả các khoá học
# Khi tạo CategoryViewSet kế thừa từ viewsets.ViewSet thì sẽ tạo ra các bộ có sẵn như: GET, POST, PUT, PATCH, DELETE
# Khi tạo CategoryViewSet kế thừa từ viewsets.generics.ListAPIView thì sẽ hiện thực list của thằng ViewSet cho mình luôn
class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Mục tiêu dùng viewset là để tạo ra các API endpoint sẵn cho mình
class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = CourSerializer
    # Dùng cái này phân trang là 20 item
    pagination_class = BasePaginator

    # Đối với queryset nếu không có gì thì ta chỉ cần khai báo như sau:
    # queryset = 

    # Trong trường hợp mình muốn thêm thì ta phải overwriter lại thuộc tính queryset thì dùng get_queryset thì nó sẽ ghi đè lên queryset bên trên
    def get_queryset(self):
        courses = Course.objects.filter(active=True)
        # Mình không nên lấy self.request.query_params['q'] vì nếu không có q thì sẽ báo lỗi (truy xuất thuộc tính của dict)
        # Trường hợp self.request.query_params.get('q') thì nếu không có q thì sẽ không báo lỗi và giá trị khi q không có sẽ là None
        q = self.request.query_params.get('q')
        if q is not None:
            # __contains là để tạo ra Like bên trong mệnh đề Where
            courses = courses.filter(subject__contains=q)

        cate_id = self.request.query_params.get('category_id')
        if cate_id is not None:
            courses = courses.filter(category_id=cate_id)

        return courses

    # detail=True vì khi ta truyền lên url có chứa course_id của khoá học: /courses/{courses_id} thì lúc đó get_lessons phải có biến pk=courses_id được truyền lên làm tham số cho hàm get_lessons
    # urls_path có do phía sau của url truyền lên từ client có dạng /courses/{courses_id}/lessons
    # Nếu không có {courses_id} => detail=False, nếu có {courses_id} => detail=True
    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        # Cách 1: lấy Course tương ứng với pk như sau:
        course = Course.objects.get(pk=pk) # /courses/1/lessons/ => pk=1
        # Cách 2: Lấy Course tương ứng với pk như sau: khi gọi self.get_object() thì nó sẽ tự động truyền pk vào bên trong luôn rồi
        # course = self.get_object()
        # Do trong Model Lesson có chứa relatied_name nên mình có thể truy xuất lấy tất cả các Lesson của Course như sau
        # lessons được gọi từ course.lessons là từ related_name="lessons"
        lessons = course.lessons.filter(active=True)

        q = request.query_params.get('q')
        if q is not None:
            lessons = lessons.filter(subject__icontains=q)

        return Response(LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)

    
# generics.RetrieveAPIView sẽ giúp tạo ra API dạng /lession/{lession_id}
class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = LessonDetailSerializer

    # def get_permissions(self):
    #     # Với 3 action này của LessionViewSet thì bắt buộc phải login
    #     if self.action in ['add_comment', 'take_action', 'take_rating']:
    #         return [permissions.IsAuthenticated()]
    #     return [permissions.AllowAny()]

    # Xử lý viết API add Tags dạng: lession/{lession_id}/tags/ cho phép gửi một mảng Tags
    @action(methods=['post'], detail=True, url_path='tags')
    def add_tag(self, request, pk):
        try:
            lesson = self.get_object() # Trường hợp nếu không tìm thấy {lession_id} thì sẽ trả về 404 nên ta bắt lỗi như sau
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # else nghĩa là trường hợp lesson = self.get_object() lấy được thành công thì chạy tiếp vào else
        else:
            # Lấy data được gửi lên từ client nằm bên trong body bằng cách
            tags = request.data.get("tags")
            if tags is not None:
                for tag in tags:
                    # get_or_create(name=Tag) nghĩa là nếu name của Tag trong DB trùng với thằng tag được gửi lên thì sẽ lấy ra, ngược lại thì sẽ tạo mới.
                    # , _ nghĩa là đây là cái cờ để nhận biết lấy ra hay là tạo mới. Trong trường hợp API này mình không cần quan tâm cái này
                    t, _ = Tag.objects.get_or_create(name=tag)
                    print('t đây nhé: ', t)
                    print('huhu: ', Tag.objects.get_or_create(name=tag))
                    # Lệnh này chỉ thêm item chưa tồn tại trong list vào
                    lesson.tags.add(t)
                # Lưu lại toàn bộ tag
                lesson.save()
                return Response(self.serializer_class(lesson).data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True, url_path='like')
    def take_like(self, request, pk):
        # Ở đây xảy ra 2 ngoại lệ:
        # 1. type lấy không được do client không gửi lên => IndexError
        # 2. dữ liệu client gửi lên không phải số => int(string) sẽ báo lỗi => ValueError
        # => Mình cần đặt trong try...except
        try:
            action_type = int(request.data['type'])
        except IndexError or ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            action = Action.objects.create(
                type=action_type, 
                # creator=request.User, 
                lesson=self.get_object()
            )
            # Để trả Action đã tạo thì phải cho đi qua serializer để xác định các trường trả về
            return Response(ActionSerializer(action).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='rating')
    def take_rate(self, request, pk):
        try:
            rating = int(request.data['type'])
        except IndexError or ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            r = Rating.objects.create(
                rate=rating, 
                # creator=request.User, 
                lesson=self.get_object()
            )
            # Để trả Action đã tạo thì phải cho đi qua serializer để xác định các trường trả về
            return Response(RatingSerializer(r).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='views')
    def inc_view(self, request, pk):
        # created là đnag tạo mới hoặc get ra: false là get, true là update
        # Ta dùng get_or_create bởi vì self.get_object() trả về lesson
        # get_or_create lấy ra LessonView có lesson = lesson đã get ở trên 
        # Trường hợp không có LessonView thì sẽ create một LessonView (Chưa từng call API lên)
        # Trường hợp có LessonView thì sẽ get LessonView ra (Đã từng call API rồi)
        v, created = LessonView.objects.get_or_create(lesson=self.get_object())
        v.views = F('views') + 1
        v.save()
        # Trước khi trả giá trị views sau update ra thì phải chuyển nó thành số, 
        # nếu không nó trả về 1 object expression => không đúng
        v.refresh_from_db()
        return Response(LessonViewSerializer(v).data, status=status.HTTP_200_OK)

    # Ta để detail=True để mình biết cái comment này dùng để thêm vào Lesson nào. Vì có {lesson_id}
    @action(methods=['post'], detail=True, url_path='add-comment')
    def add_comment(self, request, pk):
        content = request.data.get('content')
        # content khác None và rỗng
        if content:
            c = Comment.objects.create(
                content=content, 
                lesson=self.get_object(),
                # creator=request.user
            )
            return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Khi ta cho class CommentViewSet kế thừa từ thằng generics.DestroyAPIView thì sẽ tạo ra một phương thức delete
# Khi ta cho class CommentViewSet kế thừa từ thằng generics.UpdateAPIView thì sẽ tạo ra một phương thức là Update API
# URL: /comments/{comment_id} thì khi ta get_object() đã lấy ra được comment ứng với comment_id rồi 
# => mình chỉ cần check user login và thông tin user gửi lên từ client có trùng nhau để delete hay không
class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    #  Mình phải thêm serializer_class cho trường hợp là partial_update vì nó có data trả về
    # Đối với trường hợp delete thì mình không cần khai báo cái này cũng được
    serializer_class = CommentSerializer
    # Thực hiện thao tác chứng thực bẳng cách này => có login
    # permission_classes = [permissions.IsAuthenticated]

    # Thực hiện overwritting hàm delete để check quyền từ generics.DestroyAPIView xem được phép delete hay không
    def delete(self, request, *args, **kwargs):
        # request.user là user đã chứng thực rồi
        # Nếu user đã chứng thực rồi == thông tin user nằm bên trong comment được lấy ra từ self.get_object().creator => delete
        # if request.user == self.get_object().creator:
            # Gọi đến phương thức delete của generics.DeleteAPIView
        return super().destroy(request, *args, **kwargs)
        # return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        # if request.user == self.get_object().creator:
            # Gọi đến phương thức delete của generics.UpdateAPIView
            # Ở đây do nó gọi đến phương thức update của cha nên nó không xác định được cái nào được update 
            # Vì vậy, mình phải gửi chính xác cái key là content từ client lên thì nó mới hiểu được là đang update content
        return super().partial_update(request, *args, **kwargs)
        # return Response(status=status.HTTP_403_FORBIDDEN)

# Ta dùng generics.CreateAPIView để tạo ra một phương thức post của /users/
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

# đối với APIView thì nó sẽ không cung cấp các phương thức như ViewSet nên mình phải viết
# Mỗi phương thức của nó tương ứng với 1 phương thức HTTP 
# Hàm này để lấy thông tin client_id, client_serect bên trong setting
class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)
