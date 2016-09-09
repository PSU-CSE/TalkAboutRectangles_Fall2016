####################################################
## structures.py
## TalkAboutObjects
## This file contains the class representations of the various semantic objects
## and is based off of the powerpoint about the subject
#####################################################
from sklearn.cluster import AffinityPropagation

INFINITY = 100000000

# Feature structure representing different groups of objects
class DomainFeatureStructure():
    """
    Class representing the domain feature structre object
    """
    def __init__(self, description, objects):
        self.cardinality = len(objects)
        self.description = description
        self.members = objects

    def add_description(self, description):
        self.description = description

    def add_member(self, obj):
        self.members.append(obj)


    @classmethod
    def create_feature_structure(cls, objects, func):
        min_width = min([o.width for o in objects])
        max_width = max([o.width for o in objects])
        min_height = min([o.height for o in objects])
        max_height = max([o.height for o in objects])
        min_x = min([o.x for o in objects])
        max_x = max([o.x for o in objects])
        min_y = min([o.y for o in objects])
        max_y = max([o.y for o in objects])

        d = Description(min_x, max_x, min_y, max_y, min_width, max_width,
                 min_height, max_height, type)
        return cls(d, objects)

class LinguisticFeatureStructure():
    """
    Feature structure for representing user input
    """
    def __init__(self):
        self.semantics = None

    def set_semantics(self, sem):
        self.semantics = sem

class GroundedFeatureStructure():
    """
    Combined linguistic and domain feature structure class
    """

    def __init__(self, semantic_fs, domain_fs):
        #super().__init__()
        self.description = domain_fs.description
        self.semantics = semantic_fs.semantics
        self.cardinality = semantic_fs.semantics.number
        self.members = domain_fs.members

class Description():
    """
    Base information for a domain feature structure
    """

    def __init__(self, min_x, max_x, min_y, max_y, min_width, max_width,
                 min_height, max_height, type):
        self.x = [min_x, max_x]
        self.y = [min_y, max_y]
        self.width = [min_width, max_width]
        self.height = [min_height, max_height]
        self.type = type


class Semantics():
    """
    Base information for a linguistic feature structure
    """
    def __init__(self, input, term, number, shape="rectangle"):
        self.shape = shape
        self.input = input
        self.term = term
        self.number = number


class Feature():
    """
    Representation of an individual word in our supported vocabulary.
    Ultimately clustered on to create meaningful groups
    """

    def __init__(self, keyword, func, min=True, color=None):
        self.keyword = keyword
        self.func = func
        self.min = min
        self.color = color

    def cluster(self, objects):
        """
        Clustering method that uses AffinityPropogation to cluster the objects
        based on their similarity as defined by the function implemented in this
        class
        """
        X = []
        for obj in objects:
            X.append(self.call_func(obj))
        af = AffinityPropagation().fit(X)
        #cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_

        labels = list(labels)

        return zip(labels, X, objects)

    def call_func(self, x):
        if self.color is None:
            return self.func(x)
        else:
            return self.func(x, self.color)

    def create_feature_structures(self, objects):
        """
        Groups the objects together by similar attributes based on the
        function passed in on object construction
        """
        labels = self.cluster(objects)
        feature_structures = []

        #get sorted list of positions
        positions = []
        for o in objects:
            positions.append(o.y)
        positions.sort()

        for label in set([x[0] for x in labels]):
            # this line finds all objects that belong to the label
            group = [x for i, x in enumerate(labels) if labels[i][0] == label]
            members = [x[2] for x in group]
            fs = DomainFeatureStructure.create_feature_structure(members, self.func)

            #get rectangle labels
            labs = []
            for m in members:
                label = positions.index(m.y)
                labs.append(label)
            print(labs)

            fs.description.__dict__["min_%s" % self.keyword] = min([x[1] for x in group])[0]
            fs.description.__dict__["max_%s" % self.keyword] = min([x[1] for x in group])[0]
            feature_structures.append(fs)
        return feature_structures

    def find(self, feature_structures, one=False):
        if self.min:
            return self.find_min(feature_structures, one)
        else:
            return self.find_max(feature_structures, one)

    def find_max(self, feature_structures, one=False):
        max_found_val = 0
        max_found_fs = None
        for fs in feature_structures:
            try:
                val = fs.description.__dict__["max_%s" % self.keyword]
                if val > max_found_val:
                    max_found_val = val
                    max_found_fs = fs
                    if one:
                        print(max_found_val)
                        print("----")
                        for member in fs.members:
                            print(self.call_func(member))
                        max_found_fs = [x for x in fs.members
                                        if round(self.call_func(x)[0], 4) == round(max_found_val, 4)]
                        max_found_fs = DomainFeatureStructure.create_feature_structure(max_found_fs, self.func)
            except KeyError:
                continue
        return max_found_fs

    def find_min(self, feature_structures, one=False):
        min_found_val = INFINITY
        min_found_fs = None
        for fs in feature_structures:
            try:
                val = fs.description.__dict__["min_%s" % self.keyword]
                if val < min_found_val:
                    min_found_val = val
                    min_found_fs = fs
                    if one:
                        print(min_found_val)
                        print("----")
                        for member in fs.members:
                            print(self.call_func(member))
                        min_found_fs = [x for x in fs.members if
                                        round(self.call_func(x)[0], 4) == round(min_found_val, 4)]
                        min_found_fs = DomainFeatureStructure.create_feature_structure(min_found_fs, lambda x: x)
            except KeyError:
                continue
        return min_found_fs


class RelationalFeature():
    """
    Object representation of a relational phrase
    """

    def __init__(self, phrase, func):
        self.phrase = phrase
        self.func = func

    def relate(self, l_group, r_group):
        """
        Takes two groups, a left hand group and a right hand group, then calls
        the function specified on object creation to compare the objects
        and see which ones satisfy the conditions
        """
        valid = self.func(l_group, r_group)
        return DomainFeatureStructure.create_feature_structure(valid, lambda x: x)