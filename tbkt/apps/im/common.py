# coding: utf-8
import inspect
import json
import time
import itertools

import re

import logging

import math

import datetime

from apps.common import com_user
from libs.utils import db, from_unixtime, get_absurl, tbktapi, join, Struct, pinyin_abb
from libs.utils.thread_pool import call


def bind_device(user, device_type_id, client_id):
    """
    绑定用户设备
    ---------------------
    王晨光    2017-2-24
    ---------------------
    :param user: 用户
    :param device_type_id: 设备类型表ID (tbkt_web.gt_device_type)
    :param client_id: 客户端ID
    :return: (设备ID, 启动次数)
    """
    nowt = int(time.time())
    # 原则: 一个用户只有一个绑定记录
    device = db.slave.gt_device.get(user_id=user.id)
    if device:
        db.default.gt_device.filter(id=device.id).update(
            start_num=device.start_num + 1,
            update_time=nowt,
            device_type_id=device_type_id,
            client_id=client_id
        )
        return device.id, device.start_num + 1
    else:
        device_id = db.default.gt_device.create(
            ignore=True,
            device_type_id=device_type_id,
            client_id=client_id,
            user_id=user.id,
            start_num=1,
            update_time=nowt,
        )
        return device_id, 1


def get_teacher_messages(user, sids, types, page, psize):
    """
    获取教师消息列表
    --------------------
    王晨光     2017-6-7
    --------------------
    :param user: User
    :param sids: [学科ID], 空是全部消息
    :param types: [消息类型], 空是全部消息
    :param page: 页号
    :param psize: 每页条数
    :return: [消息], 总数
    """
    units = user.units
    unit_ids = [u.id for u in units]
    if not unit_ids:
        return [], 0
    unit_ids_s = ','.join(str(i) for i in unit_ids)
    unitd = {u.id: u for u in units}
    type_cond = ""
    if types:
        type_cond = "and m.type in (%s)" % ','.join(str(i) for i in types)
    subject_cond = ""
    nowt = int(time.time())
    if sids:
        subject_cond = "and m.subject_id in (%s)" % ','.join(str(i) for i in sids)
    sql = """
    select m.id, m.type, m.subject_id, m.object_id, m.add_user, m.title, m.content, 
        m.add_time, group_concat(c.unit_class_id) unit_ids, m.images
    from message m
    inner join message_class c on c.message_id=m.id and c.unit_class_id in (%s)
    where m.status=1 and m.begin_time <= %s and m.add_user=%s %s %s
    group by m.begin_time desc
    limit %s, %s
    """ % (unit_ids_s, nowt, user.id, subject_cond, type_cond, (page - 1) * psize, psize)
    messages = db.slave.fetchall_dict(sql)
    for m in messages:
        if m.type == 1 and m.images:
            # 格式化图片
            m.images = map(lambda x: get_absurl(x), json.loads(m.images))
        else:
            m.images = []
        class_ids = m.pop('unit_ids', '')
        class_ids = [int(i) for i in class_ids.split(',') if i]
        classes = []
        for i in class_ids:
            unit = unitd.get(i)
            if unit:
                classes.append({'id': unit.id, 'name': unit.name})
        m.units = classes
        m.add_time = from_unixtime(m.add_time)
    # 计算总数
    sql = """
    select count(distinct m.id) n
    from message m
    inner join message_class c on c.message_id=m.id and c.unit_class_id in (%s)
    where m.status=1 and m.begin_time <= %s and m.add_user=%s %s %s
    """ % (unit_ids_s, nowt, user.id, subject_cond, type_cond)
    row = db.slave.fetchone(sql)
    total = row[0] if row else 0

    return messages, total


def get_task_status(user_id, subject_id, task_ids):
    """
    获得作业完成情况
    :param user_id: 用户ID
    :param subject_id: 学科ID
    :param task_ids: [作业ID]
    :return: {作业ID: status}
    """
    tasks = []
    if subject_id == 21:
        # 小学数学用户测试
        tasks = db.shuxue_slave.sx_task_test.select('task_id', 'if(status=1,1,2) status').filter(
            user_id=user_id, task_id__in=task_ids).group_by('user_id', 'task_id')[:]

    if subject_id == 22:
        # 初中数学用户测试
        tasks = db.shuxue_slave.sx2_task_test.select('task_id', 'if(status=1,1,2) status').filter(
            user_id=user_id, task_id__in=task_ids).group_by('user_id', 'task_id')[:]

    if subject_id == 91:
        # 小学英语用户测试
        tasks = db.yy_slave.yy_task_progress.select('task_id', 'status').filter(
            user_id=user_id, task_id__in=task_ids).group_by('user_id', 'task_id')[:]

    if subject_id == 92:
        # 初中英语用户测试
        tasks = db.yy_slave.yy2_test.select('object_id task_id', 'status').filter(
            user_id=user_id, object_id__in=task_ids, type=5).group_by('user_id', 'object_id', 'type')[:]

    if subject_id == 51:
        tasks = db.yuwen.yw_test_new.select('task_id', 'status').filter(
            user_id=user_id, task_id__in=task_ids).group_by('user_id', 'task_id')[:]

    return {r.task_id: r.status for r in tasks}


