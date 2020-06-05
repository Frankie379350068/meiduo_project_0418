# 定义生产任务
# celery 的任务自己管理，所以要重新把yuntongxun的包放入sms下
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.ccp_sms import CCP

@celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(mobile, sms_code):
    ret = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    return ret