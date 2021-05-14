from rest_framework_jwt.views import obtain_jwt_token
from django.urls import path
from .views import UserViewSet, ProfileViewSet, change_password, current_user
from rest_framework import routers

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('profiles', ProfileViewSet, basename='profiles')

urlpatterns = [
    path('login/', obtain_jwt_token),
    path('current_user/', current_user),
    path('users/<int:pk>/change_password/', change_password),
    # path('register/', )
]

urlpatterns += router.urls
