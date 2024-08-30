"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent
from enum import Enum, auto
import curses
from collections import deque

class ACTION(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    BUTT_A = 4
    BUTT_B = 5

class LINK(Enum):
    WALK = 0
    FALL = 1
    JUMP = 2
    FAITH_JUMP = 3

class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 1,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        # Simply toggles the buttons being on or off for a duration of act_freq
        self.pyboy.send_input(self.valid_actions[action])

        for _ in range(self.act_freq):
            self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])


class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None
        self.gamespace = None
        self.gamegraph = None

    def choose_action(self):
        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        self.gamespace = self.environment.game_area()
        self.gamegraph = self.generate_graph()


        # Implement your code here to choose the best action
        # time.sleep(0.1)
        # action = self.stdscr.getch()  # Non-blocking read
        # # action = input()  # Non-blocking read

        # if action == 97: #'a'
        #     return ACTION.LEFT.value
        # elif action == 100: #'d'
        #     return ACTION.RIGHT.value
        # elif action == 115: #'s'
        #     return ACTION.DOWN.value
        # elif action == 119: #'w'
        #     return ACTION.UP.value
        # elif action == 98: #'b'
        #     return ACTION.BUTT_B.value
        # elif action == 110: #'n'
        #     return ACTION.BUTT_A.value

        # #Defult option
        # return ACTION.UP.value
        # return random.randint(0, len(self.environment.valid_actions) - 1)
        return ACTION.RIGHT.value
    
    def generate_graph(self) -> None:
        """
        This method must be called after the gamespace has been generated. It uses the gamespace to generate a traversible linked graph. The transversible links are predefined i.e walk link, jump link, big jump link, fall link, pipe link
        """
        for row in self.gamespace:
            #Check if the node has neighbors
            for column in row:

                #Check if it is a brick. In the gamespace anything with a value greater than 10 mario can stand on
                if self.gamespace[row][column] >= 10:
                    #Check fall links
                    #Check walk links
                    #Check jump links
                    #Check faith jump links
                    pass
                else:
                    pass
        return
    
    def check_fall_link(row,column,node,self):
        #check for empty space left
        if (column != 0) and (self.gamespace[row][column-1] == 0):
            #check for platform below
            platform_found = False
            while row < len(self.gamespace) and platform_found == False:
                #check if the current node is a brick
                if self.gamespace[row][column] >= 10:
                    #A fall link has been found
                    #node.add_link(start_node,finish_node,link_type)
                    pass

        #check for empty space to right    
        if (column-1 != len(self.gamespace[row])) and (self.gamespace[row][column+1] == 0):
            #check for platform below
            pass


        return

    def check_walk_link(row,column,self):
        return
    def check_jump_link(row,column,self):
        return
    def check_faith_link(row,column,self):
        return
    
                                                                            


    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...
        action = self.choose_action()

        # Run the action on the environment
        self.environment.run_action(action)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)
        #
        self.stdscr = init_curses()
        self.stdscr.clear()
        create_popup(self.stdscr)
        # self.popup_Win = create_popup(self.stdscr)
        #
        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)


            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()
        #
        cleanup_curses()


    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()

    


    #new functions
def init_curses():
    stdscr = curses.initscr()  # Initialize the screen
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Make getch() non-blocking
    curses.noecho()  # Do not display typed characters
    curses.cbreak()  # Disable line buffering
    return stdscr

def cleanup_curses():
    curses.nocbreak()  # Restore line buffering
    curses.echo()  # Re-enable character echo
    curses.endwin()  # End the curses application

def create_popup(stdscr):
# Clear the screen
# Hide the cursor
    curses.curs_set(0)

    # Get the size of the terminal
    height, width = stdscr.getmaxyx()

    # Display a message in the center of the screen
    message = "Welcome to the Curses Application!"
    message_y = height // 2
    message_x = (width - len(message)) // 2
    stdscr.addstr(message_y, message_x, message)

    # Display instructions
    instructions = "Press 'q' to quit."
    instructions_y = message_y + 2
    instructions_x = (width - len(instructions)) // 2
    stdscr.addstr(instructions_y, instructions_x, instructions)
    # Refresh the screen to show the content
    stdscr.refresh()    

    
class GameGraph:
    def __init__(self) -> None:
        self.node_list = deque()

    def add_node(self,row,col):
        self.node_list.append((Node(row,col)))


class Node:
    def __init__(self,row,col):
        self.row = row
        self.col = col        
        self.edge_list = deque()
    
    def add_edge(self,finish,link_type):
        self.edge_list.append(Edge(self,finish,link_type))

class Edge:
    def __init__(self,start,finish,link_type):
        self.start = start
        self.finish = finish
        self.link_type = link_type