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
    FAITH_JUMP = -1

class STATUS(Enum):
    DONE = 0
    MOVING = 1

class GameGraph:
    def __init__(self) -> None:
        self.node_array = np.full((16,20),None, dtype=object) #generate blank matrix witt 16 rows and 20 cols which is the size of the gamespace

    def add_node(self,row,col):
        self.node_array[row,col] = Node()

    def clear(self):
        for i,row in enumerate(self.node_array):
            for j,col in enumerate(row):
                #delete:
                self.node_array[i,j] = None

class Node:
    def __init__(self):   
        self.edge_list = deque()
        self.visited = False
        self.cost = 0
        self.parent = [0,0]
        self.parent_link = None
    
    def add_edge(self,row, col, link_type):
        self.edge_list.append(Edge(row,col,link_type))


class Edge:
    def __init__(self,finish_row,finish_col,link_type: LINK):
        self.finish_row = finish_row
        self.finish_col = finish_col
        self.link_type = link_type

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

    def run_action(self, current_row,current_col,edge: Edge, enemy_list: deque):
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """
        #release all buttons which may be held down from previous action
        self.release_all()
        [enemy_row, enemy_col] = self.get_nearest_enemy(current_row,current_col,enemy_list)

        #if an edge has been passed execute it
        if edge:
            if edge.link_type.value == LINK.WALK.value:
                status = self.walk(current_col,edge,enemy_col)
            elif edge.link_type.value == LINK.FALL.value:
                status = self.fall(current_row,current_col,edge,enemy_col),
            elif edge.link_type.value == LINK.JUMP.value:
                status = self.jump(current_row,current_col,edge,enemy_row,enemy_col)
            elif edge.link_type.value == LINK.FAITH_JUMP.value:
                status = self.faith(current_row,current_col,edge,enemy_row,enemy_col)
        #An edge has not been passed, go right by default
        else:
            self.pyboy.send_button(self.valid_actions[ACTION.RIGHT.value])

        # Simply toggles the buttons being on or off for a duration of act_freq
        # self.pyboy.send_input(self.valid_actions[action])
        for _ in range(self.act_freq):
            self.pyboy.tick()

        return
    
    def get_nearest_enemy(self,row,col,enemies: deque):
        min = [100,100]
        if len(enemies) > 0:
            for enemy in enemies:
                #get the enemy with the lowest col distance from mario
                if abs(enemy[1] - col) <= 10:
                    min = enemy
                
            return min
        else:
            return [-1,-1] 
    
    def send_button(self,buttons: list):
        for button in buttons:
            self.pyboy.send_input(self.valid_actions[button])
        return
    
    def release_all(self):
        """
        Used to release all buttons
        """
        for button in range(len(self.release_button)):
            self.pyboy.send_input(self.release_button[button])
        return
    
    def walk(self,col,edge: Edge,enemy_col) -> STATUS:
        #Check if on the target
        if col == edge.finish_col:
            return STATUS.DONE
        #If enemy exists that is within 2 cols
        elif (abs(col-enemy_col) <= 4) and enemy_col > -1:
            #check if the enemy is above or below
            if (col == enemy_col):
                #dodge backwards
                self.send_button([ACTION.LEFT.value])
                return STATUS.MOVING
            #if the enemy isn't above sit still so we can jump over and fight it
            else:
                self.release_all()
                return STATUS.DONE
        #Check if to the left of target
        elif col < edge.finish_col:
            self.send_button([ACTION.RIGHT.value])
            return STATUS.MOVING
        #Check if to the right of the target
        elif col > edge.finish_col:
            self.send_button([ACTION.LEFT.value])
            return STATUS.MOVING
        
    def fall(self,row,col,edge: Edge,enemy_col) -> STATUS:
        #Check if on the target
        if col == edge.finish_col and row == edge.finish_row:
            return STATUS.DONE
        #Check if above the target but still falling
        elif col == edge.finish_col:
            self.send_button([ACTION.DOWN.value])
            return STATUS.MOVING
        elif col < edge.finish_col:
            self.send_button([ACTION.RIGHT.value])
            return STATUS.MOVING
        #Check if to the right of the target
        elif col > edge.finish_col:
            self.send_button([ACTION.LEFT.value])
            return STATUS.MOVING
        
    def jump(self,row,col,edge: Edge,enemy_row,enemy_col) -> STATUS:
        #Check if on the target
        if col == edge.finish_col and row == edge.finish_row:
            return STATUS.DONE
        
        #else if there is no enemy or no enemy within 1 tiles of mario or mario is on the ground and can jump over, or mario is in the air but still has speed and can jump over
        # C208       1    Mario's Y speed. (0x00 (a lot of speed) to 0x19 (no speed, top of jump)) (unintentionally reaches 0x1a and 0xff)
        # C20A       1    Mario is on the ground flag (0x01 = On the ground, 0x00 = In the air)
        # | (self._read_m(0xC208) <=0x15)
        elif (enemy_row == -1) | (abs(enemy_col-col) > 4 and abs(enemy_row-row) > 2) | (self._read_m(0xC20A) == 1):
            #Check if on the same  or above row but to the left
            if row <= edge.finish_row and col < edge.finish_col:
                self.send_button([ACTION.RIGHT.value])
                return STATUS.MOVING
            #Check if on the same or above row but to the right
            elif row <= edge.finish_row and col > edge.finish_col:
                self.send_button([ACTION.LEFT.value])
                return STATUS.MOVING
            #Check if too low
            # C207       1    Probably used in Mario's jump routine. (0x00 = Not jumping, 0x01 = Ascending, 0x02 = Descending)
            elif row > edge.finish_row and self._read_m(0xC207) != 0x02:
                self.send_button([ACTION.BUTT_A.value,ACTION.RIGHT.value])
                return STATUS.MOVING
            
        #an enemy is within two tiles of mario and mario is already in the air 
        else:
            #if on the same level or below AVOID
            if (row > enemy_row):
                #check if mario is to the left or under of enemy
                if (col <= enemy_col):
                    #Avoid left
                    self.send_button([ACTION.LEFT.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING

                #must be to the right of enemy
                else:
                    #Avoid right
                    self.send_button([ACTION.RIGHT.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING

            #higher than enemy then ATTACK
            elif (row < enemy_row):
                #Check if to the left
                if (col < enemy_col):
                    #steer above
                    self.send_button([ACTION.RIGHT.value])
                    return STATUS.MOVING
                #check if to the right
                elif(col > enemy_col) and (abs(col-enemy_col) < 1):
                    self.send_button([ACTION.LEFT.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING
                #must be above
                else:
                    #STOMP
                    self.send_button([ACTION.DOWN.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING
                
    def faith(self,row,col,edge: Edge,enemy_row,enemy_col) -> STATUS:
        #Check if on the target
        if col == edge.finish_col and row == edge.finish_row:
            return STATUS.DONE
        
        #else if there is no enemy or no enemy within 1 tiles of mario or mario is on the ground and can jump over, or mario is in the air but still has speed and can jump over
        # C208       1    Mario's Y speed. (0x00 (a lot of speed) to 0x19 (no speed, top of jump)) (unintentionally reaches 0x1a and 0xff)
        # C20A       1    Mario is on the ground flag (0x01 = On the ground, 0x00 = In the air)
        # | (self._read_m(0xC208) <=0x15)
        elif (enemy_row == -1) | (abs(enemy_col-col) > 4 and abs(enemy_row-row) > 2) | (self._read_m(0xC20A) == 1):
            #Check if on the same  or above row but to the left
            if row < edge.finish_row and col < edge.finish_col:
                self.send_button([ACTION.RIGHT.value,ACTION.BUTT_B.value])
                return STATUS.MOVING
            #Check if on the same or above row but to the right
            elif row <= edge.finish_row and col > edge.finish_col:
                self.send_button([ACTION.LEFT.value,ACTION.BUTT_B.value])
                return STATUS.MOVING
            #Check if too low or on same level
            # C207       1    Probably used in Mario's jump routine. (0x00 = Not jumping, 0x01 = Ascending, 0x02 = Descending)
            elif row >= edge.finish_row and self._read_m(0xC207) != 0x02:
                self.send_button([ACTION.RIGHT.value,ACTION.BUTT_A.value,ACTION.BUTT_B.value])
                return STATUS.MOVING
            
        #an enemy is within two tiles of mario and mario is already in the air 
        else:
            #higher than enemy then ATTACK
            if (row < enemy_row) and abs(col - enemy_col) < 4:
                #Check if to the left
                if (col < enemy_col):
                    #steer above
                    self.send_button([ACTION.RIGHT.value])
                    return STATUS.MOVING
                #check if to the right
                elif(col > enemy_col) and (abs(col-enemy_col) < 1):
                    self.send_button([ACTION.LEFT.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING
                #must be above
                else:
                    #STOMP
                    self.send_button([ACTION.DOWN.value,ACTION.BUTT_B.value])
                    return STATUS.MOVING
            #if on the same level or below AVOID
            else:
                #check if mario is to the left or under of enemy
                if (col <= enemy_col):
                    #Avoid left
                    self.send_button([ACTION.LEFT.value,ACTION.BUTT_B.value,ACTION.DOWN.value])
                    return STATUS.MOVING

                #must be to the right of enemy
                else:
                    #Avoid right
                    self.send_button([ACTION.RIGHT.value,ACTION.BUTT_B.value,ACTION.DOWN.value])
                    return STATUS.MOVING



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
        self.mario_col = 0
        self.mario_row = 0
        self.status = STATUS.DONE
        self.edge = None

    def choose_action(self):
        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        self.gamespace = self.environment.game_area()
        self.generate_graph()
        self.get_mario_pos()



        #get the path based on Marios position
        visited_list = deque()
        predecessor_list = deque()
        #execute actions
        #Dijkstra only executes when mario is on the ground which is kinda bad cuz he jumps alot
        try:
            path = self.dijkstra(self.mario_row,self.mario_col,16,visited_list,predecessor_list)
            return self.gamegraph.node_array[path[1][0],path[1][1]].parent_link
        except:
            return
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
        # return ACTION.RIGHT.value
    
    def generate_graph(self):
        """
        This method must be called after the gamespace has been generated. It uses the gamespace to generate a traversible linked graph. The transversible links are predefined i.e walk link, jump link, big jump link, fall link, pipe link
        """
   
        self.gamegraph.clear()


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
                        self.check_faith_link(i,j)
        return
    
    def check_node_valid(self,row,col):
        """Returns true if mario can stand on the node"""
        if (row > 2) and (self.gamespace[row-1][col] <= 9) and (self.gamespace[row][col] >= 10):
            return True
        else:
            return False
        
    def check_empty(self,row,col):
        """Returns true if the area above the node is empty i.e zero"""
        if (row > 2) and (self.gamespace[row-1][col] <= 9) :
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
        if (column != 0) and (self.gamespace[row][column-1] <= 9):
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
        if (column < len(self.gamespace[row]) - 1) and (self.gamespace[row][column+1] <= 9):
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
        """A jump link is for nodes up to 4 blocks seperation vertically and 1 block seperation horizontally"""
        #check for nodes to the left
        scan_height = 4
        col_temp = column - 1
        row_temp = row
        if (col_temp >= 0) and (row-scan_height >= 0):
            for i in range(1,scan_height+1):
                if (self.check_empty(row_temp-i,column) == True) and (self.check_node_valid(row_temp-i,col_temp)):
                    #jump link has been found
                    if (self.check_node_exist(row_temp-i,col_temp) == False):
                        self.gamegraph.add_node(row_temp-i,col_temp)
                    self.gamegraph.node_array[row,column].add_edge(row_temp-i,col_temp,LINK.JUMP)
        
        #check for nodes to the right
        col_temp = column + 1
        row_temp = row
        if (col_temp < len(self.gamespace[row])) and (row-scan_height >= 0):
            for i in range(1,scan_height+1):
                if (self.check_empty(row_temp-i,column) == True) and (self.check_node_valid(row_temp-i,col_temp)):
                    #jump link has been found
                    if (self.check_node_exist(row_temp-i,col_temp) == False):
                        self.gamegraph.add_node(row_temp-i,col_temp)
                    self.gamegraph.node_array[row,column].add_edge(row_temp-i,col_temp,LINK.JUMP)
        return

    def check_faith_link(self,row,column):
        """A faith jump link is for nodes up to 4 blocks seperation horizontally and 2 blocks seperation horizontally"""
        #check for nodes to the left
        scan_height = 2
        scan_width = 4
        for i in range(-scan_height-1,scan_height+1):
            for j in range(-scan_width-1,scan_width+1):
                try:
                    if (self.check_empty(row+i,column+j) == True) and (self.check_node_valid(row+i,column+j)):
                        #faith link has been found
                        if (self.check_node_exist(row+i,column+j)) == False:
                            #make a node at destination
                            self.gamegraph.add_node(row+i,column+j)
                        self.gamegraph.node_array[row,column].add_edge(row+i,column+j,LINK.FAITH_JUMP)
                except:
                    # this exist for out of bound exceptions
                    pass
        return
                                 


    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """
        # run actions
        # if self.status.value == STATUS.DONE.value:
        #     edge = self.choose_action()
        # else:
        #     self.status = self.environment.run_action(self.mario_row,self.mario_col,edge)
        #     self.get_mario_pos()

        edge = self.choose_action()
        #if a new valid new edge exists
        if (edge != None):
            self.environment.run_action(self.mario_row,self.mario_col,edge,self.get_enemy_pos())
            self.edge = edge
        #otherwise a new edge does not exist, perhaps because mario is jumping
        else:
            self.environment.run_action(self.mario_row,self.mario_col,self.edge,self.get_enemy_pos())

        return


    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)


            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()


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

    def get_mario_pos(self):
        #updates the row and col that mario is currently located at
        self.mario_row = 0
        self.mario_col = 0
        for i, row in enumerate(self.gamespace):
        #Check if the node has neighbors
            for j,grid in enumerate(row):
                #Check if it is mario. Store the lower rightmost corner of mario
                if grid == 1:
                    self.mario_row = max(self.mario_row,i)
                    self.mario_col = max(self.mario_col,j)

        #remember mario must be standing on a brick, 
        self.mario_row += 1
        return

    def get_enemy_pos(self):
        #returns a list of coordinates for any enemys within 2 tiles of mario. Is -1 if no enemy
        enemy_list = deque()

        for i in range(-5,4):
            for j in range(-5,6):
                try:
                    if self.gamespace[self.mario_row+ i][self.mario_col + j] >= 15:
                        enemy_list.append([self.mario_row+i,self.mario_col+j])
                except:
                    #this exist for out of bound exceptions
                    pass
        return enemy_list

    def dijkstra(self,row,col,target,visited_list,predecessor_list:deque):

        #termination condition if made it to edge of screen or can't find path
        if col >= target or len(visited_list) > 50:
            predecessor_list.appendleft(self.gamegraph.node_array[row,col].parent)
            return predecessor_list
        #otherwise cost needs to be updated and next node returned
        else:
            max = 0
            next_node_row = 0
            next_node_col = 0
            visited_list.append([row,col])
            for coords in visited_list:
                x_coords = coords[1]
                y_coords = coords[0]
                current_vertex = self.gamegraph.node_array[y_coords,x_coords]
                for edge in current_vertex.edge_list:
                    #update cost for each reacheable node if there is a better way to get there (higher "cost" function which I know is backwards stfu)
                    if self.gamegraph.node_array[row,col].cost + self.edge_cost(edge) >= self.gamegraph.node_array[edge.finish_row,edge.finish_col].cost:
                        self.gamegraph.node_array[edge.finish_row,edge.finish_col].cost = self.gamegraph.node_array[row,col].cost + self.edge_cost(edge)#cost of current node + edge cost
                        #update parent coords
                        self.gamegraph.node_array[edge.finish_row,edge.finish_col].parent = [row,col]
                        #update parent edge
                        self.gamegraph.node_array[edge.finish_row,edge.finish_col].parent_link = edge
                        #set as next node
                        if self.gamegraph.node_array[edge.finish_row,edge.finish_col].cost > max:
                            next_node_row = edge.finish_row
                            next_node_col = edge.finish_col
                            max = self.gamegraph.node_array[edge.finish_row, edge.finish_col].cost
            [parent_row,parent_col] = self.dijkstra(next_node_row,next_node_col,target,visited_list,predecessor_list)[0] #return
            predecessor_list.appendleft(self.gamegraph.node_array[parent_row,parent_col].parent)
            return predecessor_list


    def edge_cost(self,edge: Edge):
        reward = edge.finish_col + edge.link_type.value*2
        return reward

        

#     #new functions
# def init_curses():
#     stdscr = curses.initscr()  # Initialize the screen
#     curses.curs_set(0)  # Hide the cursor
#     stdscr.nodelay(True)  # Make getch() non-blocking
#     curses.noecho()  # Do not display typed characters
#     curses.cbreak()  # Disable line buffering
#     return stdscr

# def cleanup_curses():
#     curses.nocbreak()  # Restore line buffering
#     curses.echo()  # Re-enable character echo
#     curses.endwin()  # End the curses application

# def create_popup(stdscr):
# # Clear the screen
# # Hide the cursor
#     curses.curs_set(0)

#     # Get the size of the terminal
#     height, width = stdscr.getmaxyx()

#     # Display a message in the center of the screen
#     message = "Welcome to the Curses Application!"
#     message_y = height // 2
#     message_x = (width - len(message)) // 2
#     stdscr.addstr(message_y, message_x, message)

#     # Display instructions
#     instructions = "Press 'q' to quit."
#     instructions_y = message_y + 2
#     instructions_x = (width - len(instructions)) // 2
#     stdscr.addstr(instructions_y, instructions_x, instructions)
#     # Refresh the screen to show the content
#     stdscr.refresh()    
