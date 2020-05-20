"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from BBS import settings
from app01 import views
def return_static(request, path, insecure=True, **kwargs):
  return serve(request, path, insecure, **kwargs)
urlpatterns = [
    url(r'^register/', views.register),
    url(r'^$', views.home),
    url(r'^login/', views.login),
    url(r'^logout/', views.loginout),
    # 图片验证码相关路由
    url(r'^get_code/', views.get_code),
    url(r'^home/', views.home),
    # 静态资源接口,media配置,serve区别其他url，能够访问所有文件，MEDIA_ROOT定义了开放的路径
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', return_static, name='static'),
    # 点赞点踩逻辑
    url(r'^updown/', views.updown),
    # 评论相关
    url(r'^comment/', views.comment),

    # 后台管理
    url(r'^backend/', views.backend),
    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),
    # 个人站点下的按照文章分类，标签，年月来分类文章
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/',views.site),
    # 个人站点路由设计
    url(r'^(?P<username>\w+)/$', views.site),

    url(r'^admin/', admin.site.urls),
]
urlpatterns += staticfiles_urlpatterns()
