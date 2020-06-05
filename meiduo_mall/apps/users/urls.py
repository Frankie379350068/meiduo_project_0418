from django.urls import path
from . import views

urlpatterns = [
    # 请求地址： /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 请求地址 /register/
    path('register/', views.UserRegisterView.as_view()),
    # GET http://www.meiduo.site:8000/mobiles/18500000000/count/
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),
    # POST http://www.meiduo.site:8000/login/
    path('login/', views.LoginView.as_view()),
    # delete http://www.meiduo.site:8000/logout/ , 删除服务器数据，所以是delete请求
    path('logout/', views.LogoutView.as_view()),
    # GET http://www.meiduo.site:8000/info/
    path('info/', views.UserInfoView.as_view()),
    # PUT http://www.meiduo.site:8000/emails/
    path('emails/', views.CreateEmailView.as_view()),


]