# celery 配置文件
# celery生产者生产任务 --redis中间人存储任务消息队列 --celery消费者执行任务
# 如果使用 redis 作为中间人
# 需要这样配置:
broker_url='redis://192.168.80.129:6379/3'