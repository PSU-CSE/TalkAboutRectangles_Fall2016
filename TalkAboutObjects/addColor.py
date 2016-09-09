####################################################
## addColor.py
## TalkAboutObjects
## This file contains the grammar objects that will be put into lexicon
## adds color
#####################################################

from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from ColorParser import *

'''finds the difference between two colors'''
def simple_color_func(x, y):
    c1 = (convert_color(sRGBColor(x.r / 255.0, x.g / 255.0, x.b / 255.0), LabColor))
    c2 = (convert_color(sRGBColor(y.r / 255.0, y.g / 255.0, y.b / 255.0), LabColor))
    diff = (abs(delta_e_cie2000(c1, c2)))
    return diff

'''finds the color category of a rectangle's color'''
def find_color_cat(rect, main_colors):
    #get rectangle color
    new_col = Color(rect.r, rect.g, rect.b, 'rectangle', 'cat')

    #get the color category for this rectangle
    min_dif = 10000
    min_col = Color()
    for col_comp in main_colors:
            diff = (simple_color_func(col_comp, new_col))
            if(diff < min_dif):
                min_dif = diff
                min_col = col_comp
    return min_col

'''get the difference between a color and a rectangle color'''
def color_func(x, y, main_colors):
    #convert colors the Lab Color, x rectangle, y color
    c1 = (convert_color(sRGBColor(x.r / 255.0, x.g / 255.0, x.b / 255.0), LabColor))
    c2 = (convert_color(sRGBColor(y.r / 255.0, y.g / 255.0, y.b / 255.0), LabColor))

    #find the main color category of the rectangle
    color_cat = y.category
    rect_cat = find_color_cat(x, main_colors)

    diff = (abs(delta_e_cie2000(c1, c2)))
    if(color_cat.name != rect_cat.name):

        #based on the different color categories, set different rules for each color
        #
        # increase difference if color categories are blue and purple or gold and limegreen
        if((color_cat.name == "purple" and rect_cat.name == "blue") or
               (color_cat.name == "blue" and rect_cat.name == "purple")):
            diff *= 100
        if((color_cat.name == "gold" and rect_cat.name == "limegreen") or
               (color_cat.name == "limegreen" and rect_cat.name == "gold")):
            diff = 1000

        #these colors should never be grouped together
        if((color_cat.name == "gold" and rect_cat.name == "blue") or
               (color_cat.name == "blue" and rect_cat.name == "gold")):
            diff = 1000
        if((color_cat.name == "purple" and rect_cat.name == "brown") or
               (color_cat.name == "brown" and rect_cat.name == "purple")):
            diff = 1000
        if((color_cat.name == "green" and rect_cat.name == "red") or
               (color_cat.name == "red" and rect_cat.name == "green")):
            diff = 1000
        if((color_cat.name == "green" and rect_cat.name == "brown") or
               (color_cat.name == "brown" and rect_cat.name == "green")):
            diff *= 80

    #decrease the difference if one category is hotpink and the other is purple
    if((color_cat.name == "purple" and rect_cat.name == "hotpink") or
               (color_cat.name == "hotpink" and rect_cat.name == "purple")):
            diff = diff/15

    #decrease the difference if the two colors are in the same color category or share a border color
    if(y.border_col[0] == rect_cat.name or y.border_col[1] == rect_cat.name):
        if(color_cat.name == rect_cat.name):
            diff = diff/40
        else:
            diff = (diff)/(40)
    return diff

