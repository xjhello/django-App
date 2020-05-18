from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)  # blank=True告诉django admin该字段可以为空
    create_time = models.DateField(auto_now_add=True)
    # default 默认头像的路径 upload_to需要传一个路径
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png')
    # 跟Blog表一对一
    blog = models.OneToOneField(to='Blog', null=True)

    class Meta:
        verbose_name_plural = '用户表'
        # verbose_name = '用户表'


# 个人站点包含有文章标签，文章分类，文章，个人信息
# 和标签是一对多，和分类是一对多，和文章是一对多，和个人信息是一对一
# 都是作为反向的一方，由其他表来关联关系
class Blog(models.Model):
    site_name = models.CharField(max_length=32)
    site_title = models.CharField(max_length=64)
    # 存css文件的路径
    theme = models.CharField(max_length=32)

    def __str__(self):
        return self.site_name  # 返回的是字符串类型


# 分类包含文章，和个人站点
# 和文章是一对多，由于文章是常用表，所以在反方向
# 和个人站点blog是一对多，相比于个人站点是常用表，所以是正方向
class Category(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.name


# 标签包括文章，个人站点
# 和文章是多对多，文章常用，所以是反方向
# 和个人站点blog是一对多，相比于个人站点是常用表，所以是正方向
class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.name


# 文章包含关系有分类，标签，个人站点，点赞点踩，评论，用户
# 和分类是一对多，正向
# 和标签是多对多，正向，注意自己定义了第三张表，代码中要说明
# 和个人站点是一对多，正向
# 和点赞点踩是一对多，点赞点踩常用，反向
# 和评论是一对多，评论常用，反向
# 和用户是一对一
class Article(models.Model):
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=255)
    # 存大文本
    content = models.TextField()
    create_time = models.DateField(default='2019-01-01')
    # 跟站点表一对多
    blog = models.ForeignKey(to='Blog',null=True)
    # 跟分类一对多
    category = models.ForeignKey(to='Category',null=True)
    # 跟标签多对多,手动创建第三张表
    tag = models.ManyToManyField(to='Tag', through='Article2Tag', through_fields=('article', 'tag'))

    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# 自定义的多对多
class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


# 点赞点踩，包含用户，文章
# 和用户是一对多，正向
# 和文章是一对多，反向
class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()


# 包含用户，文章，父评论
# 和用户是一对多，正方向
# 和文章是一对多，正方向
# 和父评论是一对多
class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=255)
    # 评论时间
    create_time = models.DateTimeField(auto_now_add=True)
    # parent =models.ForeignKey(to='Comment',to_field='nid')
    # 自关联,存父评论id
    parent = models.ForeignKey(to='self',null=True)
    # parent =models.IntegerField()
