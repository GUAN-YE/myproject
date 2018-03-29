# coding: utf-8
from django.conf.urls import include, url, patterns

# 班级
urlpatterns = patterns('apps.class.views',
                       (r'^province$', 'p_province'),  # 省份接口
                       (r'^cities$', 'p_cities'),  # 地市接口
                       (r'^counties$', 'p_counties'),  # 县区接口
                       (r'^schools$', 'p_schools'),  # 学校接口
                       (r'^departments$', 'p_departments'),  # 部门接口
                       (r'^join$', 'p_join'),  # 加入班级接口
                       (r'^quit$', 'p_quit'),  # 退出班级接口

                       (r'^getpwd$', 'p_getpwd'),  # 提示帐号密码
                       (r'^sendpwd$', 'p_sendpwd'),  # 发送帐号密码
                       (r'^byphone$', 'p_byphone'),  # 按老师手机号查班级
                       (r'^sendsms$', 'p_sendsms'),  # 发送班级短信

                       (r'^student/add$', 'p_add_student'),  # 添加学生接口
                       (r'^student/update$', 'p_update_student'),  # 修改班级学生信息
                       (r'^student/remove$', 'p_remove_student'),  # 移除学生

                       (r'^students$', 'p_students'),  # 班级学生列表
                       (r'^studentsNum$', 'p_students_num'),  # 分班级班级学生人数
                       (r'^teachers$', 'p_teachers'),  # 班级所有教师信息
)

