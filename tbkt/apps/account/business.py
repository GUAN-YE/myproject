# coding: utf-8
"""业务相关接口"""
from libs.utils import ajax, ajax_try
from apps.common import com_user
from . import common


@ajax_try({})
@com_user.need_teacher
def p_unopen_count(request):
    """
    @api {get} /account/unopen_count [业务]班级下未开通人数
    @apiGroup account
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "unopen": 1, # 未开通人数
        },
        "response": "ok",
        "error": ""
    }
    """
    user = request.user
    unopen = common.get_unopen_count(user)
    data = {
        'unopen': unopen
    }
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_teacher
def p_addtask_count(request):
    """
    @api {get} /account/addtask_count [业务]教师本月发作业次数
    @apiGroup account
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "addtask": 1, # 本月发作业次数
        },
        "response": "ok",
        "error": ""
    }
    """
    user = request.user
    addtask = common.get_addtask_count(user)
    data = {
        'addtask': addtask
    }
    return ajax.jsonp_ok(request, data)
