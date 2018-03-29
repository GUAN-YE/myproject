# coding: utf-8
import time

from apps.common import com_sys
from apps.common.com_user import need_teacher
from apps.im.common import get_student_ids
from libs.utils import tbktapi, ajax, join, db


def p_givesms(request):
    """
    老板语文 作业短信接口
    :param request: 
    :return: 
    """
    args = request.QUERY.casts(classes='json', content=unicode, begin_time='datetime')
    classes = args.classes or []
    content = args.content or u''
    begin_time = args.begin_time

    if not classes:
        return ajax.jsonp_fail(request, message='请选择您要发布的班级')

    content = content.strip()
    if not content:
        return ajax.jsonp_fail(request, message='短信内容不能为空')

    if len(content) > 200:
        return ajax.jsonp_fail(request, message='短信内容不能超过200字')

    unit_ids = []
    user_ids = []
    for i in classes:
        unit_id = str(i.get('unit_id'))
        if unit_id in unit_ids:
            continue
        unit_ids.append(unit_id)
        bind_ids = i.get('bind_id', '')
        user_ids += [str(i) for i in bind_ids.split(',') if i]

    hub = tbktapi.Hub(request)
    url = '/sms/send'
    if unit_ids and not user_ids:
        user_ids += get_student_ids(unit_ids)

    args = dict(user_id=join(user_ids))
    r = hub.sms.post(url, args)

    if not r:
        return ajax.jsonp_fail(request, message='服务器开小差')

    com_sys.send_im(user_ids, 2, '新作业', '你的老师布置作业了,快来看看吧!', {'type': 1})
    return ajax.jsonp_ok(request, r.data)


@need_teacher
def p_check_num(request):
    """
        @api {post} /task/checkNum [作业]待检查作业条数
        @apiGroup  task
        @apiSuccessExample {json} 成功返回
            {"message": "", "error": "",
               "data": {
                    "num": 1, 待检查作业条数
                },
              "response": "ok", "next": ""}
        @apiSuccessExample {json} 失败返回
            {"message": "", "error": "", "data": "", "response": "fail", "next": ""}
        """
    user = request.user
    units = user.units
    uid = [u.id for u in units]
    sid = user.subject_id
    table_name = {
        21: ('shuxue_slave', 'sx_task', 'sx_task_class', 'and t.type in (1,2,4,5,6)'),
        51: ('yuwen_slave', 'yw_task_new', 'yw_task_class_new', ''),
        91: ('yy_slave', 'yy_task', 'yy_task_class', 'and t.type in (1,4)')
    }

    if not uid or sid not in table_name.keys():
        return ajax.jsonp_ok(request, {'num': 0})
    table = table_name[sid]

    sql = """
      select count(1) num from %s t join %s c on t.id=c.task_id where t.status in (0,1,2)   %s
      and t.end_time<=%s   and t.begin_time<=%s  and c.unit_class_id in (%s) and c.status in (0,1,2) and t.add_user=%s
    """ % (table[1], table[2], table[3], int(time.time()),int(time.time()), ','.join(str(i) for i in uid), user.id)
    row = db.__getattr__(table[0]).fetchone_dict(sql)
    num = row.num if row else 0
    return ajax.jsonp_ok(request, {'num': num})
