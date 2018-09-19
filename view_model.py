from database_setup import Pokemon, Type, Move, Category

#
# POKEMON HEIGHT FUNCTIONS
#
def get_height_for_display(height_num):
    """ Converts the height database entry to height string for display

        Args: height_num (int): Height in inches
        Return value: height_string (str): Formatted as feet'inches"
    """
    height_string = str(height_num / 12) + '\'' + str(height_num % 12) + '\"'

    return height_string


#
# POKEMON NAME FUNCTIONS
#
def get_pokemon_name(id, session):
    """Return the pokemon name given the pokemon ID"""
    if id:
        pokemon = session.query(Pokemon).filter_by(id = id).first()

        if pokemon:
            return pokemon.name
        else:
            return 'Pokemon with ID# %s' % id

    return ''


def get_pokemon_id(name, session):
    """Return the pokemon id given the pokemon name"""
    pokemon = session.query(Pokemon).filter_by(name = name).first()

    if pokemon:
        return pokemon.id
    else:
        return None


def get_pokemon_name_list(pokemon_id_list, session):
    """Return a list of pokemon names given the list of pokemon IDs"""
    pokemon_list = []

    if pokemon_id_list:
        for id in pokemon_id_list:
            name = get_pokemon_name(id, session)
            pokemon_list.append(name)

    return pokemon_list


#
# POKEMON TYPE FUNCTIONS
#
def get_type_id(name, session):
    """Return the type id given the type name"""
    type = session.query(Type).filter_by(name = name).first()

    if type:
        return type.id
    else:
        return None


def get_type_name_list(type_id_list, session):
    """Return a list of type names given the list of type IDs"""
    type_list = []

    if type_id_list:
        for id in type_id_list:
            type = session.query(Type).filter_by(id = id).first()

            if type:
                type_list.append(type.name)

    return type_list


#
# POKEMON MOVE FUNCTIONS
#
def get_move_id(name, session):
    """Return the move id given the move name"""
    move = session.query(Move).filter_by(name = name).first()

    if move:
        return move.id
    else:
        return None


def get_move_name_list(move_id_list, session):
    """Return a list of move names given the list of move IDs"""
    move_list = []

    if move_id_list:
        for id in move_id_list:
            move = session.query(Move).filter_by(id = id).first()

            if move:
                move_list.append(move.name)

    return move_list


#
# POKEMON CATEGORY FUNCTIONS
#
def get_category_id(name, session):
    """Return the category id given the category name"""
    category = session.query(Category).filter_by(name = name).first()

    if category:
        return category.id
    else:
        return None


#
# DATA VIEW MODEL
#
class Pokemon_VM():
    def __init__(self, pokemon, session):
        """Map the columns from the Pokemon table to properties for display to the page"""
        self.id = pokemon.id
        self.name = pokemon.name
        self.description = pokemon.description
        self.image = pokemon.image
        self.height = get_height_for_display(pokemon.height)
        self.weight = pokemon.weight
        self.is_mythical = pokemon.is_mythical
        self.is_legendary = pokemon.is_legendary
        self.evolution_before = get_pokemon_name(pokemon.evolution_before, session)
        self.evolutions_after = get_pokemon_name_list(pokemon.evolution_after_list, session)
        self.types = get_type_name_list(pokemon.type_list, session)
        self.weaknesses = get_type_name_list(pokemon.weakness_list, session)
        self.moves = get_move_name_list(pokemon.move_list, session)
        self.category = pokemon.category.name
        if pokemon.user.name == '':
            self.user = pokemon.user.email
        else:
            self.user = pokemon.user.name

