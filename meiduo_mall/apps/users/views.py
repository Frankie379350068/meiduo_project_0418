from django.shortcuts import render
from django.views import View
from django import http
from apps.users.models import User
import logging, json, re

# Create your views here.
logger = logging.getLogger('django')


class MobileCountView(View):
    def get(self, request, mobile):
        # 路由转换器已经校验mobile，无需再次校验
        # 查询mobile在user表中的记录数
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': '手机号已存在', 'count': count})


class UserRegisterView(View):
    # 接收参数, 请求地址 /register/
    def post(self, request):
        json_dict = json.loads(request.body.decode())
        username = json_dict.get('username')
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        mobile = json_dict.get('mobile')
        # sms_code = json_dict.get('sms_code')
        allow = json_dict.get('allow')
        # 校验参数
        if not all([username, password, password2, mobile, allow]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({'code': 400, 'errmsg': 'username参数格式有误'})
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': 'password参数格式有误'})
        if password != password2:
            return http.JsonResponse({'code': 400, 'errmsg': '两次输入的密码不一致'})
        if not re.match(r'^1[3-9][0-9]{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': 'mobile参数格式有误'})
        if not allow:
            return http.JsonResponse({'code': 400, 'errmsg': 'allow参数有误'})

        # 处理核心业务逻辑
        try:  # 远程连接是有可能失败的，所以必须是try
            User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '注册失败'})
        return http.JsonResponse({'code': 0, 'errmsg': '注册成功'})


class UsernameCountView(View):
    def get(self, request, username):
        # 查询username在数据库中的个数
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})
