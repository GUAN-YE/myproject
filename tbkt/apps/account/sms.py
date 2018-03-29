# coding: utf-8
import os
from libs.utils import ajax, is_chinamobile, ajax_try, sms, tbktapi, json, join
from apps.common import com_user


@ajax_try("")
@com_user.need_login
def p_sendmany(request):
    """
    @api {post} /account/sendmany [短信]发多条短信
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"phone":"15981867201,15981867202", "content":"您的验证码是111", "schedule_time":"140415112622"}

        *schedule_time: 可选, 定时发送时间, 如: 140415112622 代表14年04月15日11点26分22秒
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "id": 2787448,  # 短信ID
                "success": true
            },
            "response": "ok",
            "error": ""
        }
    @apiSuccessExample {json} 失败返回
        {
            "message": "请填写短信内容",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    args = request.QUERY.casts(phone=str, content=unicode, schedule_time=str)
    phones = args.phone or ''
    content = args.content or ''
    schedule_time = args.schedule_time or ''
    phones = phones.split(',')
    phones = [s for s in phones if is_chinamobile(s)]
    if not phones:
        return ajax.jsonp_fail(request, message='请输入移动手机号')
    if not content:
        return ajax.jsonp_fail(request, message='请填写短信内容')

    hub = tbktapi.Hub(request)
    url = '/sms/send'
    d = dict(phone=join(phones), content=content, schedule_time=schedule_time,platform_id=request.user.platform_id)
    r = hub.sms.post(url, d)
    if not r:
        return ajax.jsonp_fail(request, message='服务器开小差')
    return ajax.jsonp_ok(request, r.data)


@ajax_try("")
@com_user.need_login
def p_cancel(request):
    """
    @api {post} /account/cancelsms [短信]取消定时短信
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"id":短信ID, "schedule_time":定时时间}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "success": true
            },
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(id=int, schedule_time=str)
    object_id = args.id
    schedule_time = args.schedule_time
    if not object_id:
        return ajax.jsonp_fail(request, message='缺少参数: id')
    if not schedule_time:
        return ajax.jsonp_fail(request, message='缺少参数: schedule_time')
    hub = tbktapi.Hub(request)
    url = '/sms/cancel'
    d = dict(id=object_id, schedule_time=schedule_time,platform_id=request.user.platform_id)
    r = hub.sms.post(url, d)
    if not r:
        return ajax.jsonp_fail(request, message='服务器开小差')
    return ajax.jsonp_ok(request, r)
