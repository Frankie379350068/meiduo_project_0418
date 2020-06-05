from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render
from django.views import View
from django import http
from apps.users.models import User
import logging, json, re
from django_redis import get_redis_connection
from apps.users.utils import generate_verify_email_url
# Create your views here.
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email_url
logger = logging.getLogger('django')






class CreateEmailView(LoginRequiredJSONMixin,View):
    def put(self, request):
        # 1. 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 2. 校验
        if not email:
            return http.JsonResponse({'code': 400, 'errmsg': '缺少email参数'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': 400, 'errmsg': '参数email格式有误'})
        # 3.添加email
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '添加失败'})
        # 4. * 最核心代码：服务端生成URL链接地址给网易stmp邮件中转站
        email_verify_url = generate_verify_email_url(request.user)
        send_verify_email_url.delay(email, email_verify_url)
        return http.JsonResponse({'code': 0, 'errmsg': 'ok'})


class UserInfoView(LoginRequiredJSONMixin, View):
    def get(self, request):
        json_dict = {'code': 0,
                     'errmsg': 'ok',
                     'info_data': {
                         'username': request.user.username,
                         'mobile': request.user.mobile,
                         'email': request.user.email,
                         'email_active': request.user.email_active}
                     }
        return http.JsonResponse(json_dict)


class LogoutView(View):
    def delete(self, request):
        # 清理session，从而清除登录状态
        logout(request)
        # 清理用户名cookie
        response = http.JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


class LoginView(View):
    def post(self, request):
        # 1. 接收参数
        json_dict = json.loads(request.body.decode())
        account = json_dict.get('username')
        password = json_dict.get('password')
        remembered = json_dict.get('remembered')
        # 2. 校验参数
        if not all([account, password, remembered]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        if not re.match(r'^[0-9A-Za-z_-]{5,20}$', account):
            return http.JsonResponse({'code': 400, 'errmsg': '用户名username格式错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '密码password格式错误'})
        # 3. 用户名和密码匹配
        # 3.1 最核心代码：django封装好的核心认证函数authenticat()，仅仅证明user是注册用户且密码正确
        # 实现多账号登录
        # * 比较难理解源码，可了解。判断用户输入的是用户名还是手机号； User类继承自Abstract类，所以也有USERNAME_FIELD属性，给自己后改写
        if re.match(r'^1[3-9]\d{9}$', account):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        user = authenticate(request=request, username=account, password=password)
        if not user:
            # 一定要写'用户名或者密码错误', 不能把真实的情况告诉用户，安全性考虑！
            return http.JsonResponse({'code': 400, 'errmsg': '用户名或者密码错误'})
        # 4. 状态保持
        # 4.1 状态保持： 通过状态保持来执行登录操作
        login(request, user)
        # 4.2 依据remembered的值来设置session状态保持周期
        # 如果用户选择了'记住登录状态'，则默认保持两周，否则在浏览器会话结束后，状态保持就销毁
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        # 5. 响应结果
        # 5.1创建响应对象，写入cookie
        response = http.JsonResponse({'code': 0, 'errmsg': '登录成功'})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        # 5.2响应结果
        return response


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
        sms_code = json_dict.get('sms_code')
        allow = json_dict.get('allow')
        # 校验参数
        if not all([username, password, password2, mobile, sms_code, allow]):
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
        # 图形验证码已经在发送短信完成校验，所以无需再次校验； 检验短信验证码
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile).decode()

        if sms_code != sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码错误'})

        # 处理核心业务逻辑
        try:  # 远程连接是有可能失败的，所以必须是try
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '注册失败'})
        login(request, user)
        # 写入cookie
        response = http.JsonResponse({'code': 0, 'errmsg': '注册成功'})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response


class UsernameCountView(View):
    def get(self, request, username):
        # 查询username在数据库中的个数
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})
