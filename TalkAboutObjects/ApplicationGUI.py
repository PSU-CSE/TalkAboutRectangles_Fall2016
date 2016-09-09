from Tkinter import *
from DialogueEngine import DialogueEngine


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


INTRO = "Welcome to TalkAboutObjects!\nToday we will be playing where you try and select some rectangles on the screen. Type a description to get started!"

class ApplicationGUI(Frame):
    def __init__(self, parent, dialogue_engine):
        Frame.__init__(self, parent, bg="white")
        self.parent = parent
        self.canvas = Canvas(self)
        self.scale = 4
        self.dialogue_engine = dialogue_engine
        self.initUI()
        self.out(INTRO)
        self.past_points = 0
        self.current_points = 0

    def initUI(self):
        self.parent.title("TalkAboutObjects")
        self.pack(fill=BOTH, expand=1)
        self.canvas.place(x=0, y=0)

        below_scene = self.dialogue_engine.scene.height * self.scale

        self.caption = Label(self, text=self.getCaption(self.dialogue_engine.scene))
        self.caption.place(x=0, y=below_scene + 2)

        self.textOutput = Text(self, width=80, height=16, state=DISABLED)
        self.textOutput.config(bg="#111111", fg="#cccccc")
        self.textOutput.place(x=0, y=below_scene + 25)

        self.textEntry = Entry(self, width=80)
        self.textEntry.config(bg="#111111", insertbackground="#cccccc", fg="#cccccc", font="TkFixedFont")
        self.textEntry.place(x=0, y=below_scene + 300)
        self.textEntry.bind('<Return>', self.acceptInput)

        right_x = self.dialogue_engine.scene.width * self.scale + 10

        b = Button(self, text="Regenerate", command=self.regenerate)
        b.place(x=right_x, y=0)

        b = Button(self, text="Reset", command=self.reset)
        b.place(x=right_x, y=40)

        b = Button(self, text="Back", command=self.go_back)
        b.place(x=right_x, y=100)

        #points label
        l = Label(self, text = "Points")
        l.place(x=right_x, y =160)
        l = Label(self, text = "0")
        l.place(x=right_x, y =180)

        l = Label(self, text="Load Scene by ID:")
        l.place(x=right_x, y=220)

        self.sceneIdEntry = Entry(self, width=8)
        self.sceneIdEntry.place(x=right_x, y=240)
        #self.sceneIdEntry.bind('<Return>', self.read)

        b = Button(self, text="Load", command=self.load)
        b.place(x=right_x + 60, y=240)

        self.draw()

    def acceptInput(self, event):
        userInput = self.textEntry.get()
        self.echoUser(userInput)
        self.textEntry.delete(0, END)
        self.dialogue_engine.process_input(userInput)
        self.out("")
        self.draw()

        #display and calculate points
        self.past_points = self.current_points
        right_x = self.dialogue_engine.scene.width * self.scale + 10
        turn_multiplier = self.dialogue_engine.get_turn_count()
        adj_num = self.dialogue_engine.get_adj_num()
        rel_num = self.dialogue_engine.get_rel_num()  #will multiply by 2 for even 1 term this time
        rel_num += 1
        if(turn_multiplier == 1):
            self.current_points = 3 * adj_num * rel_num
        elif(turn_multiplier == 2):
            self.current_points = 2 * adj_num * rel_num
        elif(turn_multiplier == 3):
            self.current_points = 1.5 * adj_num * rel_num
        l = Label(self, text = str(self.current_points))
        l.place(x=right_x, y =180)

    def go_back(self):
        right_x = self.dialogue_engine.scene.width * self.scale + 10
        l = Label(self, text = str(self.past_points))
        l.place(x=right_x, y =180)
        self.dialogue_engine.move_previous()
        self.draw()

    def echoUser(self, userInput):
        self.out('> ' + str(userInput))

    def out(self, toPrint):
        self.textOutput.config(state=NORMAL)
        self.textOutput.insert(END, str(toPrint) + '\n')
        self.textOutput.config(state=DISABLED)
        self.textOutput.see(END)

    def regenerate(self):
        self.past_points = 0
        self.current_points = 0
        right_x = self.dialogue_engine.scene.width * self.scale + 10
        l = Label(self, text = (str(self.current_points) + "    "))
        l.place(x=right_x, y =180)

        self.dialogue_engine.new_scene()
        self.draw()

    def getCaption(self, scene):
        return ("To reuse this scene, load it using ID " + str(scene.id)) if scene.id else "To talk about this scene, click Store in DB."

    def setScene(self, scene):
        self.caption.config(text=self.getCaption(scene))
        self.draw()

    def load(self):
        self.past_points = 0
        self.current_points = 0
        right_x = self.dialogue_engine.scene.width * self.scale + 10
        l = Label(self, text = (str(self.current_points) + "     "))
        l.place(x=right_x, y =180)

        self.dialogue_engine.load_scene(self.sceneIdEntry.get())
        self.draw()

    def reset(self, event=None):
        # TODO reset context/conversation when we have that
        self.textOutput.config(state=NORMAL)
        self.textOutput.delete(1.0, END)
        self.textOutput.config(state=DISABLED)
        self.dialogue_engine.reset()

        self.past_points = 0
        self.current_points = 0
        right_x = self.dialogue_engine.scene.width * self.scale + 10
        l = Label(self, text = (str(self.current_points) + "     "))
        l.place(x=right_x, y =180)
        self.draw()

    def draw(self):
        if self.dialogue_engine.current_state.system_output is not None:
            self.out(self.dialogue_engine.current_state.system_output)
        self.canvas.pack()
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.dialogue_engine.scene.width * self.scale, self.dialogue_engine.scene.height * self.scale, width=0, fill='#000')
        print("GUI has", len(self.dialogue_engine.current_state.selected_rectangles.all()))
        for obj in self.dialogue_engine.current_state.rectangles.all():
            if obj in self.dialogue_engine.current_state.selected_rectangles.all():
                self.canvas.create_rectangle(obj.x * self.scale, obj.y * self.scale, obj.right_x() * self.scale, obj.bottom_y() * self.scale, width=2, outline='yellow')
            self.canvas.create_rectangle(obj.x * self.scale, obj.y * self.scale, obj.right_x() * self.scale, obj.bottom_y() * self.scale, width=0, fill=rgb_to_hex((obj.r, obj.g, obj.b)))
        self.caption.config(text=self.getCaption(self.dialogue_engine.scene))
        self.canvas.pack(fill=BOTH, expand=1)



def run_gui():
    root = Tk()
    dialogue_engine = DialogueEngine()
    app = ApplicationGUI(root, dialogue_engine)
    scene = dialogue_engine.scene
    root.geometry(str(scene.width * app.scale + 300) + 'x' + str(scene.height * app.scale + 400) + '+1200+300')
    root.mainloop()


run_gui()
