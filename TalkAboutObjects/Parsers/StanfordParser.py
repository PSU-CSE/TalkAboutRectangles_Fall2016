import os
from nltk.parse import stanford
from Parsers.AbstractParser import AbstractParser
from database.models import SceneState, ACCEPT, INFORM, REJECT
from lexicon import grammar
import nltk


path = '/Users/John/research/TalkAboutObjects2/TalkAboutObjects/Parsers/StanfordJars/'
os.environ['STANFORD_PARSER'] = path
os.environ['STANFORD_MODELS'] = path
ROOT = 'ROOT'


SINGULAR = "S"
PLURAL = "P"

substitutions = {
    "next to": "NEXT_TO_TOKEN"
}

DEFAULT_ACCEPT_MESSAGE = "Congratulations you selected a rectangle!"
DEFAULT_INFORM_MESSAGE = "We have found multiple results, please provide some more information"
DEFAULT_REJECT_MESSAGE = "We're sorry, but we didn't understand that. Could you input something else?"


class ExpandedParser(AbstractParser):

    def __init__(self):
        self.parser = stanford.StanfordParser(model_path=path+"englishPCFG.ser.gz")
        self.linking_blocks = []
        self.sem_blocks = []

    def parse(self, user_input, current_state, feature_sets):
        self.sem_blocks = []
        self.linking_blocks = []

        # if the user_input is only a single word, we add a noun to it to make the phrase parsable
        words = user_input.split(" ")
        if len(words) <= 1 and words[-1] not in ["one", "ones", "box", "boxes"]:
            user_input += " ones"

        # Add 'the' to the beginning of the input to make the phrase more parse-able
        if words[0] != "the":
            user_input = "the " + user_input

        for key, value in substitutions.items():
            user_input = user_input.replace(key, value)

        # We add a period at the end to make the sentence more parse-able
        if user_input[-1] != ".":
            user_input += "."
        sentences = self.parser.raw_parse_sents((user_input,))
        for line in sentences:
            self.parse_nodes(line)

        new_state = SceneState.move_next(current_state)
        cur_rectangles = self.ground_feature_structures(feature_sets)
        if len(cur_rectangles) == 1:
            new_state.set_action(ACCEPT, user_input, DEFAULT_ACCEPT_MESSAGE)
        elif len(cur_rectangles) > 1:
            new_state.set_action(INFORM, user_input, DEFAULT_INFORM_MESSAGE)
        else:
            new_state.set_action(REJECT, user_input, DEFAULT_REJECT_MESSAGE)
        new_state.select_rectangles(cur_rectangles)
        return new_state

    def ground_feature_structures(self, feature_sets):
        groups = []
        cur_rectangles = []
        print(self.sem_blocks)
        print(self.linking_blocks)
        for sem in self.sem_blocks:
            assert sem.term
            print sem.term
            one = sem.number == SINGULAR
            if len(sem.term) == 1:
                if one:
                    groups = [[grammar[jj].find(feature_sets, one=one)] for jj in sem.term if jj in grammar]
                else:
                    groups =  [grammar[jj].find(feature_sets, one=one).members for jj in sem.term if jj in grammar]
                cur_rectangles = set(groups[0]).intersection(*groups) if groups else []
            else:
                groups =  [grammar[jj].find(feature_sets, one=False).members for jj in sem.term if jj in grammar]
                cur_rectangles = set(groups[0]).intersection(*groups) if groups else []
                if one and len(cur_rectangles) > 1:
                    cur_rectangles = []
        for group in groups:
            print len(group)

        return cur_rectangles


    def construct_fs(self, noun_phrase_node):
        adjectives = []
        number = None
        input = ""
        for node in noun_phrase_node:
            print node.label()
            if len(node.leaves()) == 1 and node.leaves()[0] in substitutions.values():
                self.linking_words.append(substitutions.keys()[substitutions.values().index(node.leaves()[0])])
            if len(node.leaves()) == 1 and node.leaves()[0].lower() in grammar:
                node.set_label("JJ")
            if node.label() == "DT":     # Ignore determinants like "the" "a" and "an"
                continue
            elif node.label() == "JJ":
                adjectives.append(node.leaves()[0])
            elif node.label() == "NNS":
                number = PLURAL       # set number to plural
            elif node.label() == "NN":
                number= SINGULAR       # set number to singular
            input += " %s" % node.leaves()[0]
        sem = Semantics(number, adjectives, input)
        return sem


    def __check_node_for_children_np(self, node):
        for child in node:
            if child.label() == "NP":
                return False
        return True

    def reshape_items(self, items, new):
        recent = items[-1]
        adj = recent.input.split(" ")[-1]
        recent.term.append(adj)
        recent.number = new.number
        recent.input = recent.input + " %s" % new.input
        items[-1] = recent
        return items

    def parse_nodes(self, parent):
        for node in parent:
            if type(node) is nltk.Tree:
                if node.label() == "NP" and \
                        self.__check_node_for_children_np(node):
                    s = self.construct_fs(node)
                    if hasattr(s, "term") and not s.term:
                        self.reshape_items(self.sem_blocks, s)
                    elif hasattr(s, "term") and not s in self.sem_blocks:
                        self.sem_blocks.append(s)
                    else:
                        self.linking_words.append(s)
                if node.label() == "IN":
                    self.linking_blocks.append(node.leaves()[0])
                self.parse_nodes(node)


