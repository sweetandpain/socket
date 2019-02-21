# from models.comment import Comment
# from models.weibo import Weibo
# from routes import (
#     redirect,
#     GuaTemplate,
#     current_user,
#     html_response,
#     login_required,
# )
# from utils import log
#
#
# def index(request):
#     """
#     weibo 首页的路由函数
#     """
#     u = current_user(request)
#     weibos = Weibo.find_all(user_id=u.id)
#     # 替换模板文件中的标记字符串
#     body = GuaTemplate.render('weibo_index.html', weibos=weibos, user=u)
#     return html_response(body)
#
#
# def add(request):
#     """
#     用于增加新 weibo 的路由函数
#     """
#     u = current_user(request)
#     form = request.form()
#     Weibo.add(form, u.id)
#     # 浏览器发送数据过来被处理后, 重定向到首页
#     # 浏览器在请求新首页的时候, 就能看到新增的数据了
#     return redirect('/weibo/index')
#
#
# def delete(request):
#     weibo_id = int(request.query['id'])
#     Weibo.delete(weibo_id)
#     return redirect('/weibo/index')
#
#
# def edit(request):
#     weibo_id = int(request.query['id'])
#     w = Weibo.find_by(id=weibo_id)
#     body = GuaTemplate.render('weibo_edit.html', weibo=w)
#     return html_response(body)
#
#
# def update(request):
#     """
#     用于增加新 weibo 的路由函数
#     """
#     form = request.form()
#     weibo_id = int(form['id'])
#     content = form['content']
#     Weibo.update(weibo_id, content=content)
#     # 浏览器发送数据过来被处理后, 重定向到首页
#     # 浏览器在请求新首页的时候, 就能看到新增的数据了
#     return redirect('/weibo/index')
#
#
# def same_user_required(route_function):
#     """
#     这个函数看起来非常绕，所以你不懂也没关系
#     就直接拿来复制粘贴就好了
#     """
#
#     def f(request):
#         log('same_user_required')
#         u = current_user(request)
#         if 'id' in request.query:
#             weibo_id = request.query['id']
#         else:
#             weibo_id = request.form()['id']
#         w = Weibo.find_by(id=int(weibo_id))
#
#         if w.user_id == u.id:
#             return route_function(request)
#         else:
#             return redirect('/weibo/index')
#
#     return f
#
#
# def comment_add(request):
#     u = current_user(request)
#     form = request.form()
#     weibo = Weibo.find_by(id=int(form['weibo_id']))
#
#     c = Comment(form)
#     c.user_id = u.id
#     c.weibo_id = weibo.id
#     c.save()
#     log('comment add', c, u, form)
#
#     return redirect('/weibo/index')
#
#
# def route_dict():
#     """
#     路由字典
#     key 是路由(路由就是 path)
#     value 是路由处理函数(就是响应)
#     """
#     d = {
#         '/weibo/add': login_required(add),
#         '/weibo/delete': login_required(same_user_required(delete)),
#         '/weibo/edit': login_required(same_user_required(edit)),
#         '/weibo/update': login_required(same_user_required(update)),
#         '/weibo/index': login_required(index),
#         # 评论功能
#         '/comment/add': login_required(comment_add),
#     }
#     return d


from utils import log
from routes import json_response, current_user
from models.weibo import Weibo
from models.comment import Comment
from routes import (
    redirect,
    GuaTemplate,
    current_user,
    html_response,
    login_required,
)




def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('1.html')
    r = header + '\r\n' + body
    return r.encode()


def all(request):
    weibos = Weibo.all_json()
    comments = Comment.all_json()
    all = (weibos, comments)
    return json_response(all)


def add(request):
    form = request.json()
    u = current_user(request)
    w = Weibo.add(form, u.id)
    return json_response(w.json())


def delete(request):
    weibo_id = int(request.query['id'])
    Weibo.delete(weibo_id)
    comments = Comment.find_all(weibo_id=weibo_id)
    for i in range(len(comments)):
        Comment.delete(comments[i].id)
    d = dict(
        message="成功删除 weibo"
    )
    return json_response(d)


def update(request):
    form = request.json()
    weibo_id = int(form['id'])
    title = form['title']
    w = Weibo.update(weibo_id, content=title)
    return json_response(w.json())


def weibo_owner_required(route_function):
    def f(request):
        u = current_user(request)
        if 'id' in request.query:
            weibo_id = request.query['id']
        else:
            # weibo_id = request.form()['id']
            form = request.json()
            weibo_id = form['id']
        w = Weibo.find_by(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            d = dict(
                message="权限不足"
            )
            return json_response(d)


    return f


def comment_owner_required(route_function):
    def f(request):
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            form = request.json()
            comment_id = form['id']
        c = Comment.find_by(id=int(comment_id))
        w = Weibo.find_by(id=c.weibo_id)

        if c.user_id == u.id or w.user_id == u.id:
            return route_function(request)
        else:
            d = dict(
                message="权限不足"
            )
            return json_response(d)

    return f



def comment_add(request):
    form = request.json()
    u = current_user(request)
    c = Comment.add(form, u.id)
    return json_response(c.json())


def comment_delete(request):
    comment_id = int(request.query['id'])
    Comment.delete(comment_id)
    d = dict(
        message="成功删除 评论"
    )
    return json_response(d)


def comment_updata(request):
    form = request.json()
    comment_id = int(form['id'])
    title = form['title']
    c = Comment.updata(comment_id, content=title)
    return json_response(c.json())


def route_dict():
    d = {
        '/api/weibo/all': login_required(all),
        '/api/weibo/add': login_required(add),
        '/api/weibo/delete': weibo_owner_required(delete),
        '/api/weibo/update': weibo_owner_required(update),
        '/weibo/index': login_required(index),
        '/api/comment/add': login_required(comment_add),
        '/api/comment/delete': comment_owner_required(comment_delete),
        '/api/comment/updata': comment_owner_required(comment_updata),
    }
    return d


# def route_dict():
#     d = {
#         '/api/weibo/all': all,
#         '/api/weibo/add': add,
#         '/api/weibo/delete': delete,
#         '/api/weibo/update': update,
#         '/weibo/index': index,
#         '/api/comment/add': comment_add,
#         '/api/comment/delete': comment_delete,
#         '/api/comment/updata': comment_updata,
#     }
#     return d
