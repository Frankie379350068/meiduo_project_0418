# celery的入口文件(类似于manage.py)
from celery import Celery
# 创建实例，名字随意
celery_app = Celery('meiduo')

# 加载配置文件名为config的配置文件，类似于settings.py
celery_app.config_from_object('celery_tasks.config')

# 注册异步任务, 任务包的名字
celery_app.autodiscover_tasks(['celery_tasks.sms'])