class Semantics():

    def __init__(self, number, terms=None, input=None, shape="rectangle"):
        self.shape = shape
        self.term = terms
        self.number = number
        self.input = input

    def __str__(self):
        return "\nSEMANTICS\nShape: %s\nAjectives: %s\nNumber: %s\n\n" % \
               (self.shape, self.term, self.number)
"""
sem_blocks = []
linking_words = []

def construct_fs(noun_phrase_node):
    adjectives = []
    number = None
    input = ""
    for node in noun_phrase_node:
        print node.label()
        if len(node.leaves()) == 1 and node.leaves()[0] in substitutions.values():
            linking_words.append(substitutions.keys()[substitutions.values().index(node.leaves()[0])])
        if node.label() == "DT":     # Ignore determinants like "the" "a" and "an"
            continue
        elif node.label() == "JJ":
            adjectives.append(node.leaves()[0])
        elif node.label() == "NNS":
            number = PLURAL       # set number to plural
        elif node.label() == "NN":
            number= SINGULAR       # set number to singular
        input += " %s" % node.leaves()[0]
    sem = Semantics(number, adjectives, input)
    return sem



def check_node_for_children_np(node):
    for child in node:
        if child.label() == "NP":
            return False
    return True

def reshape_items(items, new):
    recent = items[-1]
    adj = recent.input.split(" ")[-1]
    recent.term.append(adj)
    recent.number = new.number
    recent.input = recent.input + " %s" % new.input
    items[-1] = recent
    return items

def getNodes(parent):
    for node in parent:
        if type(node) is nltk.Tree:
            if node.label() == "NP" and \
                    check_node_for_children_np(node):
                s = construct_fs(node)
                if hasattr(s, "term") and not s.term:
                    reshape_items(sem_blocks, s)
                elif hasattr(s, "term"):
                    sem_blocks.append(s)
                else:
                    linking_words.append(s)
            if node.label() == "IN":
                linking_words.append(node.leaves()[0])
            getNodes(node)


parser = stanford.StanfordParser(model_path=path+"englishPCFG.ser.gz")
sent = "the tall skinny ones"
for key, value in substitutions.items():
    sent = sent.replace(key, value)
sentences = parser.raw_parse_sents((sent,))
for line in sentences:
    getNodes(line)
    for sent in line:
        sent.draw()

for item in sem_blocks:
    print item

for link in linking_words:
    print link

print sem_blocks"""