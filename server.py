#!/usr/bin/env python

"""A catalog webapp with CRUD."""

from flask import Flask, render_template, request, redirect
from flask import url_for, flash, session as login_session
from flask import make_response, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, Item, User

import requests

import json
import time
import random
import string

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def getAllCategory():
    """Get a list of all categories."""
    return session.query(Category).all()


def getLatestItems():
    """Get a list of latest viewed 10 items."""
    return session.query(
        Item.name.label('i_n'),
        Category.name.label(
            'c_n')).outerjoin(
        Category,
        Item.category_id == Category.id).order_by(
        Item.time.desc()).filter(Item.time > 0).limit(10).all()


def checkLogin():
    """Check user is logged in."""
    if 'access_token' in login_session:
        return True
    else:
        return False


def getIntTime():
    """Get now time with type int."""
    return int(time.time())


def getLoginUser():
    """Get now login user."""
    return session.query(User).filter_by(
        email=login_session['email']).one()


def redirectReferer():
    """redirect to referer page."""
    referer = request.headers.get('referer')
    if not referer:
        referer = url_for('catelog')
    return redirect(referer)


@app.errorhandler(404)
def error404(e):
    """404 handler."""
    return redirect(url_for('pageNotFound'))


@app.route('/404')
def pageNotFound():
    """404 page."""
    return render_template('404.html')


@app.route('/')
@app.route('/catelog/')
def catelog():
    """The main page."""
    a = getLatestItems()
    return render_template(
        'catalog.html',
        show_categories=1,
        all_categories=getAllCategory(),
        isLogin=checkLogin(),
        latest_items=getLatestItems())


@app.route('/catelog/<string:category_name>/')
def categoryList(category_name):
    """Category list page."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category.id)
        count = session.query(Item).filter_by(category_id=category.id).count()
    except Exception as e:
        return redirect(url_for('pageNotFound'))

    return render_template(
        'category.html',
        category=category,
        items=items,
        show_categories=1,
        all_categories=getAllCategory(),
        isLogin=checkLogin(),
        count=count)


@app.route('/catelog/<string:category_name>/<string:item_name>')
def itemDetail(category_name, item_name):
    """Item detail page."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(
            Item).filter_by(
            category_id=category.id,
            name=item_name).one()
    except Exception as e:
        return redirect(url_for('pageNotFound'))

    item.time = getIntTime()
    session.add(item)
    session.commit()
    return render_template(
        'item.html',
        item=item,
        category=category,
        isLogin=checkLogin())


@app.route('/catelog/JSON')
def catelogJSON():
    """Get a json within all datas."""
    categories = session.query(Category).all()
    items = session.query(Item).all()
    catelog = []
    for i in categories:
        li = []
        for j in items:
            if j.category_id == i.id:
                temp = j.serialize
                li += [temp]
        temp = i.serialize
        if len(li) > 0:
            temp['Items'] = li
        catelog += [temp]

    return jsonify(Categories=catelog)


@app.route('/user/JSON')
def userJSON():
    """Get a json file within all users."""
    user = session.query(User).all()
    result = []

    for i in user:
        result += [i.serialize]

    return jsonify(Users=result)


@app.route('/login')
def showLogin():
    """Redirect to login page with a random state."""
    if(checkLogin()):
        return redirect(url_for('catelog'))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, isLogin=checkLogin())


@app.route('/logout')
def logout():
    """Log out thiss account."""
    if 'access_token' in login_session:
        del login_session['access_token']
        del login_session['email']
        flash("you are now logout")
    return redirect(url_for('catelog'))


