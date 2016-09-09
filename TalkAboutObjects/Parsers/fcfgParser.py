####################################################
## fcfgParser.py
## TalkAboutObjects
## JM: This function implements a parser using a custom feature context free
## grammar
#####################################################

from Parsers.AbstractParser import AbstractParser
from database.models import SceneState, ACCEPT, INFORM, REJECT, MOVE_BACK
from lexicon import grammar, rel_grammar, DomainFeatureStructure
import nltk
import traceback
from nltk import parse

nltk.data.path.append("Parsers/")

#JM: constants representing the state of singular or plural
SINGULAR = "S"
PLURAL = "P"

#JM: Words we treat as reject-state word
retreat_words = ["no", "wrong", "incorrect", "not" ]

#JM: words we use to imply an accept state
accept_words = ["yes", "yeah", "ya", "ok", "okay", "right", "correct" ]


class FcfgParser(AbstractParser):
    """
    Class representing the parser we use to determine the intention of
    user's input
    """

    def __init__(self):
        self.parser = parse.load_parser('base_parse.fcfg', trace=1)

        self.adj_num = 0
        self.rel_num = 0
        self.tot_adj = 0
        self.linking_blocks = []
        self.sem_blocks = []

    def parse(self, user_input, new_state, feature_sets):
        """
        Parses user input and returns the new_state and current
        rectangles
        :param user_input: string representation of the user's input
        :param new_state: SceneState Object that is a clone of the previous state
        :param feature_sets: A list of FeatureSet objects so we know which
            groups of colors we are aware of
        :return: a new state with a user's action specified and the
            list of rectangles we think should be selected
        """
        self.adjective_options = []
        keys = grammar.keys()
        yy = []

        #JM: We convert all of the keys from our lexicon into a tuple of
        # (key, number of words in key)
        for key in keys:
            yy.append((key, len(key.split(" "))))
        #JM: We then sort the keys by number of words in it from most to fewest
        # words because we want 'dark green' to be seen as one adjective not
        # the word 'dark' and the adjective 'green'
        keys = [x[0] for x in sorted(yy, key=lambda x: x[1], reverse=True)]
        for i, key in enumerate(keys):
            if key in user_input:
                self.adjective_options.append(key)
                # Replace the adjective with a keyword to be parsed by our
                # parser
                user_input = user_input.replace(key, "adjective%s" % len(self.adjective_options))
        new_state.action = INFORM
        self.sem_blocks = []
        self.linking_blocks = []
        cur_rectangles = new_state.previous_state.selected_rectangles.all()

        # Strips punctuation
        tokens = [x.lower() for x in user_input.split() if not x in [".", "?", ",", "*"]]


        #JM: Check to see if any of their words are negative ones
        if any(x in tokens for x in retreat_words):
            new_state.action = REJECT
        #JM: Check to see if any of their words are affirmative ones
        elif any(x in tokens for x in accept_words):
            new_state.action = ACCEPT
        else:
            if len(tokens) == 1 and not tokens[0] in ["the", "a", "an"]:
                tokens = ["the"] + tokens + ["ones"]
            if len(tokens) == 2 and not tokens[0] in ["the", "a", "an"]:
                tokens = ["the"] + tokens

            sentences = self.parser.parse(tokens)

            for i, line in enumerate(sentences):
                self.parse_nodes(line)

            #new_state = SceneState.move_next(current_state)
            cur_rectangles, end_one= self.ground_feature_structures(feature_sets)
            new_state.target_singular = end_one
        return new_state, cur_rectangles

    def ground_feature_structures(self, feature_sets):
        """
        Takes a list of feature_sets and returns the rectangles that are in
        the union of the feature sets of the adjectives parsed, and the number
        of the adjective.
        """
        groups = []
        end_one = self.sem_blocks[0].number == SINGULAR
        try:
            for sem in self.sem_blocks:
                assert sem.term
                print sem.term
                one = sem.number == SINGULAR
                if len(sem.term) == 1:
                    groups.extend([grammar[jj].find(feature_sets, one=one) for jj in sem.term if jj in grammar])
                else:
                    new_groups = [grammar[jj].find(feature_sets, one=False).members for jj in sem.term if jj in grammar]
                    cur_rectangles = set(new_groups[0]).intersection(*new_groups) if new_groups else []
                    groups.append(DomainFeatureStructure.create_feature_structure(cur_rectangles, lambda x: x))
            cur_rectangles = []
            if groups:
                while self.linking_blocks:
                    linking_phrase = self.linking_blocks.pop()
                    r_group = groups.pop()
                    l_group = groups.pop()
                    result = rel_grammar[linking_phrase].relate(l_group, r_group)
                    if result:
                        groups.append(result)

                groups = [x.members for x in groups]
                cur_rectangles = set(groups[0]).intersection(*groups) if groups else []
                #if end_one and len(cur_rectangles) > 1:
                #    cur_rectangles = []
        except BaseException as e:
            print(e)
            traceback.print_exc()
            print("Error occured!")
            cur_rectangles = []

        return cur_rectangles, end_one

    def construct_fs(self, noun_phrase_node):
        """
        Traverses a noun phrase node until it finds an adjective and then it
        parses the adjective
        """
        adjectives = []
        number = None
        input = ""
        for node in noun_phrase_node:
            print("Noun phrase node:", node)
            print(node.label())
            if "JP" in str(node.label()):
                for leaf in node.leaves():
                    adjective_key = int("".join([str(x) for x in leaf if x.isdigit()]))
                    print("KEY", adjective_key)
                    print(self.adjective_options)
                    adjectives.append(self.adjective_options[adjective_key-1])
                    print("ADJECTIVES", adjectives)
            elif "= 'N'" in str(node.label()) and node.label()["NUM"] == "pl":
                number = PLURAL
            elif "= 'N'" in str(node.label()) and node.label()["NUM"] == "sg":
                number = SINGULAR
        sem = Semantics(number, adjectives, input)
        print("THESE ARE THE NUMBER OF ADJECTIVES: " + str(len(adjectives)))
        self.adj_num = len(adjectives)
        self.tot_adj += self.adj_num
        print("Sem found:", sem)
        return sem

    def construct_rel_phrase(self, node):
        """
        Pulls out the relative phrase words from a node deemed a relative
        phrase node
        """
        input = " ".join([x.leaves()[0] for x in node if not "DET" in str(x.label())])
        print("Relative phrase found", input)
        return input


    def construct_dict(self, node):
        return {x:y for (x, y) in node.label().items()}

    def parse_nodes(self, parent):
        """
        Traverses the parse tree and ultimately parses the adjectives and
        relative phrases from the tree
        """
        for node in parent:
            if type(node) is nltk.Tree:
                if "NP" in str(node.label()):
                    s = self.construct_fs(node)
                    self.sem_blocks.append(s)
                elif "RP" in str(node.label()):
                    print("Relative phrase found")
                    self.rel_num += 1
                    self.linking_blocks.append(self.construct_rel_phrase(node))
                self.parse_nodes(node)

    def get_adjectives(self):
        if(self.rel_num != 0):
            return self.tot_adj
        else:
            return self.adj_num

    def get_rel_num(self):
        return self.rel_num

    def reset(self):
        self.rel_num = 0
        self.adj_num = 0
        self.tot_adj = 0

class Semantics():
    """
    A representation of an semantics object as depicted in the powerpoint
    describing this model
    """

    def __init__(self, number, terms=None, input=None, shape="rectangle"):
        self.shape = shape
        self.term = terms
        self.number = number
        self.input = input

    def __str__(self):
        return "\nSEMANTICS\nShape: %s\nAjectives: %s\nNumber: %s\n\n" % \
               (self.shape, self.term, self.number)

