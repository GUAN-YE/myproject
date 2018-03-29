# coding: utf-8
from django.conf.urls import include, url, patterns

# 登录
urlpatterns = patterns('apps.account.login',
                       (r'^login/(?P<role>[s|t])$', 'p_login'),
                       (r"^vcode$", "p_vcode"),  # 发送验证码
                       (r"^findpwd$", "p_findpwd"),  # 发送帐号密码
                       (r"^register/student$", "p_register_student"),  # 注册学生帐号
                       (r"^register$", "p_register"),  # 注册帐号
                       (r"^feedback$", "p_feedback"),  # 意见反馈
                       (r'^get_token', 'get_token'),  # 验证账号得到，token值
                       (r'^login/web', 'phone_login'),  # 用手机号登录
                       (r'^logininfo', 'logininfo'),  # 记录用户登录信息
                       )

# 个人设置
urlpatterns += patterns('apps.account.profile',
                        (r'^profile$', 'p_profile'),  # 个人数据
                        (r'^units$', 'p_units'),  # 用户班级
                        (r'^name$', 'p_name'),  # 修改姓名
                        (r'^sex$', 'p_sex'),  # 修改性别
                        (r"^portrait$", "p_portrait"),  # 修改头像
                        (r"^border/status$", "p_border_status"),  # 边框状态是否开启
                        (r"^border/list$", "p_border"),  # 获取边框里列表
                        (r"^border/change$", "p_change_border"),  # 修改边框
                        (r"^password$", "p_password"),  # 修改密码
                        (r"^grade$", "p_grade"),  # 设置教师当前年级
                        (r"^accounts$", "p_accounts"),  # 获得本手机号绑定的所有帐号
                        (r"^switch$", "p_switch"),  # 切换账户
                        (r"^book$", "p_book"),  # 获取当前学科教材/教辅
                        (r"^uploadurl$", "p_uploadurl"),  # 获取上传文件地址(兼容老版本)
                        (r"^third$", "p_third"),  # qg用户开通信息
                        (r"^third/open$", "p_third_open"),  # qg用户开通
                        (r"^third/qg_tiyan$", "p_qg_tiyan"),  # qg用户体验
                        )

# 业务
urlpatterns += patterns('apps.account.business',
                        (r'^unopen_count$', 'p_unopen_count'),  # 教师班级下未开通人数
                        (r'^addtask_count$', 'p_addtask_count'),  # 教师发布作业次数
                        )

# 短信
urlpatterns += patterns('apps.account.sms',
                        (r'^sendmany$', 'p_sendmany'),  # 发多条
                        (r'^cancelsms$', 'p_cancel'),  # 取消定时短信
                        )

#
urlpatterns += patterns('apps.account.other_open',
                        (r'^other/subject/qg/open/info', 'qg_info'),  # 开通
                        (r'^other/subject/qg/tiyan/day', 'qg_tiyan_day'),  # 体验剩余时间
                        )
urlpatterns += patterns('apps.account.test_error',
                        (r'^test_error', 'test_error'),            # 测试代码 test_error
)