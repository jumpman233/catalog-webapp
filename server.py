# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session as login_session, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

import random, string

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getAllCategory():
    category = session.query(Category).all()

@app.route('/')
@app.route('/hello')
def HelloWorld():
    category = session.query(Category).first()
    items = session.query(Item).filter_by(category_id=category.id)
    output = ''
    for i in items:
        output += i.name
        output += '</br>'
        output += i.description
        output += '</br>'
    return output

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print oauth_flow
        oauth_flow.redirect_uri = 'postmessage'
        print(code)
        credentials = oauth_flow.step2_exchange(code)
        print(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print(code)
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/catelog/<string:category_name>/')
def categoryList(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    output = ''
    for i in items:
        output += i.name
        output += '</br>'
        output += i.description
        output += '</br>'
        output += '</br>'
    return render_template('main.html', category = category, items = items)

@app.route('/catelog/new/', methods = ['POST', 'GET'])
def newItem():
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        newItem = Item(name=request.form['name'], description=request.form[
                               'description'], category_id=category.id)
        session.add(newItem)
        session.commit()

        flash('new item created')

        return redirect(url_for('categoryList', category_name=category.name))
    else:
        all_category = session.query(Category).all()
        return render_template('new-item.html', all_category = all_category)


@app.route('/catelog/<string:category_name>/<string:item_name>/edit/', methods = ['POST', 'GET'])
def editItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name, category_id = category.id).one()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:   
            item.description = request.form['description']
        if request.form['category']:   
            newCategory = session.query(Category).filter_by(name=request.form['category']).one()
            item.category_id = newCategory.id
        session.add(item)
        session.commit()

        return redirect(url_for('categoryList', category_name=category_name))
    else:
        all_category = session.query(Category).all()
        return render_template('edit.html', item=item, all_category = all_category, category_name = category.name)

# Task 3: Create a route for deleteMenuItem function here


@app.route('/catelog/<string:category_name>/<string:item_name>/delete/', methods = ['POST', 'GET'])
def deleteItem(category_name, item_name):
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=category_name).one()
        itemToDelete = session.query(Item).filter_by(name=item_name, category_id = category.id).one()

        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('dele-item.html', item_name=item_name, category_name = category_name)

if __name__ == '__main__':
    app.secret_key = 'secret'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)