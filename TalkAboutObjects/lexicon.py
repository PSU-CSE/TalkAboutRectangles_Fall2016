####################################################
## lexicon.py
## TalkAboutObjects
## This file contains the grammar objects that will be put into lexicon
## adds scalar and relational adjectives
#####################################################

from structures import *
from addColor import *

INFINITY = 100000000

"""
Definitions of various adjectives, can easily specify more following the
example provided below
"""
skinny = Feature("skinny", lambda x: [min(x.width**2/float(x.height), x.height**2/float(x.width))], min=True)
square = Feature("square", lambda x: [min(x.width / float(x.height), x.height / float(x.width))], min=False)
tall = Feature("tall", lambda x: [x.width/float(x.height)], min=True)
flat = Feature("flat", lambda x: [x.height/float(x.width)], min=True)
long_des = Feature("long_des", lambda x: [max(x.width/float(x.height), x.height/float(x.width))],min = False)
small = Feature("small", lambda x: [x.width * x.height], min = True)
big = Feature("big", lambda x: [x.width * x.height], min = False)

#add colors to grammar
def add_color_words():
    #get all the colors from ColorParser.py
    all_colors = get_colors()
    colors = all_colors[0]
    main_colors = all_colors[1]

    #add all the colors to the grammar, use the color_func in addColor.py
    for c in colors:
        grammar[c.name] = Feature(c.name, lambda x, y: [color_func(x, y,main_colors)], min=True, color = c)


#words
grammar = {
    "skinny": skinny,
    "flat": flat,
    "tall": tall,
    "long": long_des,
    "square": square,
    "small": small,
    "tiny": small,
    "little": small,
    "big": big,
    "large": big,
    "skinnier": skinny,
    "flatter": flat,
    "taller": tall,
    "longer": long_des,
    "squarer": square,
    "smaller": small,
    "bigger": big,
    "larger": big,
    "skinnier than": skinny,
    "flatter than": flat,
    "taller than": tall,
    "longer than": long_des,
    "squarer than": square,
    "smaller than": small,
    "larger than": big
}


"""
Examples of defined relative terms
A RelationalFeature object takes the key words we want to define (eg: "to left of")
and a lambda function that takes in the set of rectangles in the left hand phrase
and a set of rectangles in the right hand phrase.

Eg: "The blue ones to the left of the square one"
        LEFT        REL PHRASE       RIGHT

So we would iterate through all of the rectangles in the left set and return them
only if they satisfy the lambda expression comparing them to the objects in the right
set.

"""
left_of = RelationalFeature("to left of", lambda x,y: [v for v in x.members
                                                       if v.x < y.description.x[0]-y.description.width[1]])
right_of = RelationalFeature("to right of", lambda x,y: [v for v in x.members
                                                         if v.x > y.description.x[1]+y.description.width[1]])
on_top_of = RelationalFeature("on top of", lambda x,y: [v for v in x.members
                                                         if v.y < y.description.y[1]-y.description.height[1] and
                                                         v.y > y.description.y[1]-2*y.description.height[1]])
next_to = RelationalFeature("next to", lambda x,y: [v for v in x.members
                                                       if (v.x < y.description.x[0]-y.description.width[1] and v.x > y.description.x[0]- 2 * y.description.width[1])
                                                       or (v.x > y.description.x[1]+y.description.width[1] and v.x < y.description.x[1]+ 2 * y.description.width[1])])

rel_grammar = {
    "to left of": left_of,
    "to right of": right_of,
    "above": RelationalFeature("above", lambda x,y: [v for v in x.members
                                                     if v.y < y.description.y[1]-y.description.height[1]]),
    "below": RelationalFeature("below", lambda x,y: [v for v in x.members
                                                     if v.y > y.description.y[0]+y.description.height[1]]),
    "between": RelationalFeature("between", lambda x,y: [v for v in x.members
                                                     if v.x > y.description.x[0] and v.x < y.description.x[1]]),
    "before": left_of,
    "after": right_of,
    "on top of": on_top_of,
    "next to": next_to
}

add_color_words()



