# Pokemon Types

The application keeps a record of all pokemon grouped by type.

## Prerequisites

1. **python 2.7.x**
2. **sqlalchemy**
3. **sqlite3**
4. **flask**
5. _database_setup.py_
6. _pokemon_types.py_
7. _initial_entries.py_ 
8. Google developers account and client secret

## Usage

The following resource gives more information on how to run python scripts: 
[How to Run a Python Script via a File or the Shell](https://www.pythoncentral.io/execute-python-script-file-shell/).

_database_setup.py_ will setup the database: _pokemon.db_

_initial_entries.py_ will populate the database

_pokemon_types.py_ will run the web server 

Navigate to port 8000, 

Home page: http://localhost:8000/pokemon/

Details page for each pokemon
Ex: http://localhost:8000/pokemon/{pokedex_id}/

### Create client secret for Google log-in

Follow the steps below to create _client_secrets.json_

1. In https://console.developers.google.com/apis/dashboard, sign in to your Google account
2. Create Project. Indicate a name for the app
3. Go to your app's page in Google APIs Console
4. Choose Credentials
5. Create an OAuth Client ID.
6. Configure the consent screen, with email and app name
7. Choose Web application list of application types
8. Set the authorized JavaScript origins - http://localhost:8000
9. Authorized redirect URIs: http://localhost:8000/login and http://localhost:8000/gconnect
10. Download the client secret JSON file and copy the contents to client_secrets.json in the same folder as the pokemon_types.py file
11. In templates/login.html, replace the client id in the following line:
```html
data-clientid="REPLACE_THIS_WITH_THE_CLIENT_ID.apps.googleusercontent.com"
```

## Database Structure

Pokemon

Types

Moves

Categories

Users

## Features

- View all pokemon in the database or per category
- View details of each pokemon
- Edit pokemon details
- Delete a pokemon
- Add a pokemon
- Make use of JSON API endpoints for a list of all pokemon, all pokemon per category or details of a specific pokemon

Ex. 

http://localhost:8000/pokemon/JSON, 

http://localhost:8000/pokemon/{category}/JSON, 

http://localhost:8000/pokemon/{pokedex_id}/JSON
