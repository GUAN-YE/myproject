# coding: utf-8
from libs.utils import db,ajax, ajax_try
import time
@ajax_try({})
# @com_user.need_login
def test_error(request):
    args = request.QUERY.casts(userid=str, platform=str, type=str, module =str,error =str, version=str, time=str)
    userid = args.userid or ''
    platform = args.platform or ''
    type = args.type or ''
    module = args.module or ''
    error = args.error or ''
    version = args.version or ''
    is_time=time.time()
    try:
        db.user.app_errorinfo.create(
            userid=userid,
            platform=platform,
            type=type,
            module=module,
            error=error,
            version=version,
            time=is_time
        )
        return ajax.jsonp_ok(request, {'message': 'ok'})
    except:
        return ajax.jsonp_fail(request,{'message':'error'} )

