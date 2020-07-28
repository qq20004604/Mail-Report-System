import json
from package.decorator_csrf_setting import my_csrf_decorator
from package.request_method_limit import post_limit, login_limit
from package.response_data import get_res_json
from package.session_manage import set_user_session, clear_session, is_logined
from .models import UserModel
from .forms import RegisterForm, LoginForm, SendRegCodeForm
from .utils import is_can_reg
from mail_pusher import utils as mail_utils
from mail_pusher.models import RegVerifyMailModel
from config.username_banned import BANNED_USERNAME


# Create your views here.
@my_csrf_decorator()
@post_limit
def send_email_regcode(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = SendRegCodeForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 拿到用户名和密码
    username = uf.cleaned_data['username']
    email = uf.cleaned_data['email']
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
    else:
        ip = request.META.get('REMOTE_ADDR')

    # 1. 账号、邮箱已使用，则不能继续注册
    # 2. 检查推送频率
    # 3. 推送验证码邮件

    # 先查重（已注册显然不能继续推送）
    search_info = is_can_reg(username=username, email=email)
    if search_info is not None:
        return get_res_json(code=0, msg=search_info)

    # 检查是否可以推送邮件
    is_can_send = mail_utils.can_send_regcode_email(email=email, ip=ip)
    if is_can_send is not None:
        return get_res_json(code=0, msg=is_can_send)

    # 创建一条邮件记录
    new_mail_info = RegVerifyMailModel.objects.create(email=email, ip=ip)
    # 推送邮件
    send_result = mail_utils.send_regcode_email(email=email, regcode=new_mail_info.verify_code)

    if send_result.code == 200:
        return get_res_json(code=send_result.code, msg='邮件发送成功，请访问邮箱查看验证码')
    else:
        return get_res_json(code=send_result.code, msg='邮件发送失败，请重试或联系管理员。\n失败原因：%s' % send_result.msg)


@my_csrf_decorator()
@post_limit
def register(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = RegisterForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 拿到用户名和密码（并去掉中间的空格）
    username = uf.cleaned_data['username'].replace(' ', '')
    password = uf.cleaned_data['password'].replace(' ', '')
    email = uf.cleaned_data['email'].replace(' ', '')
    regcode = uf.cleaned_data['regcode'].replace(' ', '')

    if username in BANNED_USERNAME:
        return get_res_json(code=0, msg='非法的用户名，请勿使用敏感词作为用户名')

    # 1. 账号、邮箱已使用，则不能继续注册
    # 2. 检查验证码+邮箱 是否有数据。如果有数据，该条数据是否过期
    # 3. 创建一条注册信息，设置密码（加密）

    # 先查账号、邮件是否已存在
    search_info = is_can_reg(username=username, email=email)
    if search_info is not None:
        return get_res_json(code=0, msg=search_info)

    # 查数据
    check_result = mail_utils.is_regcode_correct(email=email, regcode=regcode)
    if check_result is not None:
        return get_res_json(code=0, msg=check_result)

    user = UserModel.objects.create(username=username, email=email)
    # 设置密码
    user.set_pw(password)
    user.save()
    set_user_session(request, user)
    return get_res_json(code=200, msg='注册成功', data={
        'username': username,
        'userid': user.id
    })


@my_csrf_decorator()
@post_limit
def login(request):
    # 加载数据
    data = json.loads(request.body)
    # 表单校验
    uf = LoginForm(data)
    # 数据是否合法
    if uf.is_valid() is False:
        # 返回错误信息
        return get_res_json(code=0, msg=uf.get_form_error_msg())

    # 拿到用户名和密码
    username = uf.cleaned_data['username']
    password = uf.cleaned_data['password']

    # 先查重
    search_info = UserModel.objects.order_by('-id').filter(username=username)
    if len(search_info) == 0:
        return get_res_json(code=0, msg='该用户名不存在或密码错误。\n重设密码请联系 QQ：20004604')

    user = search_info[0]
    # 校验密码
    if user.is_pw_correct(password) is False:
        # 密码错误
        return get_res_json(code=0, msg='该用户名不存在或密码错误。\n重设密码请联系 QQ：20004604')
    # 登录成功，设置session
    set_user_session(request, user)
    user.set_last_login()
    user.save()

    return get_res_json(code=200, msg='登录成功', data={
        'username': username,
        'userid': user.id
    })


@my_csrf_decorator()
@post_limit
@login_limit
def logout(request):
    try:
        clear_session(request)
        return get_res_json(code=200)
    except BaseException as e:
        print(e)
        return get_res_json(code=0, msg='未知错误')


@my_csrf_decorator()
@post_limit
def had_logined(request):
    if is_logined(request) is True:
        return get_res_json(code=200, data={
            'username': request.session.get('username'),
            'userid': request.session.get('id'),
        })
    else:
        return get_res_json(code=5, msg='')
