from django.urls import path
from . import views

urlpatterns = [
    # 图形验证码请求地址 image_codes/(?P<uuid>[\w-]+)/
    path('image_codes/<uuid:uuid>/', views.ImageCodeView.as_view()),
    # 短信：GET http: // www.meiduo.site: 8000/sms_codes/18500000000/?image_code=IIJB&image_code_id=846b06a7-5766-4175-8d1f-c05625d0679c
    path('sms_codes/<mobile:mobile>/', views.SmsCodeView.as_view()),

]