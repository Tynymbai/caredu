from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, DriverGroupViewSet, LectureViewSet,
    TestViewSet, TestResultViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'groups', DriverGroupViewSet)
router.register(r'lectures', LectureViewSet)
router.register(r'tests', TestViewSet)
router.register(r'results', TestResultViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]