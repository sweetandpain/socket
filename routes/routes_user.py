from urllib.parse import unquote_plus

from models.session import Session
from routes import (
    GuaTemplate,
    current_user,
    html_response,
    random_string,
    redirect
)

from utils import log
from models.user import User


# 不要这么 import
# from xx import a, b, c, d, e, f


def login(request):
    """
    登录页面的路由函数
    """
    form = request.form()

    u, result = User.login(form)
    # session 会话
    # token 令牌
    # 设置一个随机字符串来当令牌使用
    session_id = random_string()
    form = dict(
        session_id=session_id,
        user_id=u.id,
    )
    Session.new(form)
    # cookie 范围
    # /login
    # /login/user/view
    # /todo
    headers = {
        'Set-Cookie': 'session_id={}; path=/'.format(
            session_id
        )
    }

    return redirect('/user/login/view?result={}'.format(result), headers)


def login_view(request):
    u = current_user(request)
    result = request.query.get('result', '')
    result = unquote_plus(result)

    body = GuaTemplate.render(
        'login.html',
        username=u.username,
        result=result,
    )
    return html_response(body)


def register(request):
    """
    注册页面的路由函数
    """
    form = request.form()

    u, result = User.register(form)
    # log('register post', result)

    return redirect('/user/register/view?result={}'.format(result))


# @route('/register', 'GET')
def register_view(request):
    result = request.query.get('result', '')
    result = unquote_plus(result)

    body = GuaTemplate.render('register.html', result=result)
    return html_response(body)


def route_admin_users(request):
    u = current_user(request)
    if u.admin():
        us = User.all()
        body = GuaTemplate.render('admin_users.html', users=us)
        return html_response(body)
    else:
        return redirect('/')


# RESTFul
# GET /login
# POST /login
# UPDATE /user
# DELETE /user
#

def route_dict():
    r = {
        '/user/login': login,
        '/user/login/view': login_view,
        '/user/register': register,
        '/user/register/view': register_view,
        '/admin/users': route_admin_users,
    }
    return r
