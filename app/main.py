from flask import render_template, request, Blueprint, session, redirect, url_for, abort
from .static.py.translit import translit
from . import db, articles_on_page


main = Blueprint("main", __name__)

@main.route('/')
@main.route('/page/<int:x>')
def index_page(x: int = 1):
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    return render_template(
        'index.html',
        news=db.get_news_list(((x-1)*articles_on_page, x*articles_on_page)),
        categories=db.get_categories_list(),
        page=x,
        is_logged=session['is-logged'],
        is_admin=isadm
    )

@main.route('/profile/')
@main.route('/profile/category/<string:category>')
def profile(category: str = None):
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    
    if session['is-logged']:
        nnews = db.get_news_list((0, -1), author=session['name'])
        cats = list(map(lambda x: x[2], nnews))
        if category != None:
            nnews = list(x for x in nnews if x[2] == category)
        return render_template('profile.html', 
            news=nnews, name=session['name'], email=session['email'], is_logged=session['is-logged'],
            categories=list(x for x in db.get_categories_list() if x[0] in cats), is_admin=isadm)
    else:
        return redirect(url_for('auth.login'))

@main.route('/category/<string:category>')
@main.route('/category/<string:category>/page/<int:x>')
def categories_render(category: str, x: int = 1):
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    nnews = db.get_news_list(((x-1)*articles_on_page,x*articles_on_page), category=category)
    return render_template(
        'index.html', title=f"Новости категории",
        news=nnews,
        categories=db.get_categories_list(),
        page=x,
        path="category/"+category,
        is_logged=session['is-logged'],
        is_admin=isadm
    )

@main.route('/category/<string:category>/remove')
def del_category(category: str):
    if session['is-logged'] and db.is_admin(session['email']):
        db.del_category(href=category)
        return redirect('/')
    else:
        return abort(404)

@main.route('/author/<string:author>')
@main.route('/author/<string:author>/page/<int:x>')
def author_render(author: str, x: int = 1):
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    nnews = db.get_news_list(((x-1)*articles_on_page,x*articles_on_page), author=author)
    return render_template(
        'index.html', title=f"Новости пользователя {author}",
        news=nnews,
        categories=db.get_categories_list(),
        page=x,
        path="author/"+author,
        is_logged=session['is-logged'],
        is_admin=isadm
    )

@main.route('/news_detail/<int:id>')
def news_detail(id):
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    try:
        data = db.get_article_data(id)
    except KeyError:
        return abort(404)
    try:
        ncomments = db.get_comments(id)
    except KeyError:
        ncomments = []
    return render_template('news_detail.html',
        data=data, categories=db.get_categories_list(), comments=ncomments,
        is_logged=session['is-logged'], session=session,
        is_admin=isadm, article_id=id)

@main.route('/news_detail/<int:id>/remove')
def news_remove(id):
    if session['is-logged'] and (db.is_admin(session['email']) or db.get_article_data(id)[3] == session['name']):
        db.del_article(id)
        return redirect('/')
    else:
        return abort(404)
    
@main.route('/news_detail/<int:id>/', methods=['POST'])
def add_comment(id: int):
    if session['is-logged']:
        data = dict(request.form)
        db.add_comment(id, session['name'], data['text'])
        return redirect(f"/news_detail/{id}")
    else:
        return abort(404)

@main.route('/remove_comment/<string:article_id>/<int:comment_id>')
def del_comment(article_id: str, comment_id: int):
    if session['is-logged'] and (db.is_admin(session['email']) or db.get_comments(article_id)[2] == session['name']):
        db.del_comment(comment_id)
        return redirect(f'/news_detail/{article_id}')
    else:
        return abort(404)

@main.route('/create/')
def create():
    try:
        isl = session['is-logged']
        if isl:
            isadm = db.is_admin(session['email'])
        else:
            isadm = False
    except KeyError:
        session['is-logged'] = False
        isadm = False
    if session['is-logged']:
        return render_template('create.html', is_admin=isadm, name=session['name'])
    else:
        return redirect('/login')

@main.route("/create/", methods=['POST'])
def create_get_data(*args, **kwargs):
    data = dict(request.form)
    # {'author': 'Автор', 'category': 'cat', 'title': 'cat', 'preview': 'catr', 'text': 'aergew'}
    """
    {
        "title": "Удивительное событие в школе",
        "category": "school",
        "author": "Система",
        "created_at": "2000 г(д.н.э)",
        "id": 0,
        "preview": "Вчера в местной школе произошло удивительное событие - все ученики одновременно зевнули на уроке математики. ",
        "text": "Вчера в местной школе произошло удивительное событие - все ученики одновременно зевнули на уроке математики. Преподаватель был так поражен этим коллективным зевком, что решил отменить контрольную работу."
    },
    """
    cat_translit = translit(data['category'])
    if not db.is_category(cat_translit):
        db.add_category(data['category'], cat_translit)

    data['text'] = data['text'].replace("<img ", "<img style=\"margin-bottom: 10px; margin-top: 10px;\" width=100% ")
    
    db.add_article(
        title=data['title'],
        category=cat_translit,
        author=session['name'],
        text=data['text'],
        image=data['image'] if data['image'] != '' else None,
        preview=data['preview']
    )

    return redirect('/')

@main.route('/error/')
def errors_by_users():
    return abort(200)