import random
import json

from django.contrib import auth
from django.contrib.auth import logout
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO, StringIO
from django.utils.safestring import mark_safe
from django.db import transaction

from app01 import myforms, models



class UserView():
    pass





def register(request):
    back_dic = {'code': 100, 'msg': ''}
    form_obj = myforms.RegForm()
    if request.method == 'POST':
        # POST就是数据，from会根据key字段验证
        form_obj = myforms.RegForm(request.POST)
        if form_obj.is_valid():
            cleaned_data = form_obj.cleaned_data
            print(cleaned_data)
            cleaned_data.pop("confirm_password")
            # 头像文件对象不POST中，要单独处理
            avatar = request.FILES.get('myfile')
            if avatar:
                cleaned_data['avatar'] = avatar
            # 坑。。。。.create_user不是create，前者才会自动给你加密
            models.UserInfo.objects.create_user(**cleaned_data)
            back_dic['msg'] = '注册新用户成功'
            back_dic['url'] = '/login'
        else:
            back_dic['msg'] = form_obj.errors
            back_dic['code'] = 101
        return JsonResponse(back_dic)
    # print('渲染的html',form_obj)
    return render(request, 'register.html', locals())


def login(request):
    back_dic = {'code': 100, 'msg': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 先校验验证码是否正确  忽略大小写
        # 自动截取cookie中的sessionid，get操作session_data，和session_key无关了
        print('session中的code:', request.session.get('code'))
        if request.session.get('code').upper() == code.upper():
            # 再校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                back_dic['msg'] = '登录成功'
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 101
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 102
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


def loginout(request):
    logout(request)
    return render(request, 'home.html')

# 返回随机三原色
def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# 内存管理器 能够帮你暂时保存对应数据格式的数据
def get_code(request):
    # 能够动态生成图片  如何在图片上写字  写体的样式和大小如何控制
    io_obj = BytesIO()  # 看成是文件对象 f
    img_obj = Image.new('RGB', (310, 35), get_random())
    draw_obj = ImageDraw.Draw(img_obj)  # 生成一个画笔对象 能够在图片上写字
    font_obj = ImageFont.truetype('static/fonts/zp.ttf', 40)
    # 利用ACii表生成随机验证码    大小写英文字母 + 数字
    code = ''
    for i in range(5):
        upper_str = str(chr(random.randint(65, 90)))
        lower_str = str(chr(random.randint(95, 122)))
        random_int = str(random.randint(0, 9))
        temp = random.choice([upper_str, lower_str, random_int])
        draw_obj.text((45 + i * 45, -2), temp, get_random(), font_obj)
        # 记录验证码
        code += temp
    print(code)
    # 缓存code到数据库，取值直接用code关键字就行了
    request.session['code'] = code
    img_obj.save(io_obj, 'png')  # f.write
    return HttpResponse(io_obj.getvalue())


# 展现所有文章
def home(request):
    article_list = models.Article.objects.all()
    return render(request, 'home.html', locals())


# 个人站点  **kwargs个人站点下的分类和标签划分，多个路由公用一个函数
def site(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    username = user_obj.username
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        # 路由下有两个有名分组condition和param
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tag__id=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c',
                                                                                                       'pk')
    # print(category_list)

    # 统计当前用户所对应的标签名及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c', 'pk')

    # 按照年月分组 统计文章数
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(c=Count('pk')).values_list('month', 'c')
    # print(date_list)
    """
id		时间					文章内容	  如何以年月分组需要将年月截取出来单独再作为一个字段
1	    2018-04-24		        111						2018-4
2	    2019-06-24		        111						2019-6
3		2019-05-24		        111                     2019-5
4		2019-05-24		        111                     2019-5
5		2019-01-24		        111                     2019-1

from django.db.models.functions import TruncMonth
    from django.db.models.functions import TruncMonth
			Sales.objects
			.annotate(month=TruncMonth('timestamp'))  # Truncate to month and add to select list
			.values('month')  # Group By month
			.annotate(c=Count('id'))  # Select the count of the grouping
			.values('month', 'c')  # (might be redundant, haven't tested) select month and count
    """

    return render(request, 'site.html', locals())


#  文章详情
def article_detail(request, username, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    blog = article_obj.blog.userinfo.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c',
                                                                                                       'pk')
    print(category_list)

    # 统计当前用户所对应的标签名及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c', 'pk')

    # 按照年月分组 统计文章数
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(c=Count('pk')).values_list('month', 'c')
    print(date_list)
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


def updown(request):
    """
    点赞点踩业务逻辑
        1.先校验用户是否登录
        2.判断用户是否已经点过了
        3.判断当前文章是否是当前用户自己写的
        4.操作数据库 更新数据
    :param request:
    :return:
    """
    back_dic = {'code': 100, 'msg': ''}
    if request.is_ajax():  # 判断当前请求是否是ajax请求
        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')  # js所对应的布尔值的字符串形式
        is_up = json.loads(is_up)  # 转成python对应的布尔值类型
        article_obj = models.Article.objects.filter(pk=article_id).first()
        if request.user.is_authenticated():
            is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
            if not is_click:
                if not article_obj.blog.userinfo.username == request.user.username:
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)

                        back_dic['msg'] = '点踩成功'
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 101
                    back_dic['msg'] = '臭不要脸的!'
            else:
                back_dic['code'] = 102
                back_dic['msg'] = '已经点过了'
        else:
            back_dic['code'] = 103
            back_dic['msg'] = mark_safe('请先<a href="/login/">登录</a>')
        return JsonResponse(back_dic)


def comment(request):
    back_dic = {"code": 100, 'msg': ""}
    if request.is_ajax():
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        parent_id = request.POST.get('parent_id')
        # 开启事务
        with transaction.atomic():
            models.Article.objects.filter(pk=article_id).update(comment_num=F("comment_num") + 1)
            models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                          parent_id=parent_id)
        back_dic['msg'] = '评论成功'
    return JsonResponse(back_dic)


def backend(request):
    return render(request, 'backend/backend.html')
