from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Pokemon, User, Category, Type, Move, engine

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Pokemon Types"


# Connect to Database and create database session
engine = create_engine('sqlite:///pokemon.db',  connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()


@app.route('/pokemon/login/')
def showLogin():
	return "login page"


def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


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
    login_session['email'] = data['email']

    # See if the user exists in the database or create a new entry
    userId = getUserID(login_session['email'])
    if userId == None:
        userId = createUser(login_session)
    login_session['user_id'] = userId

    output = '<br />'
    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
    response = make_response(redirect(url_for('showHome')))
    response.headers['Content-Type'] = 'text/html'
    return response


@app.route('/')
@app.route('/pokemon/')
def showHome():
    pokemon_list = session.query(Pokemon).order_by(asc(Pokemon.name))

    if not pokemon_list:
        flash('There are currently no pokemon in the database.')

    types = session.query(Type).order_by(asc(Type.name))
    return render_template('home.html', pokemon_list = pokemon_list, types = types, selected_type = 'All')


@app.route('/pokemon/<string:type>')
def showType(type):
    all_pokemon_list = session.query(Pokemon).order_by(asc(Pokemon.name))
    all_types = session.query(Type).order_by(asc(Type.name))

    pokemon_list = []
    for pokemon in all_pokemon_list:
        type_list = list(pokemon.type_list)
        if type in type_list:
            pokemon_list.append(pokemon)

    if not pokemon_list:
        flash('There are currently no %s type pokemon in the database.' % type)

    return render_template('home.html', pokemon_list = pokemon_list, types = all_types, selected_type = type)


@app.route('/pokemon/<int:id>')
def showPokemon(id):
    return "Details page for pokemon with id: %s" % id


@app.route('/pokemon/new')
def newPokemon():
    return "New pokemon page"


@app.route('/pokemon/<int:id>/edit')
def editPokemon(id):
    return "Edit page for pokemon with id: %s" % id


@app.route('/pokemon/<int:id>/delete')
def deletePokemon(id):
    return "Delete page for pokemon with id: %s" % id


@app.route('/pokemon/json')
def showAllJson():
    return "List of pokemon in json"


@app.route('/pokemon/<string:type>/json')
def showTypeJson(type):
    return "Shows all pokemon of selected type %s in json" % type


@app.route('/pokemon/<int:id>/json')
def showPokemonJson(id):
    return "Details for pokemon with id: %s in json" % id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)