import random
from tkinter import *
from itertools import chain

APP_EMPHASIS_COLOR = 'dodger blue'
APP_BACKGROUND_COLOR = 'royal blue'
BUTTON_COLOR = 'sky blue'
FONT_COLOR = 'azure'
SNAKE_BOARD_COLOR = 'white'
LOSE_COLOR = 'red'
SNAKE_COLOR = 'black'
APPLE_COLOR = 'green'
PIECE_SIZE = 10  # pixels
GAME_SPEED = 300  # ms

ALLOWED_APPLE_RANGE = range(10, 290, PIECE_SIZE)
ALLOWED_APPLE_RANGE_MIN = 10
ALLOWED_APPLE_RANGE_MAX = 290
ALLOWED_SNAKE_START_RANGE = range(50, 250, PIECE_SIZE)
'''
Program flow:
    create splash page
    when Play is clicked, create game page
    Lauch game logic loop
        Executed at GAME_SPEED
        On first movement, game begins
        Snake auto-movement in direction of last press
        Constant boundary detection and apple capture starts
        Apple generator starts
'''


class Snake(Frame):
    # a dict holding state control for the app
    app_state = {
        # True if we should initialize the app
        "init_app": True,
        # True if we should initialize the game view
        "init_game": False,
        # True if the game is currently being played
        "game_active": False,
        # True if a collision was detected during play
        "collision_detected": False
    }

    # a set holding state control for snake movement
    current_move = "None"

    # On class creation, designate root and kick off exec function
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.mainWindow = parent

        self.create_splash_widgets()

    # core logic of game
    # TODO: is this the right pattern to use with tkinter mainloop()?
    def snakeExec(self):
        if self.app_state['game_active'] == True:
            self.processMovement()
            self.processDetection()
            if self.app_state['collision_detected'] == True:
                self.collisionDetectionActions()
        self.mainWindow.after(GAME_SPEED, self.snakeExec)

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

    # The game view
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

        self.snakeExec()

    # create the main snake board and snake head
    def createSnakeBoard(self):
        self.snakeBoard = Canvas(self.upperFrame,
                                 bg=SNAKE_BOARD_COLOR,
                                 width=300,
                                 height=300)

        # Draw the snake head and place on starting point
        # TODO: make start a random spot, but not near edges
        startCoord_x = random.choice(ALLOWED_SNAKE_START_RANGE)
        startCoord_y = random.choice(ALLOWED_SNAKE_START_RANGE)
        self.snakeBoard.create_oval(startCoord_x,
                                    startCoord_y,
                                    startCoord_x + PIECE_SIZE,
                                    startCoord_y + PIECE_SIZE,
                                    fill=SNAKE_COLOR,
                                    tags="snake_head")

        # so the user can play from anywhere
        # TODO: game starts upon first move
        self.mainWindow.bind("<Key>", self.moveSnake)
        self.snakeBoard.pack()

        # make first apple
        self.generateApple()

    # generate apples in random spots on snake board
    def generateApple(self):
        '''
        use PRNG to pick coord in snake board
        do not generate apples:
            on boundary
            on current snake
        '''

        # keep trying to make new apples until a good one is made
        while True:
            # get rid of existing apple
            self.snakeBoard.delete('apple')
            appleCoord_x = random.choice(ALLOWED_APPLE_RANGE)
            appleCoord_y = random.choice(ALLOWED_APPLE_RANGE)
            self.snakeBoard.create_oval(appleCoord_x,
                                        appleCoord_y,
                                        appleCoord_x + PIECE_SIZE,
                                        appleCoord_y + PIECE_SIZE,
                                        fill=APPLE_COLOR,
                                        tags="apple")
            if self.checkIfAppleOnSnake() == 1:
                break

    # Clear splash widgets and replace with game widgets
    def onPlayClicked(self):
        self.messageLabel.pack_forget()
        self.playButton.pack_forget()
        self.create_game_widgets()

    # find if apple is overlapped with snake head
    # If no collision, returns tuple length of 1
    # TODO: snake body
    def checkIfAppleOnSnake(self):
        snakeHeadCoords = self.snakeBoard.coords("snake_head")
        return len(
            self.snakeBoard.find_overlapping(snakeHeadCoords[0],
                                             snakeHeadCoords[1],
                                             snakeHeadCoords[2],
                                             snakeHeadCoords[3]))

    # handle post-collision actions
    def collisionDetectionActions(self):
        # update app_state
        print("doing collision detection actions")
        self.app_state['collision_detected'] = False
        self.app_state['game_active'] = False
        # stop capturing movements
        self.mainWindow.unbind("<Key>")
        # change background color
        self.snakeBoard.config(bg=LOSE_COLOR)

    # handle game reset when play again is clicked
    def resetGame(self):
        self.app_state["game_active"] = False
        self.current_move = "None"
        # Re-create board
        self.snakeBoard.destroy()
        self.createSnakeBoard()

    # control snake movement
    def moveSnake(self, event):
        pressedKey = event.keysym

        # game starts on first move
        if (self.app_state['game_active'] == False):
            self.app_state['game_active'] = True
            self.current_move = pressedKey
        else:
            # set move_state from key event
            # only update current move if allowed
            if self.current_move == "Left" and pressedKey != "Right":
                self.current_move = pressedKey
            elif self.current_move == "Up" and pressedKey != "Down":
                self.current_move = pressedKey
            elif self.current_move == "Right" and pressedKey != "Left":
                self.current_move = pressedKey
            elif self.current_move == "Down" and pressedKey != "Up":
                self.current_move = pressedKey

    # continually redraw snake head in movement direction
    def processMovement(self):
        '''
        Have "Move_States" for each direction snake should move
        Move state is based on last pressed direction
        Only allow moves in the 'forward' 3 directions:
            Moving      Disallow
            LEFT        RIGHT
            UP          DOWN
        '''
        if self.current_move == 'Left':
            self.snakeBoard.move("snake_head", -10, 0)
        elif self.current_move == 'Right':
            self.snakeBoard.move("snake_head", 10, 0)
        elif self.current_move == 'Up':
            self.snakeBoard.move("snake_head", 0, -10)
        elif self.current_move == 'Down':
            self.snakeBoard.move("snake_head", 0, 10)

    # check for snake_head overlapping any side or apples
    # TODO: also check snake_head overlapping any snake body parts
    def processDetection(self):
        if self.checkIfAppleOnSnake() != 1:
            self.generateApple()
        # only detect new collisions
        # find_overlapping expects a rectangle, which a line is, right?
        # check: left, top, right, bottom
        boundaryDetected = \
            self.snakeBoard.find_overlapping(0, 0, 0, 300) or \
            self.snakeBoard.find_overlapping(0, 0, 300, 0) or \
            self.snakeBoard.find_overlapping(300, 0, 300, 300) or \
            self.snakeBoard.find_overlapping(0, 300, 300, 300)

        if boundaryDetected:
            self.app_state['collision_detected'] = True


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