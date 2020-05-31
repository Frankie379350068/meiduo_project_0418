from django.shortcuts import render
from django.views import View
from django import http
from apps.users.models import User
import logging
# Create your views here.
logger = logging.getLogger('django')

class UsernameCountView(View):
    def get(self, request, username):
        # 查询username在数据库中的个数
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})

