from Parsers.AbstractParser import AbstractParser
from database.models import SceneState, ACCEPT, INFORM, REJECT
from lexicon import grammar

DEFAULT_ACCEPT_MESSAGE = "Congratulations you selected a rectangle!"
DEFAULT_INFORM_MESSAGE = "We have found multiple results, please provide some more information"
DEFAULT_REJECT_MESSAGE = "We're sorry, but we didn't understand that. Could you input something else?"

class BasicParser(AbstractParser):

    def parse(self, user_input, current_state, feature_sets):
        cur_rectangles = SceneState.get_rectangles(current_state)
        new_state = SceneState.move_next(current_state)
        for word in user_input.split(" "):
            if word in grammar.keys():
                cur_rectangles = grammar[word].find(feature_sets).members
        if len(cur_rectangles) == 1:
            new_state.set_action(ACCEPT, user_input, DEFAULT_ACCEPT_MESSAGE)
        elif len(cur_rectangles) > 1:
            new_state.set_action(INFORM, user_input, DEFAULT_INFORM_MESSAGE)
        else:
            new_state.set_action(REJECT, user_input, DEFAULT_REJECT_MESSAGE)
        new_state.select_rectangles(cur_rectangles)
        return new_state


