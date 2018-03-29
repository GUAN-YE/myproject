# coding: utf-8
from django.conf.urls import include, url, patterns

# 消息中心
urlpatterns = patterns('apps.im.views',
    (r"^bind_device$", "p_im_bind_device"),             # 绑定个推设备

    (r"^messages$", "p_messages"),                        # 消息列表
    (r"^sendim$", "p_sendim"),                            # 发IM消息
    (r"^sendmessage$", "p_sendmessage"),                  # 发班级消息
    (r"^update_task_status$", "p_update_task_status"),    # 更新用户作业消息完成状态
    (r"^delmessage$", "p_delmessage"),                    # 取消定时作业
    (r"^template$", "p_template"),                        # 通知模版
    (r"^outside/task/send$", "p_outside_task"),           # 发送课外活动作业
    (r"^outside/task/submit$", "p_outside_task_submit"),  # 课外活动提交
    (r"^outside/task/info$", "p_outside_task_info"),      # 课外活动作业详情
    (r"^outside/task/thumb_up$", "p_outside_thumb_up"),   # 课外活动点赞
)