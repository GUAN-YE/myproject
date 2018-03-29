# coding: utf-8
from apps.common import com_sys
from apps.im.common import get_student_ids
from libs.utils import tbktapi, ajax, join


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
