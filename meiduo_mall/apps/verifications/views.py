from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from apps.libs.captcha.captcha import captcha
import random, logging
from django import http

from apps.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code

logger = logging.getLogger('django')


class SmsCodeView(View):
    def get(self, request, mobile):
        # GET http: // www.meiduo.site: 8000/sms_codes/18500000000/?image_code=IIJB&image_code_id=846b06a7-5766-4175-8d1f-c05625d0679c
        # *补充逻辑: 先判断用户是否频繁发送短信
        redis_conn = get_redis_connection('verify_code')
        send_flag_mobile = redis_conn.get('send_flag_%s' % mobile)
        if send_flag_mobile:
            return http.JsonResponse({'code': 400, 'errmsg': '请勿频繁发送短信验证码'})
        # 1. 接收参数
        image_code_client = request.GET.get('image_code')
        image_code_id_client = request.GET.get('image_code_id')  # 其实就是获取到uuid
        # 2. 校验参数
        if not all([image_code_client, image_code_id_client]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 3. 对比图形验证码，从redis数据库中取图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_image_code = redis_conn.get('img_%s' % image_code_id_client)
        # 3.1 *小细节：提取可能没数据
        if not redis_image_code:
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码失效'})
        # 3.2 每提取一次立即删除redis数据库中的图形验证码，防止被恶意用户利用
        redis_conn.delete('img_%s' % image_code_id_client)
        # 3.3 比对图形验证码
        redis_image_code = redis_image_code.decode()
        if image_code_client.lower() != redis_image_code.lower():
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码错误'})
        # 3.4 生成随机短信验证码并保存到redis数据库，发送短信给客户手机
        random_num = random.randint(0, 999999)
        sms_code = '%06d' % random_num
        logger.info(sms_code)  # 小技巧：可以在终端输出，测试的时候绕过云通讯，查看生成的短信验证码
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1) # *小细节：设置send_flag_mobile，标识，防止恶意用户再次刷新页面就可以频繁再次发送短信
        # *小细节：创建pipline管道提升redis读写性能
        pl = redis_conn.pipline()
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('send_flag_%s' % mobile, 60, 1)
        pl.execute()
        # 3.5 发送短信
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # *小细节: 由于客户收到短信可能是会有延迟，他会在页面一直等待，直到短信发送成功后，才开始计时60秒，
        #  用户交互-->美多商城-->发送短信-->响应结果 + 倒计时， 其中发送的短信是一个耗时操作。
        #  所以，应该做异步处理，把相应结果+倒计时解耦出来，展示给用户应该是先计时，增强用户体验
        # 异步函数.delay()
        ccp_send_sms_code(mobile, sms_code)
        # 4.响应结果
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
        return http.HttpResponse(image, content_type='img.jpg')
