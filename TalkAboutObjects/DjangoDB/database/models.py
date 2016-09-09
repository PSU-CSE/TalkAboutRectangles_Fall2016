from ConfigParser import RawConfigParser
from random import randint
from django.db import models


class Rectangle(models.Model):
    """
    Represents a single rectangle object in the database
    """
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    r = models.IntegerField()
    g = models.IntegerField()
    b = models.IntegerField()

    @classmethod
    def generate_rectangle(cls):
        """
        Creates a new rectangle object based on parameters found in the config
        """
        cfg = RawConfigParser()
        cfg.readfp(open('./Config/generation.conf'))
        r = Rectangle()
        r.width = randint(cfg.getint("rectangle", "min_width"), cfg.getint("rectangle", "max_width"))
        r.height = randint(cfg.getint("rectangle", "min_height"), cfg.getint("rectangle", "max_height"))
        r.x = randint(cfg.getint("rectangle", "min_x"), cfg.getint("scene", "width") - r.width)
        r.y = randint(cfg.getint("rectangle", "min_y"), cfg.getint("scene", "height") - r.height)
        r.r = randint(cfg.getint("rectangle", "min_r"), cfg.getint("rectangle", "max_r"))
        r.g = randint(cfg.getint("rectangle", "min_g"), cfg.getint("rectangle", "max_g"))
        r.b = randint(cfg.getint("rectangle", "min_b"), cfg.getint("rectangle", "max_b"))
        return r

    # Checks if two rectangles overlap and returns False if they don't
    @classmethod
    def overlaps(cls, r1, r2):
        """
        Determines if two rectangles overlap or not
        """
        if r1.x > r2.right_x() or r2.x > r1.right_x():
            return False
        if r1.y > r2.bottom_y() or r2.y > r1.bottom_y():
            return False
        return True

    def right_x(self):
        return self.x + self.width

    def bottom_y(self):
        return self.y + self.height

    def center_x(self):
        return self.x + float(self.width) / 2

    def center_y(self):
        return self.y + float(self.height) / 2

class Scene(models.Model):
    """
    A representation of a scene object in the database
    """
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    num_objects = models.IntegerField(default=0)

    def initialize_from_config(self):
        """
        Initializes the scene using parameters set in the config file
        """
        cfg = RawConfigParser()
        cfg.readfp(open('./Config/generation.conf'))
        self.height = cfg.getint("scene", "height")
        self.width = cfg.getint("scene", "width")
        self.num_objects = cfg.getint("scene", "num_objects")
        self.save()


    def create_scene(self):
        """
        Creates a new scene object
        """
        self.initialize_from_config()
        state = SceneState(scene=self)
        state.save()
        prev_rectangles = []
        while len(prev_rectangles) < 10:
            new_rect = Rectangle.generate_rectangle()
            valid = True
            for obj in prev_rectangles:
                if Rectangle.overlaps(new_rect, obj) or Rectangle.overlaps(obj, new_rect):
                    valid = False
                    break
            if valid:
                new_rect.save()
                state.rectangles.add(new_rect)
                prev_rectangles.append(new_rect)
            else:
                print("Invalid rectangle: Generating new rectangle")
        state.save()
        return state

    def load_scene(self, scene_id):
        """
        Loads a scene by ID
        """
        scene = Scene.objects.filter(id=scene_id)
        state = SceneState.objects.filter(scene=scene, previous_state=None)
        return scene, state

INITIAL = 1
INFORM = 2
ACCEPT = 3
REJECT = 4
MOVE_BACK = 5


#JM: These are the potential actions the user input can be parsed into
ACTION_CHOICES = [
    (INITIAL, "INITIAL"),
    (INFORM, "INFORM"),
    (ACCEPT, "ACCEPT"),
    (REJECT, "REJECT"),
    (MOVE_BACK, "MOVE_BACK")
]

#JM: These are the enumeration of the different states the DM can be in
START = 0
CHECK_RESULT = 1
CHECK_SET = 2
END_NORMAL = 3
END_FAILURE = 4
WAIT_INFORM = 5

STATE_CHOICES = [
    (START, "START"),
    (CHECK_RESULT, "CHECK_RESULT"),
    (CHECK_SET, "CHECK_SET"),
    (END_NORMAL, "END_NORMAL",),
    (END_FAILURE, "END_FAILURE"),
    (WAIT_INFORM, "WAIT_INFORM")
]

class SceneState(models.Model):
    """
    SceneState object represents one state for a given scene in the database.
    Contains the rectangles for the scene in addition to the selected rectangles
    for this particular state
    """
    scene = models.ForeignKey(Scene, related_name="scene_state")
    rectangles = models.ManyToManyField(Rectangle, related_name="rectangles", null=True)
    selected_rectangles = models.ManyToManyField(Rectangle, related_name="selected_rectangles", null=True)
    user_input = models.CharField(max_length=256, null=True)
    system_output=models.CharField(max_length=256, null=True)
    action = models.IntegerField(default=0, choices=ACTION_CHOICES)
    machine_state = models.IntegerField(default=0, choices=STATE_CHOICES)
    previous_state = models.ForeignKey("self", null=True)
    # needed by the system to determine singularity or plurality across states
    target_singular = models.BooleanField(default=True)

    def set_action(self, action, user_input, message, machine_state):
        """
        :param action: Action the system parsed the user as desiring
        :param user_input: the actual text input the user said
        :param message: the output the system will say to the user
        :param machine_state: the state the system is in
        :return: None
        """
        self.action = action
        self.user_input=user_input
        self.system_output = message
        self.machine_state = machine_state
        self.save()

    def select_rectangles(self, rectangles):
        """
        Adds rectangle objects to the states selected set
        :param rectangles: the rectangle objects to select
        :return: None
        """
        print("Selecting %s rectangles" % len(rectangles))
        self.selected_rectangles.clear()
        for rectangle in rectangles:
            self.selected_rectangles.add(rectangle)
        self.save()

    @classmethod
    def move_next(self, prev_state):
        """
        This function creates a new state using the same rectangles as the
        previous state
        :param prev_state: The previous state that we are moving from
        :return: None
        """
        new_state = SceneState.objects.create(scene=prev_state.scene,
                                              previous_state=prev_state, target_singular=prev_state.target_singular)
        new_state.rectangles = prev_state.rectangles.all()
        new_state.selected_rectangles = prev_state.selected_rectangles.all()
        return new_state

    @classmethod
    def get_rectangles(cls, state):
        """
        :param state: A scene state object
        :return: Either all of the rectangles if there is no previous state,
        or the selected rectangles
        """
        prev_state = state
        if prev_state.previous_state is None:
            return prev_state.rectangles.all()
        else:
            return prev_state.selected_rectangles.all()



