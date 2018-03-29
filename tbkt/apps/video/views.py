#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: view.py
@time: 2017/6/29 16:23
"""

import time

from libs.utils import db, ajax, Struct, ajax_try

@ajax_try({})
def p_tags(request):
    """
        @api {post} /video/tags [视频]视频踩顶
        @apiGroup video
        @apiParamExample {json} 请求示例
            {
            "object_id": 6723             # 视频ID或知识点ID
            "type": 1                     # 1: 视频ID 2: 知识点ID
            "status":                     # 1: 顶 0: 踩
            }
        @apiSuccessExample {json} 成功返回
            {"message": "", "error": "",
               "data": {
                    "agree_num": 1,
                    "status": 0,
                    "dis_agree_num": 1
                },
              "response": "ok", "next": ""}
        @apiSuccessExample {json} 失败返回
            {"message": "", "error": "", "data": "", "response": "fail", "next": ""}
        """
    """
    功能说明：                视频踩顶
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    张帅男                    2017-6-29
    """
    user_id = request.user_id
    data = Struct()
    object_id = int(request.POST.get("object_id", 0))
    v_type = int(request.POST.get("type", 0))
    status = int(request.POST.get("status", -1))  # 0 踩 1 赞
    if user_id:
        if v_type == 1:
            video_evaluation = db.slave.evaluation.select('id', 'agree_num', 'dis_agree_num').filter(video_id=object_id)
        else:
            video_evaluation = db.slave.evaluation.select('id', 'agree_num', 'dis_agree_num').filter(knowledge_id=object_id)
        if video_evaluation:
            video_evaluation = video_evaluation[0]
        else:
            if v_type == 1:
                video_evaluation_id = db.default.evaluation.create(video_id=object_id, add_time=time.time())
            else:
                video_evaluation_id = db.default.evaluation.create(knowledge_id=object_id, add_time=time.time())
            video_evaluation = Struct()
            video_evaluation.id = video_evaluation_id
            video_evaluation.agree_num = 0
            video_evaluation.dis_agree_num = 0
        evaluation_detail = db.slave.evaluation_detail.select('status').filter(evaluation_id=video_evaluation.id, user_id=user_id).first()
        if evaluation_detail:
            if status > -1 and evaluation_detail.status != status:
                if status == 1:
                    video_evaluation.agree_num += 1
                    video_evaluation.dis_agree_num -= 1
                elif status == 0:
                    video_evaluation.agree_num -= 1
                    video_evaluation.dis_agree_num += 1
                db.default.evaluation_detail.filter(evaluation_id=video_evaluation.id, user_id=user_id).update(status=status)
                db.default.evaluation.filter(id=video_evaluation.id).update(agree_num=video_evaluation.agree_num, dis_agree_num=video_evaluation.dis_agree_num)
            else:
                status = evaluation_detail.status
        elif status > -1:
            if status == 1:
                video_evaluation.agree_num += 1
            elif status == 0:
                video_evaluation.dis_agree_num += 1
            db.default.evaluation_detail.create(evaluation_id=video_evaluation.id, user_id=user_id, status=status)
            db.default.evaluation.filter(id=video_evaluation.id).update(agree_num=video_evaluation.agree_num,
                                                                        dis_agree_num=video_evaluation.dis_agree_num)
        agree_num = video_evaluation.agree_num
        dis_agree_num = video_evaluation.dis_agree_num
    data.agree_num = agree_num
    data.dis_agree_num = dis_agree_num
    data.status = status
    return ajax.jsonp_ok(request, data)

def p_error_feedback(request):
    """
        @api {post} /video/error_feedback [视频]报错处理
        @apiGroup video
        @apiParamExample {json} 请求示例
            {
            "type": 42
            "id": 6101
            "mark":    视频无法放
            "reason":  201
            }
        @apiSuccessExample {json} 成功返回
            {"message": "", "error": "",
               "data": {},
              "response": "ok", "next": ""}
        @apiSuccessExample {json} 失败返回
            {"message": "", "error": "", "data": "", "response": "fail", "next": ""}
        """
    """
    功能说明：                提交纠错
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    张帅男                    2017-6-29
    """
    user_id = request.user_id
    args = request.QUERY.casts(type=int, id=int, reason=str, mark=unicode)
    type_id = int(args.type or 0)
    object_id = int(args.id or 0)
    reason = args.reason or ''
    mark = args.mark or u''
    # 验证reason必须是逗号分隔的数字:
    for s in reason.split(','):
        if s:
            assert s.isdigit()
    if type_id not in (31, 32):
        db.default.error_feedback.create(
            user_id=user_id,
            type=type_id,
            object_id=object_id,
            reason=reason,
            remark=mark,
            add_time=time.time()
        )
    return ajax.jsonp_ok(request)

