from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# REST APIs
@app.route('/')
@app.route('/#')
@app.route('/catalog/')
def catalogs():
    """
    catalogs()
    Home page: displays all the catalogs on the left
    and latest 10 items to the right

    """
    stmt = session.query(Item.category_id, func.count(
        '*').label('item_counts')).group_by(Item.category_id).subquery()
    categories = session.query(Category).outerjoin(
        stmt,
        Category.id == stmt.c.category_id).filter(
            stmt.c.item_counts >= 0).order_by(Category.id)
    latest_items = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    if 'username' not in login_session:
        return render_template('catalog.html',  categoryList=categories,
                               latestItems=latest_items, STATE=state)
    return render_template('catalog.html',  categoryList=categories,
                           latestItems=latest_items, STATE=state,
                           user_name=login_session['username'])


@app.route('/catalog/<string:category_name>/items')
def category(category_name):
    """
    category(category_name)
    Display all the items of the category selected by
    category_name

    """
    stmt = session.query(Item.category_id, func.count(
        '*').label('item_counts')).group_by(Item.category_id).subquery()
    categories = session.query(Category).outerjoin(
                    stmt,
                    Category.id == stmt.c.category_id).filter(
                    stmt.c.item_counts >= 0).order_by(Category.id)
    category = session.query(Category).filter_by(name=category_name).one()
    category_items = session.query(Item).filter_by(
        category_id=category.id).all()
    if 'username' not in login_session:
        return render_template('category.html', categoryList=categories,
                               c=category, categoryItems=category_items)
    return render_template('category.html', categoryList=categories,
                           c=category, categoryItems=category_items,
                           user_name=login_session['username'])


@app.route('/catalog/new/', methods=['GET', 'POST'])
def addItem():
    """
    addItem()
    Creating a new item using HTTP Post method
    New item can be created to existing category
    or a new category. Can only be performed
    by a logged in user

    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['new_category']:
            category = Category(name=request.form['new_category'])
            session.add(category)
        else:
            category = session.query(Category).filter_by(
                name=request.form['category']).first()

        newItem = Item(name=request.form['name'], description=request.form[
                       'description'], category=category,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item Successfully Added %s' % newItem.name)
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).outerjoin(
                        stmt,
                        Category.id == stmt.c.category_id).filter(
                        stmt.c.item_counts >= 0).order_by(Category.id)
        latest_items = session.query(Item).order_by(desc(Item.id))
        return redirect(url_for('catalogs',
                                categoryList=categories,
                                latestItems=latest_items,
                                user_name=login_session['username']))
    else:
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).outerjoin(
                        stmt,
                        Category.id == stmt.c.category_id).filter(
                        stmt.c.item_counts >= 0).order_by(Category.id)
        return render_template('addItem.html', categoryList=categories)


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    """
    editItem()
    Editing an existing item.
    Operation can only be done by the logged in user
    who first created the item

    """
    editedItem = session.query(Item).filter_by(name=item_name).one()

    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction()" \
               "{alert('You are not authorized to edit this item." \
               "Please create your own item in order to edit.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            newCategory = session.query(Category).filter_by(
                name=request.form['category']).one()
            editedItem.category = newCategory
            editedItem.category_id = newCategory.id
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited %s' % editedItem.name)
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).outerjoin(
                        stmt,
                        Category.id == stmt.c.category_id).filter(
                        stmt.c.item_counts >= 0).order_by(Category.id)
        latest_items = session.query(Item).order_by(desc(Item.id))
        return redirect(url_for('catalogs',
                                categoryList=categories,
                                latestItems=latest_items,
                                user_name=login_session['username']))
    else:
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).outerjoin(
                        stmt,
                        Category.id == stmt.c.category_id).filter(
                        stmt.c.item_counts >= 0).order_by(Category.id)
        return render_template('editItem.html',
                               categoryList=categories,
                               item=editedItem,
                               user_name=login_session['username'])


@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    """
    deleteItem(item_name)
    Deleting the item selected by item_name
    Operation can only be done by the logged in user
    who first created the item

    """
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized to delete this item. " \
               "Please create your own item in order to delete.');}"\
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('%s Successfully Deleted' % itemToDelete.name)
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).outerjoin(
                        stmt,
                        Category.id == stmt.c.category_id).filter(
                        stmt.c.item_counts >= 0).order_by(Category.id)
        latest_items = session.query(Item).order_by(desc(Item.id))
        return redirect(url_for('catalogs',
                                categoryList=categories,
                                latestItems=latest_items,
                                user_name=login_session['username']))
    else:
        return render_template('deleteItem.html',
                               item_name=item_name,
                               user_name=login_session['username'])

# only original creator can edit and delete this page


@app.route('/catalog/<string:category_name>/<string:item_name>',
           methods=['GET', 'POST'])
def itemDetail(category_name, item_name):
    """
    itemDetail(category_name, item_name)
    Displaying the item info of the item selected
    by category_name and item_name. If the current
    logged in user is the item creator, he/she
    can also edit or delete the item.

    """
    item = session.query(Item).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicitem.html', item=item)
    else:
        return render_template('item.html', item=item,
                               user_name=login_session['username'])


# Google OAuth2 functions

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    gconnect()
    Google OAuth2 method used to authenticate
    and log in a google account user

    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

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
        response = make_response(json.dumps("Current user is "
                                            "already connected."), 200)
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print("gconnect user_id is ")
    print user_id

    flash("you are now logged in as %s. " % login_session['username'])
    print "done!"
    return 'Redirecting to home page'


@app.route('/gdisconnect')
def gdisconnect():
    """
    gdisconnect()
    Google OAuth2 method used to revoke an access token
    and sign out a logged in google account user

    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you are now signed out. ")
        return response
    else:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# User Table Helper Functions


def createUser(login_session):
    """
    createUser(login_session)
    Add the user of the existing login session to User table, and return
    user's email address.
    If user exists in the table already, simply return existing record's email.

    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    getUserInfo(user_id)
    return the user record from the User table using the supplied user_id

    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    getUserID(email)
    return the user id from the User table using the supplied email address

    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# JSON end points methods


@app.route('/catalog.json/')
def catalogsJSON():
    """
    catalogsJSON()
    return the entire catalog in JSON format

    """
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<string:category_name>.json')
def categoryJSON(category_name):
    """
    categoryJSON(category_name)
    return the category and its items of the selected category_name
    in JSON format

    """
    category = session.query(Category).filter_by(name=category_name).one()
    return jsonify(category=[category.serialize])


@app.route('/catalog/<string:category_name>/<string:item_name>.json')
def itemDetailJSON(category_name, item_name):
    """
    itemDetailJSON(category_name, item_name)
    return the item of the selected category_name and item_name in JSON format

    """
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(item=[item.serialize])


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
