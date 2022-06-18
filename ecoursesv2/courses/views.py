from telnetlib import STATUS
from django.shortcuts import render
from rest_framework import viewsets, generics, status
from .models import Category, Course
from rest_framework.decorators import action
from .serializers import CategorySerializer, CourSerializer, LessonSerializer
from rest_framework.response import Response
from .paginator import BasePaginator

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
    