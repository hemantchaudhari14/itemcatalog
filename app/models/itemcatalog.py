from functools import wraps

from models.auth import login_required, show_login
from flask import session as login_session
from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User
from flask import Blueprint

itemcatalog = Blueprint('itemcatalog', __name__, url_prefix="/catalog", template_folder='templates')

engine = create_engine('postgresql://catalog:Sawt00th@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@itemcatalog.route('/')
def main():
    cat = session.query(Category).all()
    items = session.query(CatalogItem).all()
    return render_template(
        'latest.html',
        item_list=items,
        categories=cat,
        login_session=login_session)


# Item details
@itemcatalog.route('/<category_name>/<item_name>/')
def catalog(category_name, item_name):
    cat = session.query(Category).all()
    selected_category = session.query(
        Category).filter_by(name=category_name).one()
    item = session.query(CatalogItem).filter_by(
        name=item_name, category_id=selected_category.id).one()
    iscreator = False
    if item.user_id == login_session['user_id']:
        iscreator = True

    return render_template(
        'item-details.html',
        categories=cat,
        item=item,
        login_session=login_session,
        iscreator=iscreator)


# Items from specific Category
@itemcatalog.route('/<category_name>/items/')
def catalog_items(category_name):
    cat = session.query(Category).all()
    selected_category = session.query(
        Category).filter_by(name=category_name).one()
    items = session.query(CatalogItem).filter_by(
        category_id=selected_category.id)
    return render_template(
        'category-items.html',
        item_list=items,
        categories=cat,
        category_name=category_name,
        login_session=login_session)


# Update an item
@login_required
@itemcatalog.route('/<item_name>/edit/', methods=['GET', 'POST'])
def edit_item(item_name):
    cat = session.query(Category).all()
    item = session.query(CatalogItem).filter_by(name=item_name).one()
    if item.user_id != login_session['user_id']:
        return 'Not allowed'
    if request.method == 'POST':
        item = session.query(CatalogItem).filter_by(name=item_name).one()
        # Get posted values
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']

        # Set new values
        item.name = title
        item.description = description
        item.category_id = category_id
        session.add(item)
        session.commit()

        return redirect(
            url_for(
                'itemcatalog.catalog',
                category_name=item.category.name,
                item_name=item.name,
            ))

    else:  # GET Method

        return render_template(
            'edit-item.html',
            item=item,
            categories=cat,
            login_session=login_session)

# Add a new item
@login_required
@itemcatalog.route('/add_item/', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # Get posted values
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']

        # Create new item
        new_item = CatalogItem(
            name=title,
            description=description,
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()

        return redirect(
            url_for(
                'itemcatalog.main',
                category_name=new_item.category.name))

    else:
        cat = session.query(Category).all()
        return render_template(
            'add-item.html',
            categories=cat,
            login_session=login_session)


# Delete an existing item
@login_required
@itemcatalog.route('/<item_name>/delete/', methods=['GET', 'POST'])
def delete_item(item_name):
    if 'username' not in login_session:
        return redirect(url_for('auth.show_login'))

    cat = session.query(Category).all()
    item = session.query(CatalogItem).filter_by(name=item_name).one()
    if item.user_id != login_session['user_id']:
        return 'Not allowed'

    if request.method == 'POST':
        cat_name = item.category.name
        session.delete(item)
        session.commit()
        return redirect(url_for('itemcatalog.catalog_items', category_name=cat_name))
    else:
        return render_template(
            'delete-item.html',
            item=item,
            categories=cat,
            login_session=login_session)