def get_student_messages(user, sids, types, page, psize):
    """
    获取学生消息列表
    --------------------
    王晨光     2017-6-7
    --------------------
    :param user: User
    :param sids: [学科ID]
    :param types: [消息类型], 空是全部消息
    :param page: 页号
    :param psize: 每页条数
    :return: [消息], 总数
    """
    unit = user.unit
    if not unit:
        return [], 0
    type_cond = ""
    if types:
        type_cond = "and m.type in (%s)" % ','.join(str(i) for i in types)
    subject_cond = ""
    if sids:
        subject_cond = "and m.subject_id in (%s)" % ','.join(str(i) for i in sids)
    nowt = int(time.time())
    sql = """
    select m.id, m.type, m.subject_id, m.object_id, m.add_user, m.title, m.content, 
        m.add_time, m.end_time endtime, m.images, m.begin_time
    from message m
    inner join message_class c on c.message_id=m.id and c.unit_class_id=%s and (c.student_ids='' or c.student_ids like '%%|%s|%%')
    where m.status=1 AND m.begin_time <= %s %s %s
    order by m.begin_time desc,m.add_time desc, m.object_id desc
    limit %s, %s
    """ % (unit.id, user.id, nowt, subject_cond, type_cond, (page - 1) * psize, psize)
    messages = db.slave.fetchall_dict(sql)
    for m in messages:
        if m.type == 1 and m.images:
            # 格式化图片
            m.images = map(lambda x: get_absurl(x), json.loads(m.images))
        else:
            m.images = []
        m.units = [{'id': unit.id, 'name': unit.name}]
        m.add_time = from_unixtime(m.add_time)
        m.end_time = from_unixtime(m.endtime)
        m.begin_time = from_unixtime(m.begin_time)

        m.is_active = 0

    # 补充完成状态
    task_messages = [m for m in messages if m.type in (2, 7, 8, 9, 101)]
    groups = itertools.groupby(task_messages, lambda x: x.subject_id)
    status_d = {}
    for subject_id, msgs in groups:
        task_ids = [m.object_id for m in msgs]
        d = get_task_status(user.id, subject_id, task_ids)
        for task_id, status in d.items():
            status_d[(subject_id, task_id)] = status

    msg_ids = [m.id for m in messages if m.type == 10]
    outside_status = get_outside_task_status(user.id, msg_ids)

    for m in messages:
        if m.type == 10:
            # 判断课外作业状态
            m.test_status = 1 if m.id in outside_status else 0
            if int(time.time()) > m.endtime:
                # 如果用户没有提交， 到结束时间用户将不能提交
                m.test_status = 1
        else:
            test_status = status_d.get((m.subject_id, m.object_id)) or 0
            if test_status != 1 and int(time.time()) > m.endtime:
                test_status = 3
            m.test_status = test_status

    # 计算总数
    sql = """
    select count(distinct m.id) n
    from message m
    inner join message_class c on c.message_id=m.id and c.unit_class_id=%s and (c.student_ids='' or c.student_ids like '%%|%s|%%')
    where m.status=1 and m.begin_time <= %s %s %s
    """ % (unit.id, user.id, nowt, subject_cond, type_cond)
    row = db.slave.fetchone(sql)
    total = row[0] if row else 0

    return messages, total


def get_user_messages(user, sids, types, page, psize):
    """
    获取用户消息列表
    --------------------
    王晨光     2017-6-7
    --------------------
    :param user: User
    :param sids: [学科ID]
    :param types: [消息类型], 空是全部消息
    :param page: 页号
    :param psize: 每页条数
    :return: [{
        "id": 消息ID,
        "type": 消息类型,
        "subject_id": 两位数学科ID,
        "object_id": 业务表ID,
        "add_user": 老师ID,
        "title": 标题,
        "content": 内容(240个字以内),
        "add_time": "2017-06-07 11:18:00" # 发布时间
    }], 总数
    """
    types = [i for i in types if i > 0]
    if user.is_teacher:
        return get_teacher_messages(user, sids, types, page, psize)
    return get_student_messages(user, sids, types, page, psize)


def get_student_ids(user, unit_ids):
    """
    获得班级下所有学生ID
    ---------------------
    王晨光     2017-4-21
    ---------------------
    :param unit_ids: [班级ID]
    :return: [学生ID]
    """
    if not unit_ids:
        return []

    return user.get_mobile_order_region().filter(user_type=1, unit_class_id__in=unit_ids).select('user_id').flat(
        'user_id')[:]


def send_class_message(user, unit_ids, student_ids, type, object_id, title, content, images, begin_time, end_time):
    """
    发送班级消息
    ---------------------
    王晨光     2017-6-7
    ---------------------
    :param user: 发布者User
    :param unit_ids: [班级ID]
    :param student_ids: [指定学生ID]
    :param type: 消息类型
    :param object_id: 业务表ID
    :param title: 标题
    :param images: 通知图片
    :param content: 内容
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :return: 消息ID
    """
    if not unit_ids:
        return
    if student_ids:
        regions = user.get_mobile_order_region().filter(unit_class_id__in=unit_ids, user_type=1).select(
            'unit_class_id', 'user_id')[:]
    else:
        regions = []
    student_id_set = set(student_ids)
    nowt = int(time.time())
    images = json.dumps(images) if images else ''
    # status = 2 if begin_time > nowt else 1
    with db.default as c:
        message_id = c.message.create(
            type=type,
            subject_id=user.subject_id,
            object_id=object_id,
            add_user=user.id,
            title=title,
            content=content,
            status=1,
            images=images,
            add_time=nowt,
            end_time=end_time,
            begin_time=begin_time,
        )
        details = []
        stu_id_list = []
        for unit_id in unit_ids:
            stu_ids = []
            for r in regions:
                if r.unit_class_id == unit_id:
                    stu_ids.append(r.user_id)
            stu_ids_s = ''
            stu_ids = [sid for sid in student_id_set if sid in stu_ids]
            stu_id_list += stu_ids
            if stu_ids:
                stu_ids_s = '|' + '|'.join(str(i) for i in stu_ids) + '|'
            d = {'message_id': message_id, 'unit_class_id': unit_id, 'student_ids': stu_ids_s}
            details.append(d)
        c.message_class.bulk_create(details)
        call(message_send_sms, unit_ids, stu_id_list, content, user.platform_id)
        if type == 10:
            if user.subject_id == 21:
                create_sx_task(user.id, message_id, title, content, nowt, end_time, begin_time, unit_ids)
            if user.subject_id == 91:
                create_yy_task(user.id, message_id, title, content, nowt, end_time, begin_time, unit_ids)
            if user.subject_id == 51:
                create_yw_task(user.id, message_id, title, content, nowt, end_time, begin_time, unit_ids)
        return message_id


def get_outside_task_status(user_id, message_ids):
    """
    获取课外作业状态
    :param user_id: 
    :param message_ids: 
    :return: 
    """
    data = db.default.outside_task_test.select("message_id").\
        filter(user_id=user_id, message_id__in=message_ids).flat("message_id")[:]
    return data


