

from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from apps.libs.captcha.captcha import captcha
import random, logging
from django import http

logger = logging.getLogger('django')

class SmsCodeView(View):
    def get(self, request, mobile):
        # GET http: // www.meiduo.site: 8000/sms_codes/18500000000/?image_code=IIJB&image_code_id=846b06a7-5766-4175-8d1f-c05625d0679c
        # 接收参数
        image_code_client = request.GET.get('image_code')
        image_code_id_client = request.GET.get('image_code_id') # 其实就是获取到uuid
        # 校验参数
        if not all([image_code_client, image_code_id_client]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 对比图形验证码
        # 从redis数据库中取图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_image_code = redis_conn.get('img_%s' % image_code_id_client)
        # 每提取一次立即删除redis数据库中的图形验证码，防止被恶意用户利用
        redis_conn.delete('img_%s' % image_code_id_client)
        # 比对图形验证码
        redis_image_code = redis_image_code.decode()
        if image_code_client.lower() != redis_image_code.lower():
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码错误'})
        # 生成随机短信验证码并保存到redis数据库，发送短信给客户手机
        random_num = random.randint(0, 999999)
        sms_code = '%06d' % random_num
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        logger.info(sms_code)
        # 相应结果
        return http.JsonResponse({'code': 0, 'errmsg': 'ok'})

class ImageCodeView(View):
    def get(self, request, uuid):
        # 因为路由转换器已经验证过uuid，所以不需要校验了
        # 生成图形验证码
        text, image = captcha.generate_captcha()
        # 创建redis连接对象，把图形验证码存入redis数据库
        redis_conn = get_redis_connection('verify_code')
        # setex(key,time,value)
        redis_conn.setex('img_%s' % uuid, 300, text)
        # 响应结果，响应图片类型的数据http.HttpReponse
        return http.HttpResponse(image, content_type = 'img.jpg')

