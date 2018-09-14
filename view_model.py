import database_setup

class Pokemon_VM():
    def get_height(self, height_num):
        height_string = ''
        return height_string


    def get_pokemon(self, id):
        return ''


    def get_pokemon_list(self, pokemon_id_list):
        pokemon_list = []
        return pokemon_list


    def get_types(self, type_id_list):
        type_list = []
        return type_list


    def get_moves(self, move_id_list):
        move_list = []
        return move_list


    def __init__(self, pokemon):

        self.id = pokemon.id
        self.name = pokemon.name
        self.description = pokemon.description
        self.image = pokemon.image
        self.height = self.get_height(pokemon.height)
        self.weight = pokemon.weight
        self.is_mythical = pokemon.is_mythical
        self.is_legendary = pokemon.is_legendary
        self.evolution_before = self.get_pokemon(pokemon.evolution_before)
        self.evolutions_after = self.get_pokemon_list(pokemon.evolution_after_list)
        self.types = self.get_types(pokemon.type_list)
        self.weaknesses = self.get_types(pokemon.weakness_list)
        self.moves = self.get_moves(pokemon.move_list)
        self.category = pokemon.category.name
