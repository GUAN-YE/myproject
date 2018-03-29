# coding: utf-8
"""消息相关接口"""
import time

import datetime

from libs.utils import db, ajax, ajax_try
from apps.common import com_user, com_sys
from . import common


@ajax_try({})
@com_user.need_login
def p_im_bind_device(request):
    """
    @api {get} /im/bind_device [IM]绑定设备
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"device_type_id":设备类型ID, "client_id":"3a74a30f6849fef1f6c86188440e2768"}

        *设备类型ID: 1安卓学生 2安卓教师 3苹果学生 4苹果教师
        *client_id: 个推sdk分配的一个字符串, 用来代表一个唯一的手机
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "start_num": 1,  # 启动次数
            "device_id": 2   # 设备ID
        },
        "response": "ok",
        "error": ""
    }

    透传参数:
    {"type": 1作业类消息 2奥数类消息}
    """
    args = request.QUERY.casts(device_type_id=int, client_id=str)
    device_type_id = args.device_type_id
    client_id = args.client_id

    if not client_id:
        return ajax.jsonp_fail(request, message="缺少参数: client_id")

    user = request.user
    device_id, start_num = common.bind_device(user, device_type_id, client_id)
    data = {
        "device_id": device_id,
        "start_num": start_num,
    }
    return ajax.jsonp_ok(request, data)


