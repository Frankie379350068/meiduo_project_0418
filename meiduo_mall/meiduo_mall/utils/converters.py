# 自定义路由转换器


class UsernameConverter:
    regex = '[a-z0-9A-Z_-]{5,20}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
