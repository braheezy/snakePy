import random
import pdb
from tkinter import *
from itertools import chain

APP_EMPHASIS_COLOR = 'dodger blue'
APP_BACKGROUND_COLOR = 'royal blue'
BUTTON_COLOR = 'sky blue'
FONT_COLOR = 'azure'
SNAKE_BOARD_COLOR = 'white'
LOSE_COLOR = 'red'
SNAKE_HEAD_COLOR = 'black'
SNAKE_TAIL_COLOR = 'purple'
APPLE_COLOR = 'green'
PIECE_SIZE = 10  # pixels
GAME_SPEED = 600  # ms

ALLOWED_APPLE_RANGE = range(10, 290, PIECE_SIZE)
ALLOWED_SNAKE_START_RANGE = range(50, 250, PIECE_SIZE)
'''
Program flow:
    create splash page
    when Play is clicked, create game page
    Lauch game logic exec loop
        Executed at GAME_SPEED
        On first movement, game begins
        Snake auto-movement in direction of last press
        Constant boundary detection and apple capture detection starts
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

    # current apple item id
    apple_id = 0

    # On class creation, designate root (parent) and make splash page
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.mainWindow = parent
        self.create_splash_widgets()

    # core logic of game
    # TODO: is this the right pattern to use with tkinter mainloop()?
    def snakeExec(self):

        # only run loops during active game session
        if self.app_state['game_active'] == True:
            self.processMovement()
            self.processDetection()
            if self.app_state['collision_detected'] == True:
                self.collisionDetectionActions()
        '''
        IMPORTANT
        Makes the game run at speed. This dictates how
        fast the snake will move, user input, boundary and apple detection
        '''
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

    # Clear splash widgets and replace with game widgets
    # Start game exec logic
    def onPlayClicked(self):
        self.messageLabel.pack_forget()
        self.playButton.pack_forget()
        self.create_game_widgets()
        self.snakeExec()

    # The game view
    def create_game_widgets(self):
        middleFrameWidth = self.middleFrame.winfo_width()

        # Left side of middle
        self.lowerLeftMiddleFrame = Frame(self.middleFrame,
                                          bd=2,
                                          bg=APP_BACKGROUND_COLOR,
                                          relief=GROOVE)
        self.lowerLeftMiddleFrame.pack(side=LEFT, padx=middleFrameWidth / 2)

        # set initial score
        # current user score to display, in the special tkinter variable
        self.score = IntVar()
        self.updateScore()
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

    # create the main snake board and snake head
    def createSnakeBoard(self):
        self.snakeBoard = Canvas(self.upperFrame,
                                 bg=SNAKE_BOARD_COLOR,
                                 width=300,
                                 height=300)

        # Create the boundaries to determine collisions a.k.a. DEATHS
        self.defineBoundaries()

        # Draw the snake head and place on random starting point
        startCoord_x = random.choice(ALLOWED_SNAKE_START_RANGE)
        startCoord_y = random.choice(ALLOWED_SNAKE_START_RANGE)
        # Make snake head options dict
        head_options = {
            "id": 0,
            "coord_x": startCoord_x,
            "coord_y": startCoord_y,
            "color": SNAKE_HEAD_COLOR,
            "tag": "snake_head"
        }
        # make linked list class head
        self.snake = SnakeLinkedList()
        self.snake.head = SnakeNode("None", self.snakeBoard, head_options)
        # on start, tail is head
        self.currentTailNode = self.snake.head

        # so the user can play from anywhere
        self.mainWindow.bind("<Key>", self.updateSnakeMovement)
        self.snakeBoard.pack()

        # make first apple
        self.generateApple()

    # boundary items for detection
    def defineBoundaries(self):
        self.snakeBoard.create_line(0,
                                    0,
                                    0,
                                    300,
                                    width=1,
                                    fill="green",
                                    tags="leftSide")
        self.snakeBoard.create_line(0,
                                    0,
                                    300,
                                    0,
                                    width=1,
                                    fill="yellow",
                                    tags="topSide")
        self.snakeBoard.create_line(300,
                                    0,
                                    300,
                                    300,
                                    width=1,
                                    fill="blue",
                                    tags="rightSide")
        self.snakeBoard.create_line(0,
                                    300,
                                    300,
                                    300,
                                    width=1,
                                    fill="black",
                                    tags="bottomSide")

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
            snakeHeadCoords = self.snakeBoard.coords(
                self.snake.head.options["tag"])
            self.snakeBoard.create_oval(appleCoord_x,
                                        appleCoord_y,
                                        appleCoord_x + PIECE_SIZE,
                                        appleCoord_y + PIECE_SIZE,
                                        fill=APPLE_COLOR,
                                        tags="apple")
            # exactly 1 means the only item overlapping the area of interest
            # is the apple
            if self.checkIfAppleOnSnake(
                    appleCoord_x,
                    appleCoord_y,
            ) == 1:
                # get apple id. remember that find_overlapping returns a tuple
                self.apple_id = self.snakeBoard.find_overlapping(
                    appleCoord_x, appleCoord_y, appleCoord_x + PIECE_SIZE,
                    appleCoord_y + PIECE_SIZE)[0]
                print("apple id is now %d" % self.apple_id)
                break

    # accessor to tkinter variable updater
    def updateScore(self, newScore=0):
        self.score.set(newScore)

    # find if generated apple is on snake
    def checkIfAppleOnSnake(
            self,
            appleCoord_x,
            appleCoord_y,
    ):
        return len(
            self.snakeBoard.find_overlapping(appleCoord_x, appleCoord_y,
                                             appleCoord_x + PIECE_SIZE,
                                             appleCoord_y + PIECE_SIZE))

    # handle post-collision actions
    def collisionDetectionActions(self):
        # update app_state
        self.app_state['collision_detected'] = False
        self.app_state['game_active'] = False
        # stop capturing movements
        self.mainWindow.unbind("<Key>")
        # change background color
        self.snakeBoard.config(bg=LOSE_COLOR)

    # handle game reset when play again is clicked
    def resetGame(self):
        # game only active after first move
        self.app_state["game_active"] = False
        # clear out stale move
        self.current_move = "None"
        # reset score
        self.updateScore()
        # Re-create board
        self.snakeBoard.destroy()
        self.createSnakeBoard()

    # capture user commands for snake movement
    def updateSnakeMovement(self, event):
        pressedKey = event.keysym

        # game starts on first move
        if (self.app_state['game_active'] == False):
            self.app_state['game_active'] = True
            self.snake.head.moveDirection = pressedKey
        else:
            # set move_state from key event
            # only update current move if it's an allowed move
            if self.snake.head.moveDirection == "Left" and pressedKey != "Right":
                self.snake.head.moveDirection = pressedKey
            elif self.snake.head.moveDirection == "Up" and pressedKey != "Down":
                self.snake.head.moveDirection = pressedKey
            elif self.snake.head.moveDirection == "Right" and pressedKey != "Left":
                self.snake.head.moveDirection = pressedKey
            elif self.snake.head.moveDirection == "Down" and pressedKey != "Up":
                self.snake.head.moveDirection = pressedKey

    # continually redraw snake head in current movement direction
    def processMovement(self):
        '''
        Have "Move_States" for each direction snake should move
        Move state is based on last pressed direction
        Only allow moves in the 'forward' 3 directions:
            Moving      Disallow
            LEFT        RIGHT
            UP          DOWN
        '''
        # if self.snake.head.moveDirection == 'Left':
        #     self.snakeBoard.move("snake_head", -PIECE_SIZE, 0)
        # elif self.snake.head.moveDirection == 'Right':
        #     self.snakeBoard.move("snake_head", PIECE_SIZE, 0)
        # elif self.snake.head.moveDirection == 'Up':
        #     self.snakeBoard.move("snake_head", 0, -PIECE_SIZE)
        # elif self.snake.head.moveDirection == 'Down':
        #     self.snakeBoard.move("snake_head", 0, PIECE_SIZE)

        # update all tail pieces with new head movement

        self.propogateNewMove()

        # fairly standard way of traversing single linked list
        currentSnakePart = self.snake.head
        while (currentSnakePart):
            tag = currentSnakePart.options["tag"]
            if currentSnakePart.moveDirection == 'Left':
                self.snakeBoard.move(tag, -PIECE_SIZE, 0)
            elif currentSnakePart.moveDirection == 'Right':
                self.snakeBoard.move(tag, PIECE_SIZE, 0)
            elif currentSnakePart.moveDirection == 'Up':
                self.snakeBoard.move(tag, 0, -PIECE_SIZE)
            elif currentSnakePart.moveDirection == 'Down':
                self.snakeBoard.move(tag, 0, PIECE_SIZE)
            currentSnakePart = currentSnakePart.next
        #self.moveTail()

    # loop through every tail piece and update move direction from its parent
    def propogateNewMove(self):

        currentSnakePart = self.snake.head
        while (currentSnakePart.next):
            currentSnakePart.next.moveDirection = currentSnakePart.moveDirection
            currentSnakePart = currentSnakePart.next

    def moveTail(self):
        # fairly standard way of traversing single linked list
        currentSnakePart = self.snake.head.next
        while (currentSnakePart):
            tag = currentSnakePart.options["tag"]
            if currentSnakePart.moveDirection == 'Left':
                self.snakeBoard.move(tag, -PIECE_SIZE, 0)
            elif currentSnakePart.moveDirection == 'Right':
                self.snakeBoard.move(tag, PIECE_SIZE, 0)
            elif currentSnakePart.moveDirection == 'Up':
                self.snakeBoard.move(tag, 0, -PIECE_SIZE)
            elif currentSnakePart.moveDirection == 'Down':
                self.snakeBoard.move(tag, 0, PIECE_SIZE)
            currentSnakePart = currentSnakePart.next

    # check for snake_head overlapping any side or apples
    # TODO: also check snake_head overlapping any snake body parts
    def processDetection(self):
        # obtain current head
        snakeHeadCoords = self.snakeBoard.coords(
            self.snake.head.options["tag"])

        # get tuple of objects over snake head location
        overlappingObjects = self.snakeBoard.find_overlapping(
            snakeHeadCoords[0], snakeHeadCoords[1], snakeHeadCoords[2],
            snakeHeadCoords[3])
        # if length of returned tupled is greater than 1, snake head
        # is on something
        if (len(overlappingObjects) > 1):
            print("apple id %d" % self.apple_id)
            # hacky, but we only care about one object overlapping head
            # and we know head is always the 5th cavas item made
            if (overlappingObjects[0] < 5):
                self.app_state['collision_detected'] = True
            # all apples are made after snake
            elif (overlappingObjects[1] == self.apple_id):
                self.updateScore(self.score.get() + 1)
                self.addTail()
                self.generateApple()
            # TODO: tail collision
            else:
                print(overlappingObjects)
                print("tail collision")
                pass

    def addTail(self):
        # get item we are appending to
        tailCoord_x = self.snakeBoard.coords(
            self.currentTailNode.options["tag"])[0]
        tailCoord_y = self.snakeBoard.coords(
            self.currentTailNode.options["tag"])[1]
        # apply correction to tail coordinates based on current direction of
        # last tail
        tailDirect = self.currentTailNode.moveDirection
        # the '1' offset ensures snake pieces are not considered overlapping
        if tailDirect == "Left":
            offset_x = PIECE_SIZE + 1
            offset_y = 0
        elif tailDirect == "Right":
            offset_x = -PIECE_SIZE - 1
            offset_y = 0
        elif tailDirect == "Down":
            offset_x = 0
            offset_y = -PIECE_SIZE - 1
        elif tailDirect == "Up":
            offset_x = 0
            offset_y = PIECE_SIZE + 1
        # build tail options
        tail_options = {
            "id": SnakeNode.class_id,
            "coord_x": tailCoord_x + offset_x,
            "coord_y": tailCoord_y + offset_y,
            "color": SNAKE_TAIL_COLOR,
            "tag": "snake_tail_" + str(SnakeNode.class_id)
        }
        newTail = SnakeNode(tailDirect, self.snakeBoard, tail_options)
        # set old tail's child to new tail
        self.currentTailNode.next = newTail
        # replace current tail status
        self.currentTailNode = newTail


class SnakeLinkedList:
    def __init__(self):
        self.head = None


class SnakeNode:
    # create a new node
    '''
    params:
        currentMoveDirection: string
        nextMoveDirection: string
        board: SnakeBoard Canvas
        options: dictionary
            {id, coord_x, coord_y, color, tag}
        next: SnakeNode child
    '''
    # current id to use
    class_id = 0

    def __init__(self, direction, board, options, next=None):
        print("making new tail", direction, options)
        self.id = options["id"]
        self.moveDirection = direction
        self.next = next
        self.options = options
        board.create_oval(options["coord_x"],
                          options["coord_y"],
                          options["coord_x"] + PIECE_SIZE,
                          options["coord_y"] + PIECE_SIZE,
                          fill=options["color"],
                          tags=options["tag"])
        self.class_id = self.class_id + 1


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