@app.route('/github-connect', methods=['POST'])
def githubConnect():
    """Github oauth2 authentication."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps({'msg': 'Invalid state parameter.', 'code': 0}),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    url = 'https://github.com/login/oauth/access_token'

    payload = {
        'client_id': '136d23cf12215410c84b',
        'client_secret': 'b299879392ef4f157d47d228e6a3f457c38a180a',
        'code': code
    }

    headers = {'Accept': 'application/json'}

    r = requests.post(url, params=payload, headers=headers)

    response = r.json()

    if 'access_token' not in response:
        response = make_response(
            json.dumps({'msg': 'Get access_token failed!', 'code': 0}),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        access_token = response['access_token']

    url = 'https://api.github.com/user/emails?\
access_token=%s' % response['access_token']

    r = requests.get(url)

    response = r.json()

    try:
        if 'email' not in response[0]:
            response = make_response(
                json.dumps({'msg': 'Get email failed!', 'code': 0}),
                401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            email = response[0]['email']
    except Exception as e:
        response = make_response(
            json.dumps({'msg': 'Get email failed!', 'code': 0}),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['email'] = email
    login_session['access_token'] = access_token

    user = session.query(User).filter_by(
        email=email).all()
    if len(user) == 0:
        newUser = User(email=email)
        session.add(newUser)
        session.commit()
        flash("you are not logged in before, you are registed \
            as %s" % login_session['email'])

    flash("you are now logged in as %s" % login_session['email'])

    response = make_response(
        json.dumps({'msg': 'Auth success!', 'code': 1}),
        200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/catelog/new/', methods=['POST', 'GET'])
def newItem():
    """Create a new item."""
    if request.method == 'POST':
        if not checkLogin():
            return requests(url_for('catelog'))

        if request.form['name'].strip() == '':
            flash('item create failed: name is empty!')
            return redirect(url_for('newItem'))

        category = session.query(
            Category).filter_by(
            name=request.form['category']).one()

        ifCategory = session.query(Category).filter_by(
            name=request.form['category']).one()
        ifItem = session.query(Item).filter_by(
            category_id=ifCategory.id,
            name=request.form['name']).all()
        if (len(ifItem) > 0):
            flash('item create failed: item(%s) \
                is already exist in category(%s)' % (
                    ifItem[0].name,
                    ifCategory.name))
            return redirect(url_for('catelog'))

        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category=category,
            auth=getLoginUser(),
            time=getIntTime())
        session.add(newItem)
        session.commit()

        flash('new item created: %s' % newItem.name)

        return redirect(url_for(
            'itemDetail',
            category_name=category.name,
            item_name=newItem.name))
    else:
        all_category = session.query(Category).all()
        return render_template(
            'new-item.html',
            all_category=all_category,
            isLogin=checkLogin())


@app.route(
    '/catelog/<string:category_name>/<string:item_name>/edit/',
    methods=['POST', 'GET'])
def editItem(category_name, item_name):
    """Edit a item."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(
            name=item_name,
            category_id=category.id).one()
        user = getLoginUser()
        item_auth = session.query(User).filter_by(
            id=item.auth_id).one()
    except Exception as e:
        return redirect(url_for('pageNotFound'))

    if item.auth_id != user.id:
        flash('You can not edit item: %s.\
            This item can only be operated by\
             %s' % (item.name, item_auth.email))
        return redirectReferer()

    if request.method == 'POST':
        if not checkLogin():
            return requests(url_for('catelog'))

        if request.form['name'].strip() == '':
            flash('item create failed: name is empty!')
            return redirect(url_for(
                'editItem',
                category_name=category_name,
                item_name=item_name))

        ifCategory = session.query(Category).filter_by(
            name=request.form['category']).one()
        ifItem = session.query(Item).filter_by(
            category_id=ifCategory.id,
            name=request.form['name']).all()
        if (len(ifItem) > 0 and (item.id != ifItem[0].id)):
            flash('item(%s) edit failed: item(%s) \
                is already exist in category(%s)' % (
                    item.name,
                    ifItem[0].name,
                    ifCategory.name))
            return redirect(url_for(
                'categoryList',
                category_name=category_name))

        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category'] != ifCategory.name:
            newCategory = session.query(Category).filter_by(
                name=request.form['category']).one()
            item.category_id = ifCategory.id
        item.time = getIntTime()

        session.add(item)
        session.commit()

        flash('item edit: %s' % item.name)

        return redirect(url_for(
            'itemDetail',
            category_name=category_name,
            item_name=item.name))
    else:
        all_category = session.query(Category).all()
        return render_template(
            'edit.html',
            item=item,
            all_category=all_category,
            category_name=category.name,
            isLogin=checkLogin())


@app.route(
    '/catelog/<string:category_name>/<string:item_name>/delete/',
    methods=['POST', 'GET'])
def deleteItem(category_name, item_name):
    """Delete a item."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        itemToDelete = session.query(Item).filter_by(
            name=item_name,
            category_id=category.id).one()
        item_auth = session.query(User).filter_by(
            id=itemToDelete.auth_id).one()
        user = getLoginUser()
    except Exception as e:
        return redirect(url_for('pageNotFound'))

    if itemToDelete.auth_id != user.id:
        flash('You can not delete item: %s.\
            This item can only be operated \
            by %s' % (itemToDelete.name, item_auth.email))
        return redirectReferer()

    if request.method == 'POST':
        if not checkLogin():
            return requests(url_for('catelog'))

        session.delete(itemToDelete)
        session.commit()

        flash('item delete: %s' % item_name)

        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template(
            'dele-item.html',
            item_name=item_name,
            category_name=category_name,
            isLogin=checkLogin())


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
