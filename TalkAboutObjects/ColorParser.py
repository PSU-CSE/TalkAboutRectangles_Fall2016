import re
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

'''Color Class. Make a color object with with rgb values. Color category is the overarching main color this color
belongs to, if a color is on the border between two main colors, it is given border colors. A main color is given
adjacent colors (blue is adjacent to limegreen, orange is adjacent to brown and red, and so on...)'''
class Color:
    name = 'black'
    def __init__(self, r = 0, g = 0, b = 0, name = '', category = '', border_col = ['',''], adjacent_col = ['','']):
        self.r = r
        self.g = g
        self.b = b
        self.name = name
        self.category = category
        self.border_col = border_col
        self.adjacent_col = adjacent_col

    def __str__(self):
        return self.name + ': ' + str(self.r) + ', ' + str(self.g) + ', ' + str(self.b)

'''Parse colorTable1.txt and put colors into Color Objects'''
def parse_table_1():
    colors = []
    f = open('colorTable1.txt', 'r')
    linesIntoColor = 0
    color = Color()
    for line in f.read().split('\n'):
        is_number = 0
        if '<tr>' in line:
            color = Color()
            linesIntoColor = 0
            continue
        linesIntoColor += 1
        if linesIntoColor is 1:
            search = re.search('\'>(?P<name>.*)</font', line)
            color.name = search.group('name')
            #split the name and check for number
            name_split = color.name.split()
            for name in name_split:
                if(name.isdigit()):
                    is_number = 1
                    continue
        if linesIntoColor is 5:
            search = re.search('>(.*)</td', line)
            color.r = int(search.group(1))
        if linesIntoColor is 6:
            search = re.search('>(.*)</td', line)
            color.g = int(search.group(1))
        if linesIntoColor is 7:
            search = re.search('>(.*)</td', line)
            color.b = int(search.group(1))
        if '</tr>' in line:
            if(is_number == 0):
                colors.append(color)
            continue
    return colors

'''Parse colorTable2.txt and put colors into Color Objects'''
def parse_table_2():
    colors = []
    f = open('colorTable2.txt', 'r')
    linesIntoColor = 0
    color = Color()
    for line in f.read().split('\n'):
        is_number = False
        if '<tr>' in line:
            color = Color()
            linesIntoColor = 0
            continue
        linesIntoColor += 1
        if linesIntoColor is 2:
            search = re.search('>(?P<name>.*)</td', line)
            color.name = search.group('name')
            #split the name and check for number
            name_split = color.name.split()
            for name in name_split:
                if(name.isdigit()):
                    is_number = True
            # Remove inner tags
            color.name = re.sub('<[^ \>]+\>', '', color.name)
        if linesIntoColor is 4:
            search = re.search('>\((?P<r>.*),(?P<g>.*),(?P<b>.*)\)</td', line)
            color.r = int(search.group('r'))
            color.g = int(search.group('g'))
            color.b = int(search.group('b'))
        if '</tr>' in line:
            if(not is_number):
                colors.append(color)
            continue
    for color in colors:
        if ' / ' in color.name:
            names = color.name.split(' / ')
            color.name = names[0]
            newColor = Color(color.r, color.g, color.b)
            newColor.name = names[1]
            colors.append(newColor)
    return colors

'''convert the two colors the lab color and find the difference'''
def color_func(x, y):
    c1 = (convert_color(sRGBColor(x.r / 255.0, x.g / 255.0, x.b / 255.0), LabColor))
    c2 = (convert_color(sRGBColor(y.r / 255.0, y.g / 255.0, y.b / 255.0), LabColor))
    diff = (abs(delta_e_cie2000(c1, c2)))
    return diff

'''when a color is between two main colors it is defined as a border color'''
def define_border_color(col, col_comp1, col_comp2):
    col.border_col = [col_comp1.name, col_comp2.name]

'''adjacent color: a main color that is close to another main color'''
def define_adjacent_col(col):
    if(col.name == 'blue'):
        col.adjacent_col = ['limegreen', '']
    if(col.name == 'limegreen'):
        col.adjacent_col = ['blue', '']
    if(col.name == 'gold'):
        col.adjacent_col = ['brown', '']
    if(col.name == 'orange'):
        col.adjacent_col = ['brown', 'red']
    if(col.name == 'purple'):
        col.adjacent_col = ['hotpink', '']
    if(col.name == 'brown'):
        col.adjacent_col = ['red', 'orange']

'''process the list of colors and assign color categories, border colors, and adjacent colors'''
def get_colors():
    many_colors = parse_table_1() + parse_table_2()
    new_colors = []
    main_colors = []

    #find main colors that will be used to define the color categories
    for col in many_colors:
        #add colors to main colors, these will be the larger 'groups' of colors.
        if(col.name == 'blue' or col.name == 'limegreen' or col.name == "orange"
           or col.name == 'red' or col.name == 'purple' or col.name == 'gold' or col.name == 'hotpink'
           or col.name == 'white' or col.name == "brown"):
            main_colors.append(col)
            define_adjacent_col(col)
        is_number = False
        name_split = col.name.split()
        #getting rid of colors that have numbers in front of them
        for name in name_split:
            if(name.isdigit()):
                is_number = True
        if(not is_number):
            new_colors.append(col)

    #defining color categories, put each color into a main color
    for new_col in new_colors:
        min_dif = 10000
        min_col = Color()
        for col_comp in main_colors:
            diff = (color_func(col_comp, new_col))
            if(diff < min_dif):
                min_dif = diff
                min_col = col_comp
        new_col.category = min_col

    #defining border colors and re-defining the color cateogries
    for new_col in new_colors:
        for col_comp in main_colors:
            diff = (color_func(col_comp, new_col))
            #if new_col is on the border between two main colors, the border colors will be these two main colors
            if(diff < 20 and new_col.category.name != col_comp.name):
                define_border_color(new_col, col_comp, new_col.category)

            #change color category to blue
            if(diff < 50 and ((new_col.category.name == 'blue' and col_comp.name == 'limegreen') or
                                  (new_col.category.name == 'limegreen' and col_comp.name == 'blue'))):
                if(diff < 40):
                    new_col.category = col_comp
                else:
                    define_border_color(new_col, col_comp, new_col.category)

            #change color category to limegreen
            if(diff < 50 and col_comp.name == "limegreen" and new_col.category.name == "gold"):
                if(diff < 40):
                    new_col.category = col_comp
            #change color category to blue
            elif(diff < 52 and col_comp.name == "blue" and new_col.category.name == "white"):
                new_col.category = col_comp
            #change color category to limegreen
            elif(diff < 43 and col_comp.name == "limegreen" and new_col.category.name == "white"):
                new_col.category = col_comp
    return new_colors,main_colors


