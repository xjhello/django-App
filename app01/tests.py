from django.db.models import Count
from django.test import TestCase

import os


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BBS.settings")
    import django
    django.setup()
    from app01 import models
    user_obj = models.UserInfo.objects.filter(username='xu123').first()
    # 统计当前用户所对应的分类名及分类下的文章数
    category_list = models.Category.objects.filter(blog=user_obj.blog).annotate(c=Count('article')).values_list('name', 'c',
                                                                                                       'pk')
    # category_list = models.Category.objects.filter(blog=user_obj.blog)
    print(category_list) # <QuerySet [<Category: 分类1>, <Category: 分类2>]>
    # 分类集合拿到后，统计每个分类名和旗下的文章数，就是用到分组
    # category_list.annotate(c=Count('article')).values_list('name', 'c', 'pk')
    # print(category_list)