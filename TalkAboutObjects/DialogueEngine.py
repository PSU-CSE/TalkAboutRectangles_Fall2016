from database.models import Scene, SceneState
from database.models import START, CHECK_RESULT, CHECK_SET, END_NORMAL, END_FAILURE, ACCEPT, INFORM, REJECT, MOVE_BACK, WAIT_INFORM
from Parsers.fcfgParser import FcfgParser
from lexicon import grammar


# JM:Different messages to display to the users depenging on their action and
# the machine state
INTRO = "Welcome to TalkAboutObjects!\nToday we will be playing where you try " \
        "and select some rectangles on the screen. Type a description to get " \
        "started!"
DEFAULT_ACCEPT_MESSAGE = "Congratulations you selected a rectangle!\nHit reset " \
                         "to play again!"

DEFAULT_INFORM_MESSAGE = "We have found multiple results, please provide some " \
                         "more information"
DEFAULT_REJECT_MESSAGE = "We're sorry, but we didn't understand that. Could you " \
                         "input something else?"
CONFIRM_ACCEPT_MESSAGE_SG = "Is this the rectangle you had in mind?"
CONFIRM_ACCEPT_MESSAGE_PL = "Are these the rectangles you had in mind?"
FOUND_MANY_MESSAGE = "We have found more than one rectangle that meets that " \
                     "description.\n"
CONFIRM_SET_MESSAGE_SG = "Is the rectangle you meant in the highlighted set?"
CONFIRM_SET_MESSAGE_PL = "Are the rectangles you meant in the highlighted set?"
GET_MORE_INFO_MESSAGE = "Please provide some more input for us to narrow it down"
NOT_UNDERSTAND_MESSAGE = "Sorry, that's not in my vocabulary. Please provide us " \
                         "some different input"
ONLY_ONE = "Sorry, we only found one rectangle that matched that description. " \
           "Please provide some new input for us to try again."
DESCRIBE_SET = "Please describe the rectangles in the set that you want"

SET_FAILURE = "Please enter some input to help us determine which rectangles you want."

