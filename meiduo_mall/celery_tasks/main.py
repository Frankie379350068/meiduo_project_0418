# celery的入口文件(类似于manage.py)
from celery import Celery
# 特别提醒(极易报错点)： 如果自定义的celery异步任务用到了settings配置文件，
# 则在创建实例之前，把Django的配置文件加载到celery运行环境中
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建实例，名字随意
celery_app = Celery('meiduo')
# 加载配置文件名为config的配置文件，类似于settings.py
celery_app.config_from_object('celery_tasks.config')
# 注册异步任务, 任务包的名字
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
