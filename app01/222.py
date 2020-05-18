# -*- coding: utf-8 -*-
import subprocess
import time
import os
root_dir = r'/root/研究院项目管理/'
"""
ls  /root/研究院项目管理 检查是否以KY和YY开头, 是的话存到遍历列表中
cd 遍历列表，依次打开
ls 存入列表中，找到周报
cd 周报
ls 存入列表中
获取当前时间，拼接文件名
KY2019001_i-stack智慧城市操作系统(二期) ->  12周报  ->  i-stackV2项目周报20190111.docx
项目名：
"""
total_list = {}


def start():
    ret = my_shell(r"ls -al  /root/研究院项目管理/")
    pro_list = []  # 项目目录
    if ret != -1:
        str_list = ret.split('\n')
        for str in str_list:
            list = str.split(' ')
            if list[-1].startswith('KY') or list[-1].startswith('YY'):
                name = root_dir + list[-1].strip('\n')
                if '(' in name and ')' in name:
                    name = name.replace('(', r'\(')
                    name = name.replace(')', r'\)')
                pro_list.append(os.path.join(name))
        print("项目目录读取完毕:\n", pro_list)
        print('==='*20)

        for pro in pro_list:
            # 生成字典的key加到total_list中
            temp_list = []
            total_list[pro] = []
            ret = my_shell(r'ls ' + pro + r'/12周报')
            print('<>>>>>>>>>>>>>>',ret)
            if ret != -1:
                week_list = ret.split(' ')
                for week in week_list:
                    if week != '':
                        temp_list.append(week)
            total_list[pro] = temp_list
        print("生成项目字典完毕：\n", total_list)
        print('===' * 20)

        for pro in pro_list:
            ret = my_shell(r'ls ' + pro + r'/12周报')
            if ret != -1:
                week_list = ret.split(' ')
                for week in week_list:
                    if week != '':
                        temp_list.append(week)
        print("周报目录读取完毕:\n", total_list)
        print('===' * 20)
    else:
        print('打开研究院错误')




# ll命令查看返回list
def ll_list(dir):
    order = 'ls -al '+dir
    print("ORDER_________________", order)
    ret = my_shell(order)
    pro_list = []
    if ret != -1:
        str_list = ret.split('\n')
        for str in str_list:
            list = str.split(' ')
            if list[-1].startswith('KY') or list[-1].startswith('YY'):
                name = root_dir+list[-1].strip('\n')
                pro_list.append(name)
        return pro_list
    else:
        return -1


# 自定义shell命令
def my_shell(cmd):
    obj = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout = obj.stdout.read()
    stderr = obj.stderr.read()
    # print('err:   ', stderr.decode(encoding='utf-8', errors='strict'))
    # print('out:   ', stdout.decode(encoding='utf-8', errors='strict'))
    if stderr:
        return -1
    else:
        return stdout.decode(encoding='utf-8', errors='strict')


if __name__ == '__main__':
    start()