def filter_word(message):
    def func(m):
        z = m.group()
        return u'*' * len(z)

    r = u"""十九大|19大|毛泽东|邓小平|江泽民|胡锦涛|习近平|李洪志|李克强|
    |张德江|俞正声|刘云山|王岐山|张高丽|师傅|套牌车|开盘|热线|抢购|中共中央|娇嫩欲滴|
    |三陪|六合彩|分裂|教徒|迫害|搞日|马会|枪支|办证|套牌|公关|黑车|人权|公证局|公安|
    |地税局|登记|抽奖|语音|代款|将军|情感|特价|优惠|折扣|葳独|特色|限量|
    |激情|民航|平方|平米|机票|信用卡|中奖|基地|开盘|订金|金融|首付|
    |组织|红旗|政策|百万|世界|会员|促销|大礼|优惠|开业|限量|法轮功|赌博|反共|麻将|彩票|
    |发票|台独|增值税"""
    a = re.compile(r)
    try:
        message = message.decode('utf-8')
    except:
        pass
    return a.sub(func, message)


def message_send_sms(unit_ids, stu_ids, content, platform_id):
    """
    发送短信
    :param unit_ids: 
    :param stu_ids: 
    :param content: 
    :param platform_id: 
    :return: 
    """
    try:
        hub = tbktapi.Hub()
        d = {
           'unit_id': join(unit_ids),
           'user_id': join(stu_ids),
           'content': content,
           'platform_id': platform_id
        }
        hub.sms.post('/sms/send', d)
    except Exception as e:
        logging.error("send msg ERROR %s:%s" % (inspect.stack()[0][3], e))


def outside_task_submit(message_id, user_id, content, type, media_url):
    """
    学生课外作业提交
    :param message_id: message pk 
    :param user_id:    用户id
    :param content:    学生活动体验描述
    :param type:       提交类型  1.图片 2.音频 3.视频
    :param media_url:  type对应文件url
    :return: 
    """
    with db.default as c:
        msg = c.message.get(id=message_id)
        if not msg:
            return 0
        now = int(time.time())

        test_id = c.outside_task_test.create(
            user_id=user_id,
            message_id=message_id,
            status=1,
            content=content,
            type=type,
            media_url=json.dumps(media_url),
            add_time=now
        )
        return test_id


def outside_task_info(user, message_id, unit_id):
    """
    获取课外活动作业详情
    :param user: 
    :param message_id: 
    :param unit_id: 
    :return: 
    """
    sql = """
    select m.id, m.content, m.title, m.begin_time, m.end_time endtime, m.add_user user_id, images from message m 
    inner join message_class c on m.id = c.message_id
    where m.id = %s and c.unit_class_id = %s;
    """ % (message_id, unit_id)
    msg = db.slave.fetchone_dict(sql)
    if not msg:
        return
    now = int(time.time())

    if msg.endtime <= now:
        # 更新教师端检查作业状态
        call(update_outside_status, user, msg.id, unit_id)

    time_sub = now - int(msg.begin_time)
    msg.begin_time = from_unixtime(msg.begin_time) if time_sub >= 24*60*60 else change_time(time_sub)
    msg.end_time = from_unixtime(msg.endtime)
    msg.is_upload = 1
    if not msg.images:
        msg.figure_images = []
        msg.images = []
    else:
        images = is_empty(map(lambda x: format_outside_url(x, is_figure=False), json.loads(msg.images)))
        msg.figure_images = is_empty(
            map(lambda x: format_outside_url(x, is_figure=True), json.loads(msg.images)))
        msg.images = images

    stu_ids = user.get_mobile_order_region().select('user_id').\
        filter(unit_class_id=unit_id, user_type=1).flat("user_id")[:]

    stu_tests = db.slave.outside_task_test.filter(user_id__in=stu_ids, message_id=message_id).\
        select("user_id", "media_url", "type", "content", "thumb_up", "add_time").order_by("-thumb_up", "add_time")[:]

    stu_tests_map = {i.user_id: i for i in stu_tests}

    if user.is_teacher:
        msg.user_name = user.real_name
        msg.portrait = user.portrait
    else:
        tea_user = com_user.get_user(msg.user_id)
        msg.user_name = tea_user.real_name
        msg.portrait = tea_user.portrait
        msg.status = 0
        if user.id in stu_tests_map or msg.endtime <= now:
            msg.status = 1

    userd = com_user.get_users(stu_ids)

    msg.finish = []
    msg.unfinish = []
    for user_id, stu_user in userd.iteritems():
        stu_test = stu_tests_map.get(user_id)
        if not stu_test:
            d = dict(
                real_name=stu_user.real_name,
                portrait=stu_user.portrait
            )
            msg.unfinish.append(d)
            continue

        media_url = is_empty(json.loads(stu_test.media_url))
        if not media_url:
            stu_test.figure_url = []
            stu_test.media_url = []
        else:
            stu_test.media_url = map(lambda x: format_outside_url(x), media_url)
            if stu_test.type == 1:
                stu_test.figure_url = map(lambda x: format_outside_url(x, is_figure=True), media_url)

        stu_test.user_name = stu_user.real_name
        stu_test.add_time = from_unixtime(stu_test.add_time)
        stu_test.portrait = stu_user.portrait
        msg.finish.append(stu_test)
    msg.finish.sort(key=lambda m: (-m.thumb_up, m.add_time))
    return msg


def format_outside_url(url, is_figure=False):
    """
    课外活动media走cnd节点    
    """
    if not url:
        return ''
    if url.startswith("http"):
        return url
    cdn_domain = "http://kwhd.m.xueceping.cn"
    if is_figure:
        old_name = url.split("/")[-1]
        new_name = "small_"+url.split("/")[-1]
        url = url.replace(old_name, new_name)
    return "%s/upload_media/%s" % (cdn_domain, url)


def is_empty(media_urls):
    """
    判断课外活动media_url字段是否为空
    :param media_urls: 
    :return: 
    """
    return [i for i in media_urls if i]


def outside_thumb_up(stu_user_id, message_id):
    """
    教师课外作业点赞
    :param stu_user_id: 
    :param message_id: 
    :return: 
    """
    db.default.outside_task_test.filter(user_id=stu_user_id, status=1, message_id=message_id).update(thumb_up=1)