@ajax_try({"message":[]})
@com_user.need_login
def p_messages(request):
    """
    @api {get} /im/messages [IM]消息列表
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"p":页号, "psize":每页条数, "subject_id":学科ID(多个用逗号分割), "type":类型(多个用逗号分割)}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "total": 10, # 总条数
            "messages": [{
                "id": 消息ID,
                "type": 消息类型(多个类型用逗号分割),
                "subject_id": 两位数学科ID,
                "object_id": 业务表ID,
                "add_user": 老师ID,
                "title": 标题,
                "content": 内容(240个字以内),
                "units": [{id:班级ID, name:班级名}],  # 接收消息的班级
                "add_time": "2017-06-07 11:18:00", # 发布时间
                "test_status": 0未做 1已完成 2继续做题,
                "images":[图片url,图片url] 
            }]
        },
        "response": "ok",
        "error": ""
    }

    *消息类型:
    空是全部消息 1:sms短信 2:task作业 3:shared资源推送 
    4:think奥数视频 5:jx_video本周视频 6:jx_paper本周试卷  7:数学试卷作业 8 知识点视频作业  9 速算作业
    
    *object_id:
    if type == 2: object_id表示各个学科的作业表ID, 比如sx_task.id, yy_task.id
        if subject_id == 21: 调小学数学作业信息接口(http://mapisx.m.jxtbkt.cn/s/math/task/info)
        if subject_id == 22: 调初中数学作业信息接口(http://mapisx2.m.jxtbkt.cn/s/math/task/info)
        if subject_id == 91: 调小学英语作业接口(http://mapiyy.m.jxtbkt.com/s/task/detail_list)
        if subject_id == 92: 目前没有初中英语
    if type == 3: object_id表示共享资源推送表(shared_push)的ID
    if type == 4: object_id表示奥数章节ID, 用来调取奥数视频
        调小学数学奥数视频接口 http://mapisx.m.jxtbkt.com/s/math/resource/think
    if type == 5: object_id表示教学进度详情ID, 用来调取本周视频
        调小学数学本周视频接口 http://mapisx.m.jxtbkt.com/s/math/resource/video
    if type == 6: object_id表示练习册章节ID, 用来调取试卷题目
        调小学数学教辅章节试卷接口 http://mapisx.m.jxtbkt.cn/sx/pcatalog_paper
    """
    user = request.user
    args = request.QUERY.casts(subject_id=str, type=str, p=int, psize=int)
    subject_ids = args.subject_id
    subject_ids = [int(s) for s in subject_ids.split(',') if s]
    sids = []
    for i in subject_ids:
        if i < 10:
            sids.append(i*10+user.dept_type)
        else:
            sids.append(i)
    types = args.type
    types = [int(s) for s in types.split(',') if s]
    page = max(1, args.p)
    psize = args.psize or 20
    messages, total = common.get_user_messages(user, sids, types, page, psize)
    data = {
        'messages': messages,
        'total': total,
    }
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_teacher
def p_sendim(request):
    """
    @api {post} /im/sendim [IM]发送IM消息
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"unit_id":班级ID(多个班用逗号连接), "user_id":发送给个人(多个用户ID用逗号连接),
         "config_id":配置ID, "title": 消息标题, "content": 消息内容
        }

        *配置ID: 1Demo 2APP学生 3APP教师
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": "",
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(unit_id=str, user_id=str, config_id=int, title=unicode, content=unicode, type=int)
    if not args.unit_id and not args.user_id:
        return ajax.jsonp_fail(request, message='缺少参数: unit_id|user_id')
    if not args.config_id:
        return ajax.jsonp_fail(request, message='缺少参数: config_id')
    if args.config_id not in (1, 2, 3):
        return ajax.jsonp_fail(request, message='参数不合法: config_id')
    if not args.title:
        return ajax.jsonp_fail(request, message='缺少参数: title')
    if not args.content:
        return ajax.jsonp_fail(request, message='缺少参数: content')
    if len(args.content) > 240:
        return ajax.jsonp_fail(request, message='消息内容过长')

    im_type = args.type or 1

    unit_ids = [int(i) for i in args.unit_id.split(',') if i]
    unit_ids = [i for i in unit_ids if i>0]

    user_ids = [int(i) for i in args.user_id.split(',') if i]
    user_ids = [i for i in user_ids if i>0]

    config_id = args.config_id
    title = args.title
    content = args.content

    if unit_ids:
       user_ids += common.get_student_ids(request.user,unit_ids)
    com_sys.send_im(user_ids, config_id, title, content, {'type': im_type})
    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_teacher
def p_sendmessage(request):
    """
    @api {post} /im/sendmessage [IM]发送普通消息
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"unit_id":班级ID(多个班用逗号连接), "student_id":指定发给某几个学生ID(可选,逗号连接)
         "type": 消息类型, "object_id":业务表ID, 
         "title": 消息标题, "content": 消息内容, "end_time": 作业短信，完成时间, "begin_time": 发作业时间,
         "images":["url", "url"]通知图片(可选)
        }

        *type:
        1、sms短信 2、task作业 3、shared资源推送 
        4、think奥数视频 5、jx_video本周视频 6、jx_paper本周试卷, 7.数学试卷作业 8.速算作业 9.知识点作业
        
        如果type = 1 
        可以只传 type, unit_id, student_id, content, images 
        
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "message_id": 5  # 新消息的ID
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(unit_id=str, student_id=str, type=int, object_id=int, title=unicode, content=unicode,
                               end_time=int, begin_time=int, images='json')
    type = args.type
    if not args.type:
        return ajax.jsonp_fail(request, message='缺少参数: type')

    if type not in (1, 2, 3, 4, 5, 6, 7):
        return ajax.jsonp_fail(request, message='参数不合法: type')

    if not args.unit_id:
        return ajax.jsonp_fail(request, message='缺少参数: unit_id')

    if type != 1 and not args.title:
        return ajax.jsonp_fail(request, message='缺少参数: title')

    if type != 1 and not args.content:
        return ajax.jsonp_fail(request, message='缺少参数: content')

    if len(args.content) > 240:
        return ajax.jsonp_fail(request, message='消息内容过长')

    if type != 1 and not args.begin_time:
        return ajax.jsonp_fail(request, message='缺少参数: end_time')

    if type == 1 and not args.content and not args.images:
        return ajax.jsonp_fail(request, message='发通知缺少参数: images or content')

    if common.filter_word_flag(args.content):
        return ajax.jsonp_fail(request, message='发送失败，该短信内容中包含敏感词！')

    user = request.user
    unit_ids = [int(i) for i in args.unit_id.split(',') if i]
    unit_ids = [i for i in unit_ids if i > 0]
    student_ids = [int(s) for s in args.student_id.split(',') if s]
    now = int(time.time())
    images = args.images or []
    object_id = args.object_id
    title = args.title
    if type == 1:
        title = "%s通知" % time.strftime("%m月%d日", time.gmtime(now))
    content = common.filter_word(args.content) or u"这是%s老师下发的%s张图片" % (user.real_name, len(images))
    end_time = args.end_time or now
    begin_time = args.begin_time or now
    my_unit_ids = [u.id for u in user.units]

    if not my_unit_ids:
        return ajax.jsonp_fail(request, message='请先加入班级')

    unit_ids = list(set(unit_ids) & set(my_unit_ids))
    if not unit_ids:
        return ajax.jsonp_fail(request, message='班级ID不属于当前班级')

    message_id = common.send_class_message(user, unit_ids, student_ids, type, object_id, title, content, images,
                                           begin_time, end_time)
    data = {
        'message_id': message_id
    }
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_login
def p_update_task_status(request):
    """
    @api {post} /im/update_task_status [IM]更新作业消息完成状态
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"subject_id":学科ID, "task_id":作业ID, "status":状态(1完成 2继续做题)}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
        },
        "response": "ok",
        "error": ""
    }
    """
    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_delmessage(request):
    """
    @api {post} /im/delmessage [IM]取消定时作业
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {"subject_id":学科ID, "task_id":作业ID,"type":作业类型}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(subject_id=int, task_id=int, type=int)
    subject_id = int(args.subject_id)
    task_id = int(args.task_id)
    type = int(args.type)
    db.default.message.filter(object_id=task_id, subject_id=subject_id, type=type, status=1).update(status=-1)
    return ajax.jsonp_ok(request)


@ajax_try("")
def p_template(request):
    """
    @api {post} /im/template [IM]通知模版
    @apiGroup IM
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": [
            "请同学们回家后看第x页，第x题的难题视频讲解，并完成拓展练习",
            "请同学们完成第x可是的拓展练习，扫描拓展练习的二维码就可以观看了",
            "请同学们看第x课时的错题视频讲解，并订正错题，扫描错题二维码就可以观看了"
        ],
        "response": "ok",
        "error": ""
    }
    """
    data = [u"请同学们看第x课时的错题视频讲解，并订正错题，扫描错题二维码就可以观看了",
            u"请同学们完成第x课时的拓展练习，扫描拓展练习的二维码就可以观看了",
            u"请同学们回家后看第x页，第x题的难题视频讲解，并完成拓展练习"]
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_teacher
def p_outside_task(request):
    """
    @api {post} /im/outside/task/send [IM]课外活动-发送作业
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {
            "content":活动描述文字, 
            "end_time":结束时间,   
            "images":活动描述图片, ["image url", "image url"]
            "unit_id":班级id,     "班级id,班级id,班级id"
            "type":作业类型,       1.创意手工 2.做家务 3.自定义
        }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "message_id": 1
        },
        "response": "ok",
        "error": ""
    }
    
    @apiSuccessExample {json} 失败返回
    {
        "message": "活动描述不能为空",
        "next": "",
        "data": "",
        "response": "fail",
        "error": ""
    }
    
    """
    args = request.QUERY.casts(content=unicode, end_time=unicode, images='json', unit_id=str, type=int)
    content = args.content
    end_time = args.end_time
    images = args.images or []
    unit_id = args.unit_id
    typ = args.type
    if not content and not images:
        return ajax.jsonp_fail(request, message='活动描述不能为空')
    if len(content) > 200:
        return ajax.jsonp_fail(request, message="描述不能超过200字")
    if not unit_id:
        return ajax.jsonp_fail(request, message="请选择班级")
    if not end_time:
        return ajax.jsonp_fail(request, message="请选择活动结束时间")
    if not typ:
        return ajax.jsonp_fail(request, message="缺少课外活动作业类型")

    user = request.user

    year = str(datetime.datetime.today().year)
    a = end_time.replace(u"月", "-").replace(u"日", " ").replace(u"时", ":00:00")
    end_time = year + "-" + a
    end_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))

    unit_ids = [int(i) for i in unit_id.split(',') if i and int(i) > 0]
    user_unit_id = [u.id for u in user.units]
    if not user_unit_id:
        return ajax.jsonp_fail(request, message="请先加入班级")

    unit_ids = list(set(unit_ids) & set(user_unit_id))
    if not unit_ids:
        return ajax.jsonp_fail(request, message="所选班级和实际班级不符")

    title = {
        1: u"创意手工",
        2: u"做家务",
        3: u"自定义"
    }.get(typ, u"自定义")

    # 课外活动作业类型
    task_type = 10
    begin_time = int(time.time())
    msg_id = common.send_class_message(user, unit_ids, [], task_type, typ, title, content, images, begin_time, end_time)
    return ajax.jsonp_ok(request, {"message_id": msg_id})


@ajax_try("")
@com_user.need_login
def p_outside_task_submit(request):
    """
    @api {post} /im/outside/task/submit [IM]课外活动-作业提交
    @apiGroup IM
    @apiParamExample {json} 请求示例
        {
            "message_id": 作业id(tbkt_com.message), 
            "type": 1.图片 2.音频 3.视频,    
            "content": 活动描述文字,
            "url": type=1.图片url type=2.音频url type=3.视频url
        }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "test_id": 1
        },
        "response": "ok",
        "error": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "缺少参数",
        "next": "",
        "data": "",
        "response": "fail",
        "error": ""
    }
    
    """
    args = request.QUERY.casts(message_id=int, type=int, content=unicode, url="json")
    msg_id = args.message_id
    url_type = args.type
    content = args.content
    url = args.url or []
    user_id = request.user_id

    if not msg_id:
        return ajax.jsonp_fail(request, message="找不到这个作业")

    if not url_type:
        return ajax.jsonp_fail(request, message="你要上传什么类型的作业?")

    if not content and (not url or not url[0]):
        return ajax.jsonp_fail(request, message="请输入活动心得 或者 上传内容")

    test_id = common.outside_task_submit(msg_id, user_id, content, url_type, url)
    return ajax.jsonp_ok(request, {"test_id": test_id})


@ajax_try("")
@com_user.need_login
def p_outside_task_info(request):
    """
    @api {post} /im/outside/task/info [IM]课外活动-作业信息
    @apiGroup IM
    @apiParamExample {json} 请求示例
    {
        "message_id": 作业id(tbkt_com.message), 
        "unit_id": 班级id
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "status": 1,   
            "finish": [
                {
                    "thumb_up": 1,
                    "user_id": 608898,
                    "user_name": "小小学生",
                    "content": "测试册数册数侧二次嘎达的萨达撒大声地",
                    "portrait": "http://file.m.xueceping.cn/upload_media/portrait/2017/12/18/2017121817284732843.png",
                    "media_url": [
                        "http://file.m.xueceping.cn/upload_media/portrait/2017/12/18/2017121817284732843.png"
                    ],
                    "type": 1,
                    "add_time": "2018-01-18 17:47:25"
                }
            ],
            "user_id": 3677026,
            "title": "创意手工",
            "unfinish": [
                {
                    "portrait": "http://file.m.xueceping.cn/upload_media/portrait/2017/09/19/20170919103351664562.png",
                    "real_name": "宝马"
                },
                {
                    "portrait": "http://res-hn-beta.m.jxtbkt.cn/user_media/images/profile/default-student.png",
                    "real_name": "刘启明"
                }
            ],
            "content": "创意手工",
            "end_time": "2018-01-19 00:00:00",
            "begin_time": "7小时前",
            "portrait": "http://res-hn-beta.m.jxtbkt.cn/user_media/images/profile/default-teacher.png",
            "user_name": "测试10",
            "id": 100001253
        },
        "response": "ok",
        "error": ""
    }
    * type: 1.图片 2.音频 3.视频
    * 学生类型 status = 1 完成 0 未完成
    @apiSuccessExample {json} 失败返回
    {
        "message": "缺少参数",
        "next": "",
        "data": "",
        "response": "fail",
        "error": ""
    }
    """
    args = request.QUERY.casts(message_id=int, unit_id=int)
    message_id = args.message_id
    unit_id = args.unit_id

    user = request.user
    if not message_id or not unit_id:
        return ajax.jsonp_fail(request, message="缺少参数")

    data = common.outside_task_info(user, message_id, unit_id)
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_login
def p_outside_thumb_up(request):
    """
    @api {post} /im/outside/task/thumb_up [IM]课外活动-点赞
    @apiGroup IM
    @apiParamExample {json} 请求示例
    {
        "message_id": 作业id(tbkt_com.message), 
        "user_id": 作业学生id
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data":"",
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(message_id=int, user_id=int)
    message_id = args.message_id
    user_id = args.user_id
    common.outside_thumb_up(user_id, message_id)
    return ajax.jsonp_ok(request)





