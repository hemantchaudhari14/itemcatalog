from functools import wraps

from models.user import get_user_id, create_user
from flask import Flask, render_template, url_for, request, redirect, jsonify, Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User
# Create Anti Forgery State Token
from flask import session as login_session
import random
import string
# GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response


auth = Blueprint('auth', __name__, template_folder='templates')

# Google Client ID
CLIENT_ID = json.loads(
    open('/media/sf_Hemant/udacity-item-catalog-app-master/app/client_secret.json', 'r').read())['web']['client_id']


def login_required(func):
    @wraps(func)  # this requires an import
    def wrapper():
        if 'username' not in login_session:
            return redirect('login')
        else:
            func()

    return wrapper


@auth.route('/gconnect', methods=['POST', ])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    print 'in Geconnect method 2'
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print 'in Geconnect method 3'
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'in Geconnect method 4'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print 'in Geconnect method 5'
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    print 'in Geconnect method 6'
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
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Retrieve User Info
    user_id = get_user_id(login_session['email'])
    if not user_id:
        login_session['user_id'] = create_user(login_session)
    else:
        login_session['user_id'] = user_id

    return "Sucess"


"""
 Renders the login page.
"""
@auth.route('/login')
def show_login():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Disconnect the google login, on logout call
@auth.route('/logout')
def gdisconnect():
    if login_session['provider'] == 'google':
        # Only disconnect a connected user
        access_token = login_session.get('access_token')
        if access_token is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # Execute HTTP GET request to revoke the current token
        url = 'https://accounts.google.com/o/oauth2/revoke?' \
              'token=%s' % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
		      return redirect(url_for('itemcatalog.main'))
        else:
            response = make_response(
                json.dumps(
                    'Failed to revoke token for given user.',
                    400))
            response.headers['Content-Type'] = 'application/json'
            return response

        return "Logged out Sucessfully"