def change_time(temp_time):
    """
    时间戳相减获取中文时间节点
    :param temp_time: 
    :return: 
    """
    day = 24 * 60 * 60
    hour = 60 * 60
    sec = 60
    if temp_time < 60:
        return "%d秒前" % math.ceil(temp_time)
    elif temp_time > day:
        days = divmod(temp_time, day)
        return "%d天前" % (int(days[0]))
    elif temp_time > hour:
        hours = divmod(temp_time, hour)
        return '%d小时前' % int(hours[0])
    else:
        mins = divmod(temp_time, sec)
        return "%d分钟前" % (int(mins[0]))


def create_sx_task(user_id, message_id, title, content, add_time, end_time, begin_time, unit_ids):
    """
    将课外活动写入数学库
    :param user_id:     教师id
    :param message_id:  tbkt_com.message pk
    :param title:       作业标题
    :param content:     作业描述
    :param add_time:    添加时间
    :param end_time:    结束时间
    :param begin_time:  开始时间
    :param unit_ids:    发送班级id
    :return: 
    """
    with db.shuxue as dt:
        task_id = dt.sx_task.create(
            add_user=user_id,
            type=6,
            status=1,
            add_time=add_time,
            begin_time=begin_time,
            end_time=end_time,
            sms_content=content,
            title=title,
            object_id=message_id
        )
        args = []
        for i in unit_ids:
            d = dict(
                task_id=task_id,
                unit_class_id=i,
                status=1
            )
            args.append(d)
        if args:
            dt.sx_task_class.bulk_create(args)


def create_yw_task(user_id, message_id, title, content, add_time, end_time, begin_time, unit_ids):
    """
    将课外活动作业写入语文库
    :param user_id:     教师id
    :param message_id:  tbkt_com.message pk
    :param title:       作业标题
    :param content:     作业描述
    :param add_time:    添加时间
    :param end_time:    结束时间
    :param begin_time:  开始时间
    :param unit_ids:    发送班级id
    :return: 
    """
    with db.yuwen as dy:
        task_id = dy.yw_task_new.create(
            add_user=user_id,
            chapter_id=0,
            type=4,
            status=1,
            add_time=add_time,
            begin_time=begin_time,
            end_time=end_time,
            title=content,
            object_id=message_id
        )
        args = []
        for i in unit_ids:
            d = dict(
                task_id=task_id,
                unit_class_id=i,
                status=1
            )
            args.append(d)
        if args:
            dy.yw_task_class_new.bulk_create(args)


def create_yy_task(user_id, message_id, title, content, add_time, end_time, begin_time, unit_ids):
    """
    将课外活动作业写入英语库
    :param user_id:     教师id
    :param message_id:  tbkt_com.message pk
    :param title:       作业标题
    :param content:     作业描述
    :param add_time:    添加时间
    :param end_time:    结束时间
    :param begin_time:  开始时间
    :param unit_ids:    发送班级id
    :return: 
    """
    with db.yy as dy:
        task_id = dy.yy_task.create(
            type=4,
            object_id=message_id,
            add_user=user_id,
            title=title,
            status=1,
            add_time=add_time,
            sms_content=content,
            begin_time=begin_time,
            end_time=end_time
        )
        args = []
        for i in unit_ids:
            d = dict(
                task_id=task_id,
                unit_class_id=i,
                status=1
            )
            args.append(d)
        if args:
            dy.yy_task_class.bulk_create(args)


def update_outside_status(user, message_id, unit_id):
    """
    到结束时间后更新课外活动 
    检查作业状态
    ——————————————————————
    王世成       2018-02-07
    
    :param user: 
    :param message_id:
    :param unit_id: 
    :return: 
    """
    if not user and message_id:
        return
    
    if not user.is_teacher:
        return 
    
    if user.subject_id == 21:
        task = db.shuxue.sx_task.get(add_user=user.id, type=6, object_id=message_id)
        if task:
            db.shuxue.sx_task_class.filter(task_id=task.id, unit_class_id=unit_id).update(status=4)

    if user.subject_id == 51:
        task = db.yuwen.yw_task_new.get(add_user=user.id, type=4, object_id=message_id)
        if task:
            db.yuwen.yw_task_class_new.filter(task_id=task.id, unit_class_id=unit_id).update(status=4)

    if user.subject_id == 91:
        task = db.yy.yy_task.get(add_user=user.id, type=4, object_id=message_id)
        if task:
            db.yy.yy_task_class.filter(task_id=task.id, unit_class_id=unit_id).update(status=4)




