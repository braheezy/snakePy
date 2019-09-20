from tkinter import *

APP_EMPHASIS_COLOR = 'dodger blue'
APP_BACKGROUND_COLOR = 'royal blue'
BUTTON_COLOR = 'sky blue'
FONT_COLOR = 'azure'
SNAKE_BOARD_COLOR = 'white'
LOSE_COLOR = 'red'
SNAKE_COLOR = 'black'
EXEC_SPEED = 100  # ms
GAME_SPEED = 1000  # ms


class Snake(Frame):
    state = {
        "init_app": True,
        "init_game": False,
        "game_loaded": False,
        "game_active": False,
        "detected": False
    }

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.mainWindow = parent

        self.snakeExec()

    def snakeExec(self):
        # create inital page
        if self.state["init_app"]:
            self.create_splash_widgets()
            self.state["init_app"] = False
        # create game page
        elif self.state["init_game"]:
            # game_loaded updated when snakeBoard is made
            self.create_game_widgets()
            self.state["init_game"] = False
        # game loaded. assume its being played
        elif self.state["game_loaded"]:
            # if collided, clean up
            if self.state['detected'] == True:
                print("state says detected")
                self.detectionActions()
            elif self.state['game_active'] == True:
                self.processDetection()

        self.mainWindow.after(EXEC_SPEED, self.snakeExec)

    def detectionActions(self):
        # update state
        print("doing detection actions")
        self.state['detected'] = False
        self.state['game_active'] = False
        # stop capturing movements
        self.mainWindow.unbind("<Key>")
        # change background color
        self.snakeBoard.config(bg=LOSE_COLOR)

    # The initial view
    def create_splash_widgets(self):
        # Top half of screen. For some reason, can't chain the pack() to it
        self.upperFrame = Frame(self.mainWindow,
                                bd=3,
                                relief=SUNKEN,
                                bg=APP_EMPHASIS_COLOR)
        self.upperFrame.pack()

        # Simple greeter label
        self.messageLabel = Label(
            self.upperFrame,
            bg=APP_EMPHASIS_COLOR,
            text="Welcome to SnakePy!!",
            font=("Times", 30, "bold"),
        )
        self.messageLabel.pack(padx=30, pady=30)

        # middle section
        self.middleFrame = Frame(self.mainWindow,
                                 bd=3,
                                 relief=SUNKEN,
                                 bg=APP_BACKGROUND_COLOR)
        self.middleFrame.pack()

        # Play button. Capture click or enter
        self.playButton = Button(self.middleFrame,
                                 text="Play",
                                 width=15,
                                 height=3,
                                 bg=BUTTON_COLOR,
                                 command=self.onPlayClicked)
        self.playButton.pack()

        # lower section
        self.lowerFrame = Frame(self.mainWindow,
                                bd=3,
                                relief=SUNKEN,
                                bg=APP_EMPHASIS_COLOR)
        self.lowerFrame.pack()

    # Clear splash widgets and replace with game widgets
    def onPlayClicked(self):
        self.messageLabel.pack_forget()
        self.playButton.pack_forget()
        self.state["init_game"] = True

    def create_game_widgets(self):
        middleFrameWidth = self.middleFrame.winfo_width()

        # Left side of middle
        self.lowerLeftMiddleFrame = Frame(self.middleFrame,
                                          bd=2,
                                          bg=APP_BACKGROUND_COLOR,
                                          relief=GROOVE)
        self.lowerLeftMiddleFrame.pack(side=LEFT, padx=middleFrameWidth / 2)

        # Special tk variables are needed to auto-update widgets
        # http://effbot.org/tkinterbook/variable.htm
        self.score = IntVar()
        # TODO: use a function to update variable
        self.score.set(0)
        # Labels to display current score
        self.scoreLabel = Label(self.lowerLeftMiddleFrame,
                                font="bold",
                                text="Score: ",
                                bg=APP_BACKGROUND_COLOR,
                                fg=FONT_COLOR).pack()

        self.scoreValueLabel = Label(self.lowerLeftMiddleFrame,
                                     font="bold",
                                     textvariable=self.score,
                                     bg=APP_BACKGROUND_COLOR,
                                     fg=FONT_COLOR).pack()

        # Right side of middle
        self.lowerRightMiddleFrame = Frame(self.middleFrame,
                                           bd=2,
                                           bg=APP_BACKGROUND_COLOR,
                                           relief=GROOVE)
        self.lowerRightMiddleFrame.pack(side=RIGHT, padx=middleFrameWidth / 2)

        # Quit button
        self.quitButton = Button(self.lowerRightMiddleFrame,
                                 text="Quit",
                                 width=5,
                                 height=3,
                                 bg='salmon2',
                                 command=self.mainWindow.destroy).pack()

        # play again
        self.playAgainButton = Button(self.lowerFrame,
                                      text="Play Again",
                                      width=6,
                                      height=4,
                                      bg=BUTTON_COLOR,
                                      command=self.resetGame).pack()

        self.createSnakeBoard()

    def resetGame(self):
        self.state["game_loaded"] = False
        # Re-create board
        self.snakeBoard.destroy()
        self.createSnakeBoard()

    def createSnakeBoard(self):
        self.snakeBoard = Canvas(self.upperFrame,
                                 bg=SNAKE_BOARD_COLOR,
                                 width=300,
                                 height=300)
        # Create the boundaries to determine collisions a.k.a. DEATHS
        #self.defineBoundaries()
        # Draw the snake head and place on starting point
        # TODO: make start a random spot, but not near edges
        self.snakeBoard.create_oval(150,
                                    150,
                                    160,
                                    160,
                                    fill=SNAKE_COLOR,
                                    tags="snake_head")

        # so the user can play from anywhere
        # TODO: game starts upon first move
        self.mainWindow.bind("<Key>", self.moveSnake)
        self.snakeBoard.pack()
        self.state["game_loaded"] = True

    def moveSnake(self, event):
        # game starts on first move
        if (self.state['game_active'] == False):
            self.state['game_active'] = True

        # process key event
        # TODO: auto movement
        pressedKey = event.keysym
        if (pressedKey == "Left"):
            self.snakeBoard.move("snake_head", -10, 0)
        elif (pressedKey == "Right"):
            self.snakeBoard.move("snake_head", 10, 0)
        elif (pressedKey == "Up"):
            self.snakeBoard.move("snake_head", 0, -10)
        elif (pressedKey == "Down"):
            self.snakeBoard.move("snake_head", 0, 10)

    def defineBoundaries(self):
        self.snakeBoard.create_line(0,
                                    0,
                                    0,
                                    300,
                                    width=20,
                                    fill="green",
                                    tags="leftSide")
        self.snakeBoard.create_line(0,
                                    0,
                                    300,
                                    0,
                                    width=20,
                                    fill="yellow",
                                    tags="topSide")
        self.snakeBoard.create_line(300,
                                    0,
                                    300,
                                    300,
                                    width=20,
                                    fill="blue",
                                    tags="rightSide")
        self.snakeBoard.create_line(0,
                                    300,
                                    300,
                                    300,
                                    width=20,
                                    fill="black",
                                    tags="bottomSide")

    # check for snake_head overlapping any side
    def processDetection(self):

        # only detect new collisions
        # find_overlapping expects a rectangle, which a line is, right?
        # check: left, top, right, bottom
        detected = \
            self.snakeBoard.find_overlapping(0, 0, 0, 300) or \
            self.snakeBoard.find_overlapping(0, 0, 300, 0) or \
            self.snakeBoard.find_overlapping(300, 0, 300, 300) or \
            self.snakeBoard.find_overlapping(0, 300, 300, 300)

        if detected:
            self.state['detected'] = True


def main():
    root = Tk()
    app = Snake(root)
    app.master.title("snakePy")

    # setup window and run
    root.configure(bg=APP_BACKGROUND_COLOR)
    root.geometry("655x600+600+300")
    root.mainloop()


if __name__ == '__main__':
    main()