from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify, Blueprint
from flask import session as login_session
from sqlalchemy.sql import func
from sqlalchemy import asc, desc
from mod_catalog import session
from models.Item import Item, User
from models.Category import Category
import mod_auth
import requests
import random
import string
import json

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_catalog = Blueprint('catalog', __name__)


# Decorators
def login_required(function):
    # wraps(function)
    def wrapper():
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return function()
    wrapper.func_name = function.func_name
    return wrapper


def creator_required(function):
    # wraps(function)
    def wrapper(item_name):
        if 'username' not in login_session:
            return redirect('/login')
        item = session.query(Item).filter_by(name=item_name).one()
        if item.user_id != login_session['user_id']:
            return "<script>function myFunction()" \
                   "{alert('You are not authorized to edit this item." \
                   "Please create your own item in order to edit.');}" \
                   "</script><body onload='myFunction()''>"
        else:
            return function(item_name)
    wrapper.func_name = function.func_name
    return wrapper


# REST APIs
@mod_catalog.route('/')
@mod_catalog.route('/#')
@mod_catalog.route('/catalog/')
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


@mod_catalog.route('/catalog/<string:category_name>/items')
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


@mod_catalog.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def addItem():
    """
    addItem()
    Creating a new item using HTTP Post method
    New item can be created to existing category
    or a new category. Can only be performed
    by a logged in user

    """
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
        return redirect(url_for('catalog.catalogs',
                                categoryList=categories,
                                latestItems=latest_items,
                                user_name=login_session['username']))
    else:
        stmt = session.query(Item.category_id, func.count(
            '*').label('item_counts')).group_by(Item.category_id).subquery()
        categories = session.query(Category).all()
        return render_template('addItem.html', categoryList=categories,
                               user_name=login_session['username'])


@mod_catalog.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
@creator_required
def editItem(item_name):
    """
    editItem()
    Editing an existing item.
    Operation can only be done by the logged in user
    who first created the item

    """
    editedItem = session.query(Item).filter_by(name=item_name).one()
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
        return redirect(url_for('catalog.catalogs',
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


@mod_catalog.route('/catalog/<string:item_name>/delete',
				   methods=['GET', 'POST'])
@creator_required
def deleteItem(item_name):
    """
    deleteItem(item_name)
    Deleting the item selected by item_name
    Operation can only be done by the logged in user
    who first created the item

    """
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
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
        return redirect(url_for('catalog.catalogs',
                                categoryList=categories,
                                latestItems=latest_items,
                                user_name=login_session['username']))
    else:
        return render_template('deleteItem.html',
                               item_name=item_name,
                               user_name=login_session['username'])

# only original creator can edit and delete this page


@mod_catalog.route('/catalog/<string:category_name>/<string:item_name>',
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
    creator = mod_auth.controllers.getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicitem.html', item=item)
    else:
        return render_template('item.html', item=item,
                               user_name=login_session['username'])

# JSON end points methods


@mod_catalog.route('/catalog.json/')
def catalogsJSON():
    """
    catalogsJSON()
    return the entire catalog in JSON format

    """
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@mod_catalog.route('/catalog/<string:category_name>.json')
def categoryJSON(category_name):
    """
    categoryJSON(category_name)
    return the category and its items of the selected category_name
    in JSON format

    """
    category = session.query(Category).filter_by(name=category_name).one()
    return jsonify(category=[category.serialize])


@mod_catalog.route('/catalog/<string:category_name>/<string:item_name>.json')
def itemDetailJSON(category_name, item_name):
    """
    itemDetailJSON(category_name, item_name)
    return the item of the selected category_name and item_name in JSON format

    """
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(item=[item.serialize])