def filter_word_flag(message):
    """判断是否含有敏感词汇"""
    r = u"""习近平|彭丽媛|李克强|普渡众生|救渡世人|杀戮|李洪志|假新闻|方励之|学生运动|六.四六四|
    中共高层|北京当局|血洗|强奸|两会|新一届|国家领导人|人大代表|政协委员|党专制|贪恋权力|倒行逆施|
    军权膨胀|公投|谪系人马|江泽民|胡锦涛|温家宝|曾庆红|军委主席|流氓政权|禽流感|吾尔开希|血吸虫|
    保钓活动|自焚|民主自由|性伴侣|东海天然气|公开信|爆炸|紫陽|祸国殃民|专制政权|讲真相|追悼会|001工程|
    扩大台湾农产品|包机|福建戒毒所|康晓光|康小光|权威主义|保钓|希望之声|九&评|退党|抵制日货|游行|滕兴善|
    陆建华|陈晖|张戎|不为人知的故事|The Unknown Story|芙蓉姐姐|焦国标|讨伐中宣部|窝囊的中国|哈工大女博士|
    平可夫|总统号|瓦良格|萨拉托加|明斯克号|福莱斯特|航空母舰|太石村|银行卡诈骗|三峡移民|移民|杜湘成|滕兴善|
    癌症村|拉法叶舰|拉案|陈光诚|维权|绝食抗议|反垄断法|天药|系统神学|许万平|郑茂清|新股发行|中天行公司|国统会|
    十七大前后的中国|中国丈夫毛泽东的情事|胡温面临的地雷阵|内部日记|十二个春秋|邓力群|未来自由中国在民间|颐和园|
    刘志华生活腐败|保钓行动|上海合作组织|朝令夕改|高考移民|高考舞弊|取款风波|出国考察|高考泄题|姬鹏飞|西藏边防|
    武装冲突|戴松林疑案|高莺莺死亡案件|湘阴群体事件|法＆轮|湘潭韶山|杨长军天安门广场自残事件|无线针孔摄象机|
    无线针孔摄象机看字专用针孔摄像机|隐形无线耳机|暗访摄像包|台湾进口纽扣式超清晰针孔摄像机|汽车反测速雷达|迷魂药|迷奸药|
    瘙痒药吃了后就全身痒想脱光衣服的|三唑伦|仿五四枪/狙击枪|军用炸药|六合彩/买码|完全自杀手册|陈良宇|裸之秀|核电站|力霸|
    宏观调控|人大主任|国家药监局|尼日利亚|绑架|双规|境外并购|美国副国务卿|陈水扁过境美国|招待费耗资3700亿|高家伟|
    安徽农民工子弟学校|刘胡兰|乡亲铡刀|缅甸问题|杭州湾跨海大桥|摧毁旧卫星|医生状告医院|开单提成|大连建厂|中国反卫星武器|
    辽宁两会|衡阳中院工作报告|衡阳中院|中院工作报告|衡阳中院|衡阳中级人民法院|查禁八本图书|长株潭‘申特’不受重庆成都影响|
    三峡旅游资源被垄断|浏阳河水出现异味|威海政府掀"全民募捐"浪潮|山西黑砖窑|北大一教授被辞退致信教育部部长陈情|取消利息税|
    郑筱萸案件|体协原副主席宋万年|汉唐证券|辽宁海城二台子社区|中国石化集团公司高层人事变动|安徽高考文科统分|2008奥运性感泳装|
    加强网上群体性事件信息管理|物价上涨|高校罢课|高校罢餐|超级&信使|人权圣火|同样的世界，同样的人权|人权圣火之歌|事纪神|呼喊派|
    门徒会|统一教|观音法门|中功|菩提功|民运|藏独|示威|西藏&独立|集会|游行|喇嘛&抗议|拉萨&抗议|哲蚌寺|甘丹寺|藏族&独立|拉萨&戒严|
    西藏&暴乱|五一&游行|高校&游行|抵制家乐福|交行|账 号|招行|超?级短信|超级?短信|超?级信使|抵制家乐福|抵制法货|游行|西藏&起义|
    达赖&抗议|色拉寺|法国&游行|51&游行|超级信使|超 级 信使|超级 信使|裸体|法轮功|法&轮|轮&工&力|明&慧&网|法&輪|超科学|共匪|
    功德圆满|九评讲播|邪灵|上天在警告世人|同化宇宙|萬&古&事&為&法&來|万&古&事&為&法&來|讲&真&相&民&谣|讲&真&相&诗&歌|
    突&破&网&络&封&锁|滴&滴&血&泪&唤&君&醒|坦&荡&正&法&路|江氏一只黑手|康妮·契普卡|法&轮&转&动|天安门自焚|正念|
    用&真&像&打&破&禁&锢|法&囵|漠&视&人&权&施&独&裁|洗&脑&酷&刑|溶心法理|freenet-china.org|www.dajiyuan.com.cn|
    briefcase.yahoo.com|breakit.batcave.net|bbs.ievista.com|lookatme0.tripod.ca|www.geocities.com|baishishi|
    twfgm.no-ip.com|noblock.no-ip.com|www.dajiyuan.com|xiaopin.zapto.org|donghua.zapto.org|nolie.redirectme.net|
    mzc.zapto.org|gui.hopto.org|spr.hopto.org|freenet-china.org|www.minghui|www.minghui.org|24.83.220.95|www.xys2.org|
    101.redirectme.net|belong.zapto.org|elite.zapto.org|fresh.hopto.org|spring.bounceme.net|twfgm.no-ip.com|zapto.org|
    X泽民|x泽民|江core|江xx|江核心|江氏|反攻大陆|反共|天安门事件|射精|性交|阴道|阴茎|野鸡|口交|鸡巴|勃起|一夜情|鸡奸|江卖国|江贼民|
    sy01.nhua.org|www.downdown.net|www.111shop.com|zhina444.allhere.com|zhina444.xrs.net|gau12.amxy.com|dd21.kaxb.com|
    qxbbs.homeftp.net|uw.slyip.com|207.44.142.89|Web3.km120.com|h119.ath.cx|转&法&轮|法轮佛法|国家恐怖主义|24.87.30.178|
    江氏集团|江家班|江黑心|党魁|dadaobao.myetang.com|sy01.nhua.org|祝春林|马英泽|大纪元|卖淫|生化袭击|婊子|新闻封锁|大面积爆发|
    屠城|反宇宙的力量|庸医|台湾特工|一手操控|生化武器|政府黑暗|隐瞒疫情|安全投毒|封城|隐瞒数据|生物武器|骚货|江系人马|重疫区|消息封锁|
    瘟疫|nu18.com|万&古&事&为&法&来|精液|阴唇|阴蒂|淫邪|龟头|xxboy.net|www.hellocd.com|www6.kinghost.com|www.boybbs.net|
    pointsmoney.com|中国农民调查|韩桂芝|刘杰告状信|逊克农场26队|红顶商人|杀人奶粉|慰问信|瀑布沟|经租房|丁子霖|生者与死者|清水君|
    杨建利|王炳章|movie.yygov.com|交媾|刘晓竹|中宣部是中国社会的艾滋病|民运分子|新闻管制|舆论钳制|乱伦|轮奸|做爱|loveroot|suck|
    dick|shit|fuck|妓女|退脏帐号|退脏不咎|嘉禾事件|绿色台商|张玉凤&毛泽东|张万钧|www.in-wa.com|www.500movies.com|www.hhslut.com|
    www.hkgirlz.com|www.taiwanmovie.com|www.pussyasians.com|证券&巨资|蒋彦永|中国铁路&签名|爱国者同盟|love21cn|正邪大决战|
    救度世人|迷昏药|迷魂药|河南&艾滋病|黑龙江&干部|新唐人电视|权贵私有化|炮轰中国教育部|废除劳教签名活动|跨世纪的良心犯|汉风|克劳塞维茨|
    赵&紫&阳|大紀元|趙&紫&陽|www.12488.com|www.90550.com|29t.com|两性视频|情色电影|尤甘斯克|六四屠城|ftp.xinhone.com|
    u1.tengotech.com|w8.sullyhome.net|ming.got-game.org|王斌余|市长自杀|木塔里甫|玉素甫|库尔勒市长|超级信使|二手汽车|
    超级信使|性幻想|偷拍|婚外恋|情色|艳照|露点|一夜情|婚外情|两性|隐私|腐败中国|三个呆婊|社会主义灭亡|打倒中国|打倒共产党|
    打倒共产主义|打倒胡锦涛|打倒江泽民|打倒江主席|打倒李鹏|打倒罗干|打倒温家宝|打倒中共|打倒朱镕|抵制共产党|抵制共产主义|
    抵制胡锦涛|抵制江泽民|抵制江主席|抵制李鹏|抵制罗干|抵制温家宝|抵制中共|抵制朱镕基|灭亡中国|亡党亡国|粉碎四人帮|激流中国|
    特供|特贡|特共|zf大楼|殃视|贪污腐败|强制拆除|形式主义|政治风波|太子党|上海帮|北京帮|清华帮|红色贵族|权贵集团|河蟹社会|
    喝血社会|九风|9风|十七大|十7大|十九大|17da|九学|9学|四风|4风|双规|南街村|最淫官员|警匪|官匪|独夫民贼|官商勾结|城管暴力执法|
    强制捐款|毒豺|一党执政|一党专制|一党专政|专制政权|宪法法院|胡平|苏晓康|贺卫方|谭作人|焦国标|万润南|张志新|辛灝年|高勤荣|王炳章|
    高智晟|司马璐|刘晓竹|刘宾雁|魏京生|寻找林昭的灵魂|别梦成灰|谁是新中国|讨伐中宣部|异议人士|民运人士|启蒙派|选国家主席|民一主|
    min主|民竹|民珠|民猪|chinesedemocracy|大赦国际|国际特赦|da选|投公|公头|宪政|平反|党章|维权|昝爱宗|宪章|08宪|08xz|抿主|
    敏主|人拳|人木又|人quan|renquan|中国人权|中国新民党|群体事件|群体性事件|上中央|去中央|讨说法|请愿|请命|公开信|联名上书|
    万人大签名|万人骚动|截访|上访|shangfang|信访|访民|集合|集会|组织集体|静坐|静zuo|jing坐|示威|示wei|游行|you行|油行|
    游xing|youxing|官逼民反|反party|反共|抗议|亢议|抵制|低制|底制|di制|抵zhi|dizhi|boycott|血书|焚烧中国国旗|baoluan|
    流血冲突|出现暴动|发生暴动|引起暴动|baodong|灭共|杀毙|罢工|霸工|罢考|罢餐|霸餐|罢参|罢饭|罢吃|罢食|罢课|罢ke|霸课|ba课|
    罢教|罢学|罢运|网特|网评员|网络评论员|五毛党|五毛们|5毛党|戒严|jieyan|jie严|戒yan|8的平方事件|知道64|八九年|贰拾年|2o年|
    20和谐年|贰拾周年|六四|六河蟹四|六百度四|六和谐四|陆四|陆肆|198964|5月35|89年春夏之交|64惨案|64时期|64运动|4事件|四事件|
    北京风波|学潮|学chao|xuechao|学百度潮|门安天|天按门|坦克压大学生|民主女神|历史的伤口|高自联|北高联|血洗京城|四二六社论|王丹|
    柴玲|沈彤|封从德|王超华|王维林|吾尔开希|吾尔开西|侯德健|阎明复|方励之|蒋捷连|丁子霖|辛灏年|蒋彦永|严家其|陈一咨|中华局域网|党的喉舌|
    互联网审查|当局严密封锁|新闻封锁|封锁消息|爱国者同盟|关闭所有论坛|网络封锁|金盾工程|无界浏览|无界网络|自由门|何清涟|中国的陷阱|汪兆钧|
    记者无疆界|境外媒体|维基百科|纽约时报|bbc中文网|华盛顿邮报|世界日报|东森新闻网|东森电视|星岛日报|wikipedia|美国广播公司|英国金融时报|
    自由亚洲|自由时报|中国时报|反分裂|威胁论|左翼联盟|钓鱼岛|保钓组织|主权|弓单|火乍|木仓|石肖|核蛋|步qiang|bao炸|爆zha|baozha|zha药|
    zha弹|炸dan|炸yao|zhadan|zhayao|hmtd|三硝基甲苯|六氟化铀|炸药配方|弹药配方|炸弹配方|皮箱炸弹|火药配方|人体炸弹|人肉炸弹|解放军|
    兵力部署|军转|军事社|8341部队|第21集团军|七大军区|7大军区|北京军区|沈阳军区|济南军区|成都军区|广州军区|南京军区|兰州军区|颜色革命|
    规模冲突|塔利班|基地组织|恐怖分子|恐怖份子|三股势力|印尼屠华|印尼事件|蒋公纪念歌|马英九|mayingjiu|李天羽|苏贞昌|林文漪|陈水扁|陈s扁|
    陈随便|阿扁|a扁|告全国同胞书|台百度湾|台完|台wan|taiwan|台弯|湾台|台湾国|台湾共和国|台军|台独|台毒|台du|taidu|twdl|一中一台|打台湾|
    两岸战争|攻占台湾|支持台湾|进攻台湾|占领台湾|统一台湾|收复台湾|登陆台湾|解放台湾|解放tw|解决台湾|光复民国|台湾独立|台湾问题|台海问题|
    台海危机|台海统一|台海大战|台海战争|台海局势|入联|入耳关|中华联邦|国民党|x民党|民进党|青天白日|闹独立|duli|fenlie|日本万岁|小泽一郎|
    劣等民族|汉人|汉维|维汉|维吾|吾尔|热比娅|伊力哈木|疆独|东突厥斯坦解放组织|东突解放组织|蒙古分裂分子|列确|阿旺晋美|藏人|臧人|zang人|藏民|
    藏m|达赖|赖达|dalai|哒赖|dl喇嘛|丹增嘉措|打砸抢|西独|藏独|葬独|臧独|藏毒|藏du|zangdu|支持zd|藏暴乱|藏青会|雪山狮子旗|拉萨|啦萨|啦沙|
    啦撒|拉sa|lasa|la萨|西藏|藏西|藏春阁|藏獨|藏独|藏独立|藏妇会|藏青会|藏字石|xizang|xi藏|x藏|西z|tibet|希葬|希藏|硒藏|稀藏|西脏|西奘|
    西葬|西臧|援藏|bjork|王千源|安拉|回教|回族|回回|回民|穆斯林|穆罕穆德|穆罕默德|默罕默德|伊斯兰|圣战组织|清真|清zhen|qingzhen|真主|阿拉伯|
    高丽棒子|韩国狗|满洲第三帝国|满狗|鞑子|江丑闻|江嫡系|江毒|江独裁|江蛤蟆|江核心|江黑心|江胡内斗|江祸心|江家帮|江绵恒|江派和胡派|江派人马|
    江泉集团|江人马|江三条腿|江氏集团|江氏家族|江氏政治局|江氏政治委员|江梳头|江太上|江戏子|江系人|江系人马|江宰民|江贼|江贼民|江主席|麻果丸|
    麻将透|麻醉弹|麻醉狗|麻醉枪|麻醉槍|麻醉药|麻醉藥|台独|台湾版假币|台湾独立|台湾国|台湾应该独立|台湾有权独立|天灭中共|中共帮凶|中共保命|
    中共裁|中共党文化|中共腐败|中共的血旗|中共的罪恶|中共帝国|中共独裁|中共封锁|中共封网|中共腐败|中共黑|中共黑帮|中共解体|中共近期权力斗争|
    中共恐惧|中共权力斗争|中共任用|中共退党|中共洗脑|中共邪教|中共邪毒素|中共政治游戏|爱女人|爱液|按摩棒|拔出来|爆草|包二奶|暴干|暴奸|暴乳|
    爆乳|暴淫|屄|被操|被插|被干|逼奸|仓井空|插暴|操逼|操黑|操烂|肏你|肏死|操死|操我|厕奴|插比|插b|插逼|插进|插你|插我|插阴|潮吹|潮喷|成人dv|
    成人电影|成人论坛|成人小说|成人电|成人电影|成人卡通|成人聊|成人片|成人视|成人图|成人文|成人小|成人电影|成人论坛|成人色情|成人网站|成人文学|
    成人小说|艳情小说|成人游戏|吃精|赤裸|抽插|扌由插|抽一插|春药|大波|大力抽送|大乳|荡妇|荡女|盗撮|多人轮|发浪|放尿|肥逼|粉穴|封面女郎|
    风月大陆|干死你|干穴|肛交|肛门|龟头|裹本|国产av|好嫩|豪乳|黑逼|后庭|后穴|虎骑|花花公子|换妻俱乐部|黄片|几吧|鸡吧|鸡巴|鸡奸|寂寞男|
    寂寞女|妓女|激情|集体淫|奸情|叫床|脚交|金鳞岂是池中物|金麟岂是池中物|精液|就去日|巨屌|菊花洞|菊门|巨奶|巨乳|菊穴|开苞|口爆|口活|口交|
    口射|口淫|裤袜|狂操|狂插|浪逼|浪妇|浪叫|浪女|狼友|聊性|流淫|铃木麻|凌辱|漏乳|露b|乱交|乱伦|轮暴|轮操|轮奸|裸陪|买春|美逼|美少妇|美乳|
    美腿|美穴|美幼|秘唇|迷奸|密穴|蜜穴|蜜液|摸奶|摸胸|母奸|奈美|奶子|男奴|内射|嫩逼|嫩女|嫩穴|捏弄|女优|炮友|砲友|喷精|屁眼|品香堂|前凸后翘|
    强jian|强暴|强奸处女|情趣用品|情色|拳交|全裸|群交|惹火身材|人妻|人兽|日逼|日烂|肉棒|肉逼|肉唇|肉洞|肉缝|肉棍|肉茎|肉具|揉乳|肉穴|肉欲|
    乳爆|乳房|乳沟|乳交|乳头|三级片|骚逼|骚比|骚女|骚水|骚穴|色逼|色界|色猫|色盟|色情网站|色区|色色|色诱|色欲|色b|少年阿宾|少修正|射爽|射颜|
    食精|释欲|兽奸|兽交|手淫|兽欲|熟妇|熟母|熟女|爽片|爽死我了|双臀|死逼|丝袜|丝诱|松岛枫|酥痒|汤加丽|套弄|体奸|体位|舔脚|舔阴|调教|偷欢|
    偷拍|推油|脱内裤|文做|我就色|无码|舞女|无修正|吸精|夏川纯|相奸|小逼|校鸡|小穴|小xue|写真|性感妖娆|性感诱惑|性虎|性饥渴|性技巧|性交|
    性奴|性虐|性息|性欲|胸推|穴口|学生妹|穴图|亚情|颜射|阳具|杨思敏|要射了|夜勤病栋|一本道|一夜欢|一夜情|一ye情|阴部|淫虫|阴唇|淫荡|
    阴道|淫电影|阴阜|淫妇|淫河|阴核|阴户|淫贱|淫叫|淫教师|阴茎|阴精|淫浪|淫媚|淫糜|淫魔|淫母|淫女|淫虐|淫妻|淫情|淫色|淫声浪语|淫兽学园|
    淫书|淫术炼金士|淫水|淫娃|淫威|淫亵|淫样|淫液|淫照|阴b|应召|幼交|幼男|幼女|欲火|欲女|玉女心经|玉蒲团|玉乳|欲仙欲死|玉穴|援交|原味内衣|
    援助交际|张筱雨|招鸡|招妓|中年美妇|抓胸|自拍|自慰|作爱|18禁|99bb|a4u|a4y|adult|amateur|anal|a片|fuck|gay片|g点|g片|hardcore|
    h动画|h动漫|incest|porn|secom|sexinsex|sm女王|xiao77|xing伴侣|tokyohot|yin荡|贱人|装b|大sb|傻逼|傻b|煞逼|煞笔|刹笔|傻比|
    沙比|欠干|婊子养的|我日你|我操|我草|卧艹|卧槽|爆你菊|艹你|cao你|你他妈|真他妈|别他吗|草你吗|草你丫|操你妈|擦你妈|操你娘|操他妈|
    日你妈|干你妈|干你娘|娘西皮|狗操|狗草|狗杂种|狗日的|操你祖宗|操你全家|操你大爷|妈逼|你麻痹|麻痹的|妈了个逼|马勒|狗娘养|贱比|贱b|
    下贱|死全家|全家死光|全家不得好死|全家死绝|白痴|无耻|sb|杀b|你吗b|你妈的|婊子|贱货|人渣|混蛋|媚外|和弦|兼职|限量|铃声|性伴侣|
    男公关|火辣|精子|射精|诱奸|强奸|做爱|性爱|发生关系|按摩|快感|处男|猛男|少妇|屌|屁股|下体|a片|内裤|浑圆|咪咪|发情|刺激|白嫩|
    粉嫩|兽性|风骚|呻吟|sm|阉割|高潮|裸露|不穿|一丝不挂|脱光|干你|干死|我干|裙中性运动|乱奸|乱伦|乱伦类|乱伦小|伦理大|伦理电影|
    伦理毛|伦理片|裸聊|裸聊网|裸体写真|裸舞视|裸照|美女裸体|美女写真|美女上门|美艳少妇|妹按摩|妹上门|迷幻药|迷幻藥|迷昏口|迷昏药|
    迷昏藥|迷魂香|迷魂药|迷魂藥|迷奸粉|迷奸药|迷情粉|迷情水|迷情药|迷药|迷藥|谜奸药|骚妇|骚货|骚浪|骚女|骚嘴|色电影|色妹妹|色情表演|
    色情电影|色情服务|色情图片|色情小说|色情影片|色情表演|色情电影|色情服务|色情片|色视频|色小说|性伴侣|性服务|性福情|性感少|性伙伴|
    性交|性交视频|性交图片|性奴|性奴集中营|性虐|阴唇|阴道|阴蒂|阴户|阴间来电|阴茎|阴茎增大|阴茎助勃|阴毛|陰唇|陰道|陰戶|淫荡|淫荡美女|
    淫荡视频|淫荡照片|淫乱|淫靡|淫魔|淫魔舞|淫女|淫情女|淫肉|淫騷妹|淫兽|淫兽学|淫水|淫穴|morphine|摇头丸|迷药|乖乖粉|narcotic|
    麻醉药|精神药品|爱女人|爱液|按摩棒|拔出来|爆草|包二奶|暴干|暴奸|暴乳|爆乳|暴淫|屄|被操|被插|被干|逼奸|仓井空|插暴|操逼|操黑|操烂|
    肏你|肏死|操死|操我|厕奴|插比|插b|插逼|插进|插你|插我|插阴|潮吹|潮喷|成人电影|成人论坛|成人色情|成人网站|成人文学|成人小说|艳情小说|
    成人游戏|吃精|赤裸|抽插|扌由插|抽一插|春药|大波|大力抽送|大乳|荡妇|荡女|盗撮|多人轮|发浪|放尿|肥逼|粉穴|封面女郎|风月大陆|干死你|干穴|
    肛交|肛门|龟头|裹本|国产av|好嫩|豪乳|黑逼|后庭|后穴|虎骑|花花公子|换妻俱乐部|黄片|几吧|鸡吧|鸡巴|鸡奸|寂寞男|寂寞女|妓女|激情|
    集体淫|奸情|叫床|脚交|金鳞岂是池中物|金麟岂是池中物|精液|就去日|巨屌|菊花洞|菊门|巨奶|巨乳|菊穴|开苞|口爆|口活|口交|口射|口淫|
    裤袜|狂操|狂插|浪逼|浪妇|浪叫|浪女|狼友|聊性|流淫|铃木麻|凌辱|漏乳|露b|乱交|乱伦|轮暴|轮操|轮奸|裸陪|买春|美逼|美少妇|美乳|美腿|
    美穴|美幼|秘唇|迷奸|密穴|蜜穴|蜜液|摸奶|摸胸|母奸|奈美|奶子|男奴|内射|嫩逼|嫩女|嫩穴|捏弄|女优|炮友|砲友|喷精|屁眼|品香堂|前凸后翘|
    强jian|强暴|强奸处女|情趣用品|情色|拳交|全裸|群交|惹火身材|人妻|人兽|日逼|日烂|肉棒|肉逼|肉唇|肉洞|肉缝|肉棍|肉茎|肉具|揉乳|肉穴|
    肉欲|乳爆|乳房|乳沟|乳交|乳头|三级片|骚逼|骚比|骚女|骚水|骚穴|色逼|色界|色猫|色盟|色情网站|色区|色色|色诱|色欲|色b|少年阿宾|少修正|
    射爽|射颜|食精|释欲|兽奸|兽交|手淫|兽欲|熟妇|熟母|熟女|爽片|爽死我了|双臀|死逼|丝袜|丝诱|松岛枫|酥痒|汤加丽|套弄|体奸|体位|舔脚|
    舔阴|调教|偷欢|偷拍|推油|脱内裤|文做|我就色|无码|舞女|无修正|吸精|夏川纯|相奸|小逼|校鸡|小穴|小xue|写真|性感妖娆|性感诱惑|性虎|
    性饥渴|性技巧|性交|性奴|性虐|性息|性欲|胸推|穴口|学生妹|穴图|亚情|颜射|阳具|杨思敏|要射了|夜勤病栋|一本道|一夜欢|一夜情|一ye情|
    阴部|淫虫|阴唇|淫荡|阴道|淫电影|阴阜|淫妇|淫河|阴核|阴户|淫贱|淫叫|淫教师|阴茎|阴精|淫浪|淫媚|淫糜|淫魔|淫母|淫女|淫虐|淫妻|淫情|
    淫色|淫声浪语|淫兽学园|淫书|淫术炼金士|淫水|淫娃|淫威|淫亵|淫样|淫液|淫照|阴b|应召|幼交|幼男|幼女|欲火|欲女|玉女心经|玉蒲团|玉乳|
    欲仙欲死|玉穴|援交|原味内衣|援助交际|张筱雨|招鸡|招妓|中年美妇|抓胸|自拍|自慰|作爱|18禁|99bb|a4u|a4y|adult|amateur|anal|a片|
    fuck|gay片|g点|g片|hardcore|h动画|h动漫|incest|porn|secom|sexinsex|sm女王| xiao77|xing伴侣|tokyohot|yin荡"""
    if isinstance(message, unicode):
        return re.search(r, message)
    else:
        message = message.decode('utf-8')
        return re.search(r, message)
