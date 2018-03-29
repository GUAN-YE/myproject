# coding:utf-8
from apps.account import common
from libs.utils import ajax


def qg_info(request):
    """
    全国(北京)开通页面
    :param request:
    :return:
    """
    args = request.QUERY.casts(province_id=int, third_id=int, from_type=int)
    user = request.user
    province_id = args.province_id
    third_id = args.third_id
    from_type = args.from_type
    out = common.get_user_info(province_id, third_id, from_type, user)
    return ajax.jsonp_ok(request, out)


def qg_tiyan_day(request):
    """
    全国(北京)体验剩余时间
    :param request:
    :return:
    """
    """
    @api {post} /account/other/subject/qg/tiyan/day 全国(北京)体验剩余时间
    @apiGroup account
    @apiParamExample {json} 请求示例
    {
        "subject_id" : 2,5,9
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": [
            {
                "sid": 2
                "status":  1     # 0 未体验， 1 正在体验    2 体验过或开通过
                "tiyan_day": 25, # 体验剩余时间，  0代表没在体验时间内
            },
            {
                "sid": 5
                "status":  0     # 0 未体验， 1 正在体验    2 体验过或开通过
                "tiyan_day": 0, # 体验剩余时间，  0代表没在体验时间内
            },
        ]
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(subject_id=str)
    subject_ids = args.subject_id
    subject_ids = [int(s) for s in subject_ids.split(',') if s]
    user = request.user
    out = common.get_qg_tiyan_day(user, subject_ids)
    return ajax.ajax_ok(out)