class DialogueEngine():
    """
    Class that controls the flow of dialogue between the user and the system.
    """
    def __init__(self):
        # The scene object that stores our rectangles
        self.scene = Scene()
        self.current_state = self.scene.create_scene()
        self.domain_feature_structures = []
        # Must specify a parser
        self.parser = FcfgParser()
        self.categorize_world()
        self.turn_count = 0
        self.adj_num = 0
        self.rel_num = 0
        self.parser.reset()

    def categorize_world(self):
        """
        This function generates the categorization of the world and
        puts the various objects into groups and builds domain feature
        structures from the categorizations.
        :return: None
        """
        for key, feature in grammar.items():
            group = feature.create_feature_structures(self.current_state.rectangles.all())
            print(key)
            self.domain_feature_structures.extend(group)


    def load_scene(self, scene_id):
        """
        Function grabs a scene by id from the database and displays it to the
        user
        :param scene_id: id number of the scene object
        :return: None
        """
        self.scene = Scene.objects.get(id=scene_id)
        self.current_state = SceneState.objects.get(scene=self.scene, previous_state=None)
        self.domain_feature_structures = []
        self.categorize_world()
        self.turn_count = 0
        self.adj_num = 0
        self.rel_num = 0
        self.parser.reset()

    def new_scene(self):
        """
        Generates a new scene
        :return: None
        """
        self.scene = Scene()
        self.current_state = self.scene.create_scene()
        self.domain_feature_structures = []
        self.categorize_world()
        self.turn_count = 0
        self.adj_num = 0
        self.rel_num = 0
        self.parser.reset()

    def process_input(self, input):
        """
        Function takes in user input and parses it and updates the state of the
        world.
        :param input: string representation of the user input
        :return: None, updates current state
        """
        new_state = SceneState.move_next(self.current_state)
        prev_machine_state = self.current_state.machine_state
        try:
            new_state, cur_rectangles, = self.parser.parse(input, new_state,
                                           self.domain_feature_structures)


            prev_selected = self.current_state.selected_rectangles.all()
            if prev_selected:
                cur_rectangles = set(cur_rectangles).intersection(set(prev_selected))

            user_action = new_state.action
            print("Singular: %s" % (new_state.target_singular))

            #JM: The user is trying to narrow down the search space
            if user_action == INFORM:
                print("Inform")
                print(new_state.target_singular)
                print(len(cur_rectangles))
                #JM: find the number of adjectives and relative terms
                self.turn_count += 1
                self.adj_num = self.parser.get_adjectives()
                self.rel_num = self.parser.get_rel_num()
                if new_state.target_singular and len(cur_rectangles) == 1:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, CONFIRM_ACCEPT_MESSAGE_SG, CHECK_RESULT)
                    new_state.select_rectangles(cur_rectangles)
                elif new_state.target_singular and len(cur_rectangles) > 1:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, FOUND_MANY_MESSAGE + CONFIRM_SET_MESSAGE_SG, CHECK_SET)
                    new_state.select_rectangles(cur_rectangles)
                elif new_state.target_singular and len(cur_rectangles) == 0:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, NOT_UNDERSTAND_MESSAGE, prev_machine_state)
                elif not new_state.target_singular and len(cur_rectangles) == 0:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, NOT_UNDERSTAND_MESSAGE, prev_machine_state)
                elif not new_state.target_singular and len(cur_rectangles) == 1:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, ONLY_ONE, prev_machine_state)
                elif not new_state.target_singular and len(cur_rectangles) > 1:
                    self.parser.reset()
                    new_state.set_action(INFORM, input, CONFIRM_ACCEPT_MESSAGE_PL, CHECK_RESULT)
                    new_state.select_rectangles(cur_rectangles)
                    print("Current rectangle number: %s " % len(cur_rectangles))

            #JM:The user is agreeing to something we have asked them
            elif user_action == ACCEPT:
                print("Accept")
                if prev_machine_state == CHECK_RESULT:
                    new_state.set_action(ACCEPT, input, DEFAULT_ACCEPT_MESSAGE, END_NORMAL)
                elif prev_machine_state == CHECK_SET:
                    new_state.set_action(ACCEPT, input, DESCRIBE_SET, WAIT_INFORM)

            #JM: The user is rejecting something we have asked them
            elif user_action == REJECT:
                print("Reject")
                if prev_machine_state == CHECK_RESULT and new_state.target_singular:
                    new_state.set_action(REJECT, input, CONFIRM_SET_MESSAGE_SG, CHECK_SET)
                elif prev_machine_state == CHECK_RESULT and not new_state.target_singular:
                    new_state.set_action(REJECT, input, CONFIRM_SET_MESSAGE_PL, CHECK_SET)
                elif prev_machine_state == CHECK_SET:
                    return self.reset_reject()
                    #if self.current_state.previous_state.machine_state == CHECK_RESULT:
                    #    new_state = self.current_state.previous_state.previous_state
                    #    new_state.set_action(INFORM, input, NOT_UNDERSTAND_MESSAGE, prev_machine_state)
                    #else:
                    #    new_state = self.current_state.previous_state

        #JM: If an error is thrown, we tell them we don't understand and undo the
        # state change
        except BaseException as e:
            self.parser.reset()
            print("ERROR:", e)
            new_state.set_action(INFORM, input, NOT_UNDERSTAND_MESSAGE, prev_machine_state)
            new_state.previous_state = self.current_state.previous_state

        self.current_state = new_state
        print("At end of func:", len(self.current_state.selected_rectangles.all()))

    def move_previous(self):
        """
        Moves back one state
        :return: None
        """

        self.turn_count += -1
        if self.current_state.previous_state is not None:
            self.current_state = self.current_state.previous_state

    def reset_reject(self):
        """
        Reset function called when we have selected rectangles where none of them
        are in the set they wanted
        :return: None
        """
        self.turn_count = 0
        self.adj_num = 0
        self.rel_num = 0
        self.parser.reset()
        rectangles = self.current_state.rectangles.all()
        prev_state = self.current_state
        new_state = SceneState.objects.create(scene=prev_state.scene)
        new_state.rectangles = rectangles
        self.current_state = new_state
        new_state.save()
        self.current_state.set_action(0, "", SET_FAILURE, START)

    def reset(self):
        """
        Resets the selected rectangles and state information but doesn't
        generate new rectangles.
        :return:
        """
        self.turn_count = 0
        self.adj_num = 0
        self.rel_num = 0
        self.parser.reset()
        rectangles = self.current_state.rectangles.all()
        prev_state = self.current_state
        new_state = SceneState.objects.create(scene=prev_state.scene)
        new_state.rectangles = rectangles
        self.current_state = new_state
        new_state.save()
        self.current_state.set_action(0, "", SET_FAILURE, START)

    def get_turn_count(self):
        return self.turn_count

    def get_adj_num(self):
        return self.adj_num

    def get_rel_num(self):
        return self.rel_num


