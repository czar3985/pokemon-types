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

from view_model import Pokemon_VM, get_type_id, get_category_id, get_move_id, get_pokemon_name_list, get_type_name_list, get_move_name_list

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
    pokemon_list = session.query(Pokemon).order_by(asc(Pokemon.id))

    if not pokemon_list:
        flash('There are currently no pokemon in the database.')

    types = session.query(Type).order_by(asc(Type.name))
    return render_template('home.html', pokemon_list = pokemon_list, types = types, selected_type = 'All')


@app.route('/pokemon/<string:type>')
def showType(type):
    all_pokemon_list = session.query(Pokemon).order_by(asc(Pokemon.id))
    all_types = session.query(Type).order_by(asc(Type.name))
    type_id = get_type_id(type, session)

    pokemon_list = []
    if all_pokemon_list:
        for pokemon in all_pokemon_list:
            type_list = list(pokemon.type_list)
            if type_id in type_list:
                pokemon_list.append(pokemon)

    if not pokemon_list:
        flash('There are currently no %s type pokemon in the database.' % type)

    return render_template('home.html', pokemon_list = pokemon_list, types = all_types, selected_type = type)


@app.route('/pokemon/<int:id>')
def showPokemon(id):
    pokemon = session.query(Pokemon).filter_by(id = id).one()

    pokemon_view_model = Pokemon_VM(pokemon, session)

    return render_template('details.html', pokemon = pokemon_view_model)


def parse_evolution_after_list(pokemon_input):
    # Get the list of pokemon from the comma-separated input
    separated_input = pokemon_input.replace(' ','').split(',')

    pokemon_list = []
    if separated_input:
        # Check if pokemon id is valid
        for item in separated_input:
            try:
                int(item)
                pokemon_list.append(item)
            except ValueError:
                continue

    return pokemon_list


def parse_type_list(type_input):
    # Get the list of types from the comma-separated input
    separated_input = type_input.split(',')

    type_list = []
    if separated_input:
        # All possible types have been added in the database.
        # Check each type input now for validity
        for item in separated_input:
            type = string.capwords(item.strip())
            id = get_type_id(type, session)
            if (id != None):
                type_list.append(id)

    return type_list


def parse_move_list(move_input):
    # Get the list of moves from the comma-separated input
    separated_input = move_input.split(',')

    move_list = []
    if separated_input:
        # Check each move if already in the database
        for item in separated_input:
            move = string.capwords(item.strip())
            id = get_move_id(move, session)
            if (id != None):
                move_list.append(id)
            else:
                new_move = Move(name = move)
                session.add(new_move)
                session.commit()
                move_list.append(get_move_id(move, session))

    return move_list


def check_category(category_name):
    # Database entries are in capitalized first letter format
    category_name_cap = string.capwords(category_name)

    # Check if already in the database
    id = get_category_id(category_name_cap, session)
    if id == None:
        # Add to the database if not found
        new_category = Category(name = category_name_cap)
        session.add(new_category)
        session.commit()
        id = get_category_id(category_name_cap, session)

    return id


@app.route('/pokemon/new', methods=['GET','POST'])
def newPokemon():
    if request.method == 'POST':
        if request.form.get('mythical'):
            is_mythical = True
        else:
            is_mythical = False

        if request.form.get('legendary'):
            is_legendary = True
        else:
            is_legendary = False

        newPokemon = Pokemon(id = request.form['id'],
                            name = request.form['name'],
                            description = request.form['description'],
                            image = request.form['image'],
                            height = (request.form.get('height_ft', type=int) * 12) + request.form.get('height_inch', type=int),
                            weight = request.form['weight'],
                            is_mythical = is_mythical,
                            is_legendary = is_legendary,
                            evolution_before = request.form['evolution_before'],
                            evolution_after_list = parse_evolution_after_list(request.form['evolution_after']),
                            type_list = parse_type_list(request.form['type']),
                            weakness_list = parse_type_list(request.form['weakness']),
                            move_list = parse_move_list(request.form['move']),
                            category_id = check_category(request.form['category']),
                            user_id = 1)

        session.add(newPokemon)
        session.commit()

        flash('New pokemon added')
        return redirect(url_for('showPokemon', id = newPokemon.id))
    else:
        return render_template('new.html')


@app.route('/pokemon/<int:id>/edit', methods=['GET','POST'])
def editPokemon(id):
    pokemon = session.query(Pokemon).filter_by(id = id).one()
    if request.method == 'POST':
        pokemon.name = request.form['name']
        pokemon.description = request.form['description']
        pokemon.image = request.form['image']

        pokemon.height = (request.form.get('height_ft', type=int) * 12) + request.form.get('height_inch', type=int)
        pokemon.weight = request.form['weight']

        if request.form.get('mythical'):
            pokemon.is_mythical = True
        else:
            pokemon.is_mythical = False

        if request.form.get('legendary'):
            pokemon.is_legendary = True
        else:
            pokemon.is_legendary = False

        pokemon.evolution_before = request.form['evolution_before']
        pokemon.evolution_after_list = parse_evolution_after_list(request.form['evolution_after'])
        pokemon.type_list = parse_type_list(request.form['type'])
        pokemon.weakness_list = parse_type_list(request.form['weakness'])
        pokemon.move_list = parse_move_list(request.form['move'])
        pokemon.category_id = check_category(request.form['category'])

        session.add(pokemon)
        session.commit()

        flash('Pokemon details edited')
        return redirect(url_for('showPokemon', id = newPokemon.id))

    else:
        evolutions_after = ', '.join(get_pokemon_name_list(pokemon.evolution_after_list, session))
        types = ', '.join(get_type_name_list(pokemon.type_list, session))
        weaknesses = ', '.join(get_type_name_list(pokemon.weakness_list, session))
        moves = ', '.join(get_move_name_list(pokemon.move_list, session))

        return render_template('edit.html',
                               pokemon = pokemon,
                               evolutions_after = evolutions_after,
                               types = types,
                               weaknesses = weaknesses,
                               moves = moves)


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