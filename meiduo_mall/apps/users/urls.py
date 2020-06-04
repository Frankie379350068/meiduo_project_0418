from django.urls import path
from . import views

urlpatterns = [
    # 请求地址： /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 请求地址 /register/
    path('register/', views.UserRegisterView.as_view()),
    # GET http://www.meiduo.site:8000/mobiles/18500000000/count/
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),
]