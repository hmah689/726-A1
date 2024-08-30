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
import numpy as np

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
        self.gamegraph = GameGraph() #create an empty list of nodes

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
        for i, row in enumerate(self.gamespace):
            #Check if the node has neighbors
            for j,grid in enumerate(row):
                #Check if it is a brick. In the gamespace anything with a value greater than 10 mario can stand on
                if grid >= 10:
                    if self.check_node_valid(i,j) == False:
                        pass
                    else:
                        if self.check_node_exist(i,j) == False:
                        #create a node
                            self.gamegraph.add_node(i,j)

                        self.check_fall_link(i,j)
                        self.check_walk_link(i,j)
                        self.check_jump_link(i,j)
                        #Check faith jump links
        return
    
    def check_node_valid(self,row,col):
        """Returns true if mario can stand on the node"""
        if (row > 2) and (self.gamespace[row-1][col] <= 1) and (self.gamespace[row-2][col] <= 1) and (self.gamespace[row][col] >= 10):
            return True
        else:
            return False
        
    def check_empty(self,row,col):
        """Returns true if the area above the node is empty i.e zero"""
        if (row > 2) and (self.gamespace[row-1][col] <= 1) and (self.gamespace[row-2][col] <= 1):
            return True
        else:
            return False
        
    def check_node_exist(self,row,col):
        """Returns zero if there is no node present at the specified row col position"""
        if self.gamegraph.node_array[row,col] == None:
            return False
        else:
            return True
    
    def check_fall_link(self,row,column):
        #check for empty space left
        if (column != 0) and (self.gamespace[row][column-1] <= 1):
            #check for platform below
            platform_found = False
            row_temp = row
            col_temp = column - 1
            while row_temp < len(self.gamespace) and platform_found == False:
                #check if the current node is a brick
                if self.gamespace[row_temp][col_temp] >= 10:
                    #A fall link has been found
                    if self.check_node_exist(row_temp,col_temp) == False:
                        self.gamegraph.add_node(row_temp,col_temp)
                    #add a link
                    self.gamegraph.node_array[row,column].add_edge(row_temp,col_temp,LINK.FALL)
                    platform_found = True
                else:
                    row_temp+=1

        #check for empty space right
        if (column < len(self.gamespace[row]) - 1) and (self.gamespace[row][column+1] <= 1):
            #check for platform below
            platform_found = False
            row_temp = row
            col_temp = column + 1
            while row_temp < len(self.gamespace) and platform_found == False:
                #check if the current node is a brick
                if self.gamespace[row_temp][col_temp] >= 10:
                    #A fall link has been found
                    if self.check_node_exist(row_temp,col_temp) == False:
                        self.gamegraph.add_node(row_temp,col_temp)
                    #add a link
                    self.gamegraph.node_array[row,column].add_edge(row_temp,col_temp,LINK.FALL)
                    platform_found = True
                else:
                    row_temp+=1
        return

    def check_walk_link(self,row,column):
        #check for nodes to the left
        col_temp = column - 1
        if (col_temp >= 0) and (self.gamespace[row][col_temp] >= 10):
            #make sure the node is valid
            if self.check_node_valid(row,col_temp) == False:
                pass
            else:
                #add a node if there isn't already one
                if self.check_node_exist(row,col_temp) == False:
                    self.gamegraph.add_node(row,col_temp)
                self.gamegraph.node_array[row,column].add_edge(row,col_temp,LINK.WALK)
        #check for node to the right
        col_temp = column + 1
        if (col_temp < len(self.gamespace[row])) and (self.gamespace[row][col_temp] >= 10):
            #make sure the node is valid
            if self.check_node_valid(row,col_temp) == False:
                pass
            else:
                #add a node if there isn't already one
                if self.check_node_exist(row,col_temp) == False:
                    self.gamegraph.add_node(row,col_temp)
                self.gamegraph.node_array[row,column].add_edge(row,col_temp,LINK.WALK)
        return
    
    def check_jump_link(self,row,column):
        """A jump link is for nodes up to 3 blocks seperation vertically and 1 block seperation horizontally"""
        #check for nodes to the left
        col_temp = column - 1
        row_temp = row
        if (col_temp >= 0) and (row-3 >= 0):
            for i in range(1,4):
                if (self.check_empty(row_temp-i,column) == True) and (self.check_node_valid(row_temp-i,col_temp)):
                    #jump link has been found
                    if (self.check_node_exist(row_temp-i,col_temp) == False):
                        self.gamegraph.add_node(row_temp-i,col_temp)
                    self.gamegraph.node_array[row,column].add_edge(row_temp-i,col_temp,LINK.JUMP)
        
        #check for nodes to the right
        col_temp = column + 1
        row_temp = row
        if (col_temp < len(self.gamespace[row])) and (row-3 >= 0):
            for i in range(1,4):
                if (self.check_empty(row_temp-i,column) == True) and (self.check_node_valid(row_temp-i,col_temp)):
                    #jump link has been found
                    if (self.check_node_exist(row_temp-i,col_temp) == False):
                        self.gamegraph.add_node(row_temp-i,col_temp)
                    self.gamegraph.node_array[row,column].add_edge(row_temp-i,col_temp,LINK.JUMP)
        return

    # def check_faith_link(row,column,self):
    #     return
    
                                                                            


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
        self.node_array = np.full((16,20),None, dtype=object) #generate blank matrix witt 16 rows and 20 cols which is the size of the gamespace

    def add_node(self,row,col):
        self.node_array[row,col] = Node()


class Node:
    def __init__(self):   
        self.edge_list = deque()
    
    def add_edge(self,row, col, link_type):
        self.edge_list.append(Edge(row,col,link_type))

class Edge:
    def __init__(self,finish_row,finish_col,link_type):
        self.finish_row = finish_row
        self.finish_col = finish_col
        self.link_type = link_type