import random
import pdb
from tkinter import *
from itertools import chain

# App styling
# TODO: cooler colors. or let the user set them
APP_EMPHASIS_COLOR = 'dodger blue'
APP_BACKGROUND_COLOR = 'royal blue'
BUTTON_COLOR = 'sky blue'
FONT_COLOR = 'azure'
SNAKE_BOARD_COLOR = 'white'
LOSE_COLOR = 'red'
SNAKE_HEAD_COLOR = 'black'
SNAKE_TAIL_COLOR = 'purple'
APPLE_COLOR = 'green'

# Game settings
# TODO: implement a difficulty setting for the user that updates these values
BOARD_WIDTH = 300  # pixels
BOARD_HEIGHT = 300  # pixels
PIECE_SIZE = 10  # pixels
# no points for the snake head, so minus 1
MAX_SCORE = BOARD_WIDTH * BOARD_HEIGHT - 1  # apples
GAME_SPEED = 150  # ms
# apples cannot be placed within 10 pixels of the boundary
ALLOWED_APPLE_RANGE = range(10, 290, PIECE_SIZE)
# snake starts at least 100 pixels from any boundary
ALLOWED_SNAKE_START_RANGE = range(100, 200, PIECE_SIZE)
'''
Program flow:
    create splash page
    when Play is clicked, create game page
    Lauch game logic exec loop:
        Executed at GAME_SPEED
        On first snake movement, game begins
        Snake auto-movement in direction of last press
        Constant collision detection and apple capture detection starts
    While being played,
        tkinter after() is used to run a loop along side mainloop()
            do snake movement, redraws snake every game cycle:
                head moves, possibly in a new direction
                all tail pieces move
            check for detection:
                boudaries: fail
                apples: success
                tail pieces: fail
            on success:
                add tail piece
                make new apple, which:
                    cannot be on current snake
                    cannot be within 10 pixels of boundary
            on fail:
                stop capturing movement
                reset various app states
            on Play Again:
                finish cleaning up app states
                destroy and re-create snake board
            await for first snake movement and start again!
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

    # current score and tail segments
    score = None

    # To track snakeNodes
    # Could (and properly, should) have used a LinkedList parent
    # class to manage the SnakeNodes, but it seemed like too much
    # overhead for this project
    snakeHead = None
    currentTail = None

    # using this allows us to capture multiple snake commands
    # between draw cycles
    currentDirection = None

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
                self.collisionDetectedActions()
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

    # create the main snake board and snake head
    def createSnakeBoard(self):
        self.snakeBoard = Canvas(self.upperFrame,
                                 bg=SNAKE_BOARD_COLOR,
                                 width=BOARD_WIDTH,
                                 height=BOARD_HEIGHT)

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
            "tag": "snake_head",
            "direction": None,
            "nextDirection": None
        }
        # make snake head node
        self.snakeHead = SnakeNode(board=self.snakeBoard, options=head_options)
        # on start, tail is head
        self.currentTail = self.snakeHead

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
                                    BOARD_HEIGHT,
                                    width=1,
                                    fill="green",
                                    tags="leftSide")
        self.snakeBoard.create_line(0,
                                    0,
                                    BOARD_WIDTH,
                                    0,
                                    width=1,
                                    fill="yellow",
                                    tags="topSide")
        self.snakeBoard.create_line(BOARD_WIDTH,
                                    0,
                                    BOARD_WIDTH,
                                    BOARD_HEIGHT,
                                    width=1,
                                    fill="blue",
                                    tags="rightSide")
        self.snakeBoard.create_line(0,
                                    BOARD_HEIGHT,
                                    BOARD_WIDTH,
                                    BOARD_HEIGHT,
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
                self.snakeHead.options["tag"])
            self.snakeBoard.create_oval(appleCoord_x,
                                        appleCoord_y,
                                        appleCoord_x + PIECE_SIZE,
                                        appleCoord_y + PIECE_SIZE,
                                        fill=APPLE_COLOR,
                                        tags="apple")
            # exactly 1 means the only item overlapping the area of interest
            # is the apple, which is what we want
            if self.checkIfAppleOnSnake(
                    appleCoord_x,
                    appleCoord_y,
            ) == 1:
                # get apple id. remember that find_overlapping returns a tuple
                self.apple_id = self.snakeBoard.find_overlapping(
                    appleCoord_x, appleCoord_y, appleCoord_x + PIECE_SIZE,
                    appleCoord_y + PIECE_SIZE)[0]
                break

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
    def collisionDetectedActions(self):
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
        self.score.set(0)
        # Re-create board
        self.snakeBoard.destroy()
        self.createSnakeBoard()

    # capture user commands for snake movement
    def updateSnakeMovement(self, event):
        pressedKey = event.keysym

        # game starts on first move
        if (self.app_state['game_active'] == False):
            self.app_state['game_active'] = True
            self.snakeHead.options['direction'] = pressedKey
            self.currentDirection = pressedKey
        else:
            # set head move direction from key event
            # only update move if it's an allowed move
            if self.currentDirection == "Left" and pressedKey != "Right":
                self.snakeHead.options['direction'] = pressedKey
            elif self.currentDirection == "Up" and pressedKey != "Down":
                self.snakeHead.options['direction'] = pressedKey
            elif self.currentDirection == "Right" and pressedKey != "Left":
                self.snakeHead.options['direction'] = pressedKey
            elif self.currentDirection == "Down" and pressedKey != "Up":
                self.snakeHead.options['direction'] = pressedKey

        self.snakeHead.options['nextDirection'] = self.snakeHead.options[
            'direction']

    # continually redraw snake head in current movement direction
    def processMovement(self):
        '''
        To move the snake, start at the head and move each tail according to 
        it's saved direction. After the move, each tail piece needs to update it's 
        direction from it's parent
        '''
        # fairly standard way of traversing single linked list
        currentSnakePart = self.snakeHead
        while (currentSnakePart):
            tag = currentSnakePart.options["tag"]
            if currentSnakePart.options['direction'] == 'Left':
                self.snakeBoard.move(tag, -PIECE_SIZE, 0)
            elif currentSnakePart.options['direction'] == 'Right':
                self.snakeBoard.move(tag, PIECE_SIZE, 0)
            elif currentSnakePart.options['direction'] == 'Up':
                self.snakeBoard.move(tag, 0, -PIECE_SIZE)
            elif currentSnakePart.options['direction'] == 'Down':
                self.snakeBoard.move(tag, 0, PIECE_SIZE)
            currentSnakePart = currentSnakePart.next

        self.currentDirection = self.snakeHead.options['direction']
        # after move, update all tail segments for next cycle move
        self.propogateNewMove()

    # loop through every tail piece and update move direction from its parent
    def propogateNewMove(self):
        currentSnakePart = self.snakeHead
        while (currentSnakePart):
            # If more tail exists, propogate move direction before updating self direction
            if (currentSnakePart.next):
                currentSnakePart.next.options[
                    'nextDirection'] = currentSnakePart.options['direction']
            currentSnakePart.options['direction'] = currentSnakePart.options[
                'nextDirection']
            currentSnakePart = currentSnakePart.next

    # check for snake_head hitting any side, self, or apples
    def processDetection(self):
        '''
        Item                Index
            bounds           1-4
            snake head       5
            apple            self.apple_id
        from find_overlapping, expect tuple:
            (element_1, element_2)

        Any touched items will be considered 'overlapping'
        find_overlapping returns a tuple of items in the bound, referenced by
        their index, which is determined by the order they are drawn on board

        Note:
            The first tail created, the 'neck', is drawn on pixels that overlap
            the head. This threw off the original detection logic. After some experimenting,
            decided it was best to if the head only detected collisions in 'front'
            of it.
            'Front' is defined as a small rectangle in front of the head. This prevents
            detection logic from going off when snake head travels next to snake tails
        '''
        # obtain current head
        snakeHeadCoords = self.snakeBoard.coords(self.snakeHead.options["tag"])

        # only find overlapping objects in 'front' portion of head
        # search for objects on the head, with an 1 pixel offset so
        # head does not detect neck as 'overlapping'
        headDirection = self.snakeHead.options["direction"]
        if headDirection == "Left":
            overlappingObjects = self.snakeBoard.find_overlapping(
                snakeHeadCoords[0], snakeHeadCoords[1] + 1, snakeHeadCoords[0],
                snakeHeadCoords[3] - 1)
        elif headDirection == "Right":
            overlappingObjects = self.snakeBoard.find_overlapping(
                snakeHeadCoords[2], snakeHeadCoords[1] + 1, snakeHeadCoords[2],
                snakeHeadCoords[3] - 1)
        elif headDirection == "Down":
            overlappingObjects = self.snakeBoard.find_overlapping(
                snakeHeadCoords[0] + 1, snakeHeadCoords[3],
                snakeHeadCoords[2] - 1, snakeHeadCoords[3])
        elif headDirection == "Up":
            overlappingObjects = self.snakeBoard.find_overlapping(
                snakeHeadCoords[0] + 1, snakeHeadCoords[1],
                snakeHeadCoords[2] - 1, snakeHeadCoords[1])

        # tuple will always have len of 1, for the snake head. Anything greater
        # means it hit something
        if (len(overlappingObjects) > 1):
            # second element not apple, collided with something bad
            if (overlappingObjects[1] != self.apple_id):
                self.app_state['collision_detected'] = True
            else:
                # apple captured
                # because special tkinter variables
                self.score.set(self.score.get() + 1)
                # did they win?
                if (self.score.get() != MAX_SCORE):
                    self.addTail()
                    self.generateApple()
                else:
                    # handle win condition
                    pass

    # append a new tail segment to the end of the snake
    def addTail(self):
        # get item we are appending to
        tailCoord_x = self.snakeBoard.coords(
            self.currentTail.options["tag"])[0]
        tailCoord_y = self.snakeBoard.coords(
            self.currentTail.options["tag"])[1]

        # Place new tail 'behind' snake
        # apply correction to new tail coordinates based on direction of
        # current tail
        tailDirect = self.currentTail.options["direction"]
        if tailDirect == "Left":
            offset_x = PIECE_SIZE
            offset_y = 0
        elif tailDirect == "Right":
            offset_x = -PIECE_SIZE
            offset_y = 0
        elif tailDirect == "Down":
            offset_x = 0
            offset_y = -PIECE_SIZE
        elif tailDirect == "Up":
            offset_x = 0
            offset_y = PIECE_SIZE
        # build tail options
        tail_options = {
            "id": self.score.get(),
            "coord_x": tailCoord_x + offset_x,
            "coord_y": tailCoord_y + offset_y,
            "color": SNAKE_TAIL_COLOR,
            "tag": "snake_tail_" + str(self.score.get()),
            "direction": tailDirect,
            "nextDirection": None
        }
        newTail = SnakeNode(self.snakeBoard, tail_options)

        self.currentTail.options['nextDirection'] = tailDirect
        self.currentTail.next = newTail
        # replace current tail with new tail
        self.currentTail = newTail


class SnakeNode:
    # represents any segment of the snake, head included
    # Linked List felt like the right call because of the need to:
    #   1. have a list. Need to track each snake segment for collision purposes
    #   2. dynamically grow that list
    #   3. have each list item communicate data to the next list item, specifically,
    #       which direction to move
    '''
    params:
        board: SnakeBoard Canvas
        options: dictionary
            {coord_x, coord_y, color, tag, direction, nextDirection}
        next: SnakeNode child
    '''
    def __init__(self, board, options, next=None):
        self.next = next
        self.options = options
        board.create_oval(options["coord_x"],
                          options["coord_y"],
                          options["coord_x"] + PIECE_SIZE,
                          options["coord_y"] + PIECE_SIZE,
                          fill=options["color"],
                          tags=options["tag"])


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