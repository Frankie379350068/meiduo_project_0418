from django.urls import path
from . import views

urlpatterns = [
    # 请求地址： /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),

]