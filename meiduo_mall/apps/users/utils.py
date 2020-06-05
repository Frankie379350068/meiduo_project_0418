import logging

from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

logger = logging.getLogger('django')

def generate_verify_email_url(user):
    # 1.创建序列化器
    s = Serializer(settings.SECRET_KEY, 24*3600)
    # 2. 选择要加密的数据, {}类型
    data = {'email':user.email}
    # 3. 数据的序列化及解码
    token = s.dumps(data).decode()
    # 4. 拼接链接地址url
    url = settings.EMAIL_VERIFY_URL + token
    # 5. 返回拼接的url
    return url



def check_verify_email_url():
    pass
