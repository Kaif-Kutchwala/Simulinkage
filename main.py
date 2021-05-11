from math import asin, cos, sin, sqrt
import numpy as np
import pymunk, pygame, sys, pymunk.pygame_util
import time
from tkinter import filedialog
import tkinter as tk
import json
import logging
from pymunk_objects import Link, Anchor, Obstacle, Joint, Motor
from error import error
from kinematics_solver import forward_kinematics, inverse_kinematics
from ui_components import Screen, TextInput, Button, Text, DropDown, text_objects
from ui_components import xsmallfont, smallfont, mediumfont, largefont, xlargefont
from ui_components import white, black, grey, bright_grey, primary, primary_bright, secondary, secondary_bright

       
def main():
    #Create root window for errors and hide it
    root = tk.Tk()
    root.withdraw()

    #initialise pygame
    pygame.init()
    pygame.key.set_repeat(500,50)
    screen = pygame.display.set_mode((1200,750)) #create screen and set size to 1200x750
    pygame.display.set_caption('Simulinkage') #Set window title to 'Simulinkage'
    clock = pygame.time.Clock() #Create clock object (required for simulation)
    pymunk.pygame_util.positive_y_is_up = True #sets positive y in upward direction
    #store screen width and height in global variables
    s_width = screen.get_width() 
    s_height = screen.get_height()

    space = pymunk.Space() #Create space object to store objects and simulate
    space.gravity = (0, -100) #set gravity in y direction to -100
    space.damping = 0.95 #set damping to emulate wind resistance
    draw_options = pymunk.pygame_util.DrawOptions(screen) #Draws all objects added to space on screen

    #Initialise flags
    global grid_visible, paused, label, trace, cooldown
    grid_visible = True #flag to decide whether to draw grid on screen or not
    paused = True #flag to pause simulation
    label = False #flag to label objects in space
    trace = False #flag to trace links
    cooldown = False
    backspace = False
    cooldown_counter = 0

    #Initialise dictionaries to store information of elements
    global open_forward_solution, open_inverse_solution, inverse_message, forward_message, origin
    text_inputs = {}
    links = {}
    joints = {}
    obstacles = {}
    anchors = {}
    motors = {}
    links_to_trace = {}
    open_forward_solution = ''
    open_inverse_solution = ''
    inverse_message = ''
    forward_message = ''
    origin = [50,50]

    #create dictionaries to store information required for saving json files
    s_links = {}
    s_joints = {}
    s_obstacles = {}
    s_anchors = {}
    s_motors = {}

    #Create Text Inputs
    title_y = 20 #y height of title, all text inputs are drawn relative to this
    
    #Link configuration text inputs for kinematic anlaysis
    link_1_length_input = TextInput('open_link_length_1', 1010, 60, 90,15, 'length', section='kinematic')
    link_1_angle_input = TextInput('open_link_angle_1', 1100, 60, 90,15, 'angle', section='kinematic', prev=link_1_length_input )
    link_1_color_input = TextInput('open_link_color_1', 1010, 80, 180,15, 'color', section='kinematic', prev=link_1_angle_input )

    link_2_length_input = TextInput('open_link_length_2', 1010, 130, 90,15, 'length', section='kinematic', prev=link_1_color_input )
    link_2_angle_input = TextInput('open_link_angle_2', 1100, 130, 90,15, 'angle', section='kinematic', prev=link_2_length_input )
    link_2_color_input = TextInput('open_link_color_2', 1010, 150, 180,15, 'color', section='kinematic', prev=link_2_angle_input )

    link_3_length_input = TextInput('open_link_length_3', 1010, 200, 90,15, 'length', section='kinematic', prev=link_2_color_input)
    link_3_angle_input = TextInput('open_link_angle_3', 1100, 200, 90,15, 'angle', section='kinematic', prev=link_3_length_input)
    link_3_color_input = TextInput('open_link_color_3', 1010, 220, 180,15, 'color', section='kinematic' ,prev=link_3_angle_input)

    link_4_length_input = TextInput('open_link_length_4', 1010, 270, 90,15, 'length', section='kinematic', prev=link_3_color_input)
    link_4_angle_input = TextInput('open_link_angle_4', 1100, 270, 90,15, 'angle', section='kinematic', prev=link_4_length_input)
    link_4_color_input = TextInput('open_link_color_4', 1010, 290, 180,15, 'color', section='kinematic', prev=link_4_angle_input)

    link_5_length_input = TextInput('open_link_length_5', 1010, 340, 90,15, 'length', section='kinematic', prev=link_4_color_input)
    link_5_angle_input = TextInput('open_link_angle_5', 1100, 340, 90,15, 'angle', section='kinematic', prev=link_5_length_input)
    link_5_color_input = TextInput('open_link_color_5', 1010, 360, 180,15, 'color', section='kinematic', prev=link_5_angle_input)

    link_6_length_input = TextInput('open_link_length_6', 1010, 410, 90,15, 'length', section='kinematic', prev=link_5_color_input)
    link_6_angle_input = TextInput('open_link_angle_6', 1100, 410, 90,15, 'angle', section='kinematic', prev=link_6_length_input)
    link_6_color_input = TextInput('open_link_color_6', 1010, 430, 180,15, 'color', section='kinematic', prev=link_6_angle_input)

    link_7_length_input = TextInput('open_link_length_7', 1010, 480, 90,15, 'length', section='kinematic', prev=link_6_color_input)
    link_7_angle_input = TextInput('open_link_angle_7', 1100, 480, 90,15, 'angle', section='kinematic', prev=link_7_length_input)
    link_7_color_input = TextInput('open_link_color_7', 1010, 500, 180,15, 'color', section='kinematic', prev = link_7_angle_input)
    
    #Add Link
    link_x1_input = TextInput('x1', 1010, title_y + 20, 40, 15, 'x1', prev= None, section='link')
    link_y1_input = TextInput('y1', 1050, title_y + 20, 40, 15, 'y1', prev=link_x1_input, section='link')
    link_x2_input = TextInput('x2', 1090, title_y + 20, 40, 15, 'x2', prev=link_y1_input, section='link')
    link_y2_input = TextInput('y2', 1130, title_y + 20, 40, 15, 'y2', prev=link_x2_input, section='link')
    link_id_input = TextInput('link_id', 1010, title_y + 40, 80, 15, 'id', prev=link_y2_input, section='link')
    link_color_input = TextInput('link_color', 1090, title_y + 40, 80, 15, 'color', prev=link_id_input, section='link')
    #link_type_input = TextInput('link_type', 1170, title_y + 40, 20, 15, '1', prev=link_color_input, section='link')
    link_type_dropdown = DropDown('link_type', 1175, title_y + 20, 20, 15, smallfont, 't', {'F':'Fixed','D':'Dynamic'}, dd_type='fixed')
    
    #Add Joint
    joint_id_input = TextInput('joint_id', 1010, title_y +100, 90, 15, 'joint_id', prev=link_color_input, section='joint')
    joint_coords_input = TextInput('joint_coords', 1100, title_y +100, 90, 15, 'coordinates', prev=joint_id_input, section='joint')
    joint_object1_dropdown = DropDown('joint_object1', 1010, title_y + 120, 90, 15, smallfont, 'object 1', {})
    joint_object2_dropdown = DropDown('joint_object2', 1100, title_y + 120, 90, 15, smallfont, 'object 2', {})

    #Add Obstacle
    obstacle_sides_input = TextInput('obstacle_sides', 1010, title_y + 180, 90, 15, 'sides', prev=joint_coords_input, section='obstacle')
    obstacle_radius_input = TextInput('obstacle_radius', 1100, title_y + 180, 90, 15, 'radius', prev=obstacle_sides_input, section='obstacle' )
    obstacle_vertices_input = TextInput('obstacle_vertices', 1010, title_y + 200, 180, 15, 'vertices', prev=obstacle_radius_input, section='obstacle')
    obstacle_id_input = TextInput('obstacle_id', 1010, title_y + 220, 90, 15, 'id', prev=obstacle_vertices_input, section='obstacle')
    obstacle_color_input = TextInput('obstacle_color', 1100, title_y + 220, 70, 15, 'color', prev=obstacle_id_input, section='obstacle')
    #obstacle_type_input = TextInput('obstacle_type', 1170, title_y + 220, 20, 15, 't', prev=obstacle_color_input, section='obstacle')
    obstacle_type_dropdown = DropDown('obstacle_type', 1170, title_y + 220, 20, 15, smallfont, 't', {'F':'Fixed','D':'Dynamic'}, dd_type='fixed')
    
    #Add Motor
    motor_id_input = TextInput('motor_id', 1010, title_y +280, 90, 15, 'motor_id', prev=obstacle_color_input, section='motor')
    motor_limits_input = TextInput('motor_limits', 1100, title_y +280, 90, 15, 'limits', prev=motor_id_input, section='motor')
    motor_object1_dropdown = DropDown('motor_object1', 1010, title_y + 300, 60, 15, smallfont, 'object 1', {})
    motor_object2_dropdown = DropDown('motor_object2', 1070, title_y + 300, 60, 15, smallfont, 'object 2', {})
    motor_speed_input = TextInput('motor_speed', 1130, title_y + 300, 60, 15, 'speed', prev=motor_limits_input, section='motor')
    
    #Add Anchor
    anchor_id_input = TextInput('anchor_id', 1010, title_y + 360, 90, 15, 'id', prev=motor_speed_input, section='anchor')
    anchor_coords_input = TextInput('anchor_coords', 1100, title_y + 360, 90, 15, 'coordinates', prev=anchor_id_input, section='anchor')
    
    #Gravity
    gravity_input = TextInput('gravity', 1010, title_y + 440, 180, 15, 'gravity', prev=anchor_coords_input, section='gravity')
    
    #Delete Element
    delete_element_dropdown = DropDown('delete_id', 1010, title_y +500, 180, 15, smallfont, 'Select element', {})
    #delete_id_input = TextInput('delete_id', 1010, title_y +500, 180, 15, 'element_id', prev=gravity_input, section='delete')
    
    #Toggle Trace Link
    trace_object_dropdown = DropDown('trace_id', 1010, title_y + 560, 70, 15, smallfont, 'select', {})
    trace_pos_dropdown = DropDown('trace_pos', 1080, title_y + 560, 20, 15, smallfont, 'P', {'S':'Start', 'E':'End'}, dd_type='fixed')
    #trace_id_input = TextInput('trace_id', 1010, title_y + 560, 70, 15, 'link_id', prev=gravity_input, section='trace')
    #trace_pos_input = TextInput('trace_pos', 1080, title_y + 560, 20, 15, '1', prev=trace_id_input, section='trace')
    trace_color_input = TextInput('trace_color', 1100, title_y + 560, 90, 15, 'color', prev=gravity_input, section='trace')

    num_of_links_input = TextInput('num_links', 700, 300, 100, 50, '1-7', largefont, white, section='open_menu')
    
    end_effector_pos_input = TextInput('end_effector_pos', 1095, title_y + 610, 90, 15, 'target position', section=None)
    origin_input = TextInput('open_origin', 1065, title_y + 630, 120, 15, 'origin', prev=end_effector_pos_input, section=None)
    origin_input.set_text('0,0')

    #Create Screens
    mainMenu = Screen(screen, 'Main Menu', fill = (41,70,91))
    simulationScreen = Screen(screen, 'Simulation Mode')
    analysisMenu = Screen(screen, 'Analysis Mode Menu', fill = (41,70,91))
    openLoopMenu = Screen(screen, 'Open Loop Menu', fill = (41,70,91))
    forwardOpen = Screen(screen, 'Forward Analysis')
    inverseOpen = Screen(screen, 'Inverse Analysis')

    mainMenu.makeCurrent() #set main menu as currently displayed screen

    def clear_dictionaries(dictionaries):
        '''Takes a list of dictionaries as a parameter.
            Iterates through the list and clears all dictionaries.'''
        for dictionary in dictionaries:
            dictionary.clear()

    def create_link(space, link_id, x1, y1, x2, y2, link_type, link_color):
        '''Creates a link between (x1,y1) and (x2,y2).
        \nIf link_type is 1, a dynamic link is created, else a fixed link is created.
        \nIf link has been succesfully created, it's information will be saved in links and s_links. '''
        link = Link(space, link_id, x1, y1, x2, y2, link_type, link_color)
        if link.created: #if link was created, register it
            link.register(links, s_links)
            delete_element_dropdown.add_to_menu(link.id, link.id)
            motor_object1_dropdown.add_to_menu(link.id, link.id)
            motor_object2_dropdown.add_to_menu(link.id, link.id)
            joint_object1_dropdown.add_to_menu(link.id, link.id)
            joint_object2_dropdown.add_to_menu(link.id, link.id)
            trace_object_dropdown.add_to_menu(link.id, link.id)
            return link #if registerd, return link object
    
    def create_joint(space, joint_id, object1, object2, joint_coords):
        '''Creates a joint between object1 and object2 at given coordinates.
        \nIf joint has been succesfully created, it's information will be saved in joints and s_joints. '''
        joint = Joint(space, joint_id, object1, object2, joint_coords)
        if joint.created: #if joint was created, register it
            joint.register(joints, s_joints)
            delete_element_dropdown.add_to_menu(joint.id, joint.id)
            return joint #if registerd, return joint object

    def create_obstacle(space, id, sides, vertices, radius, color, obstacle_type):
        '''Creates an obstacle with given configuration.
        \nIf sides = 1, a circular obstacle is created with specified radius.
        \nIf sides > 1, radius sets the thickness of the border.
        \nIf obstacle_type is 1, a dynamic obstacle is created, else a fixed obstacle is created.
        \nIf obstacle has been succesfully created, it's information will be saved in obstacles and s_obstacles. '''
        obstacle = Obstacle(space, id, sides, vertices, radius, color, obstacle_type)
        if obstacle.created: #if obstacle was created, register it
            obstacle.register(obstacles, s_obstacles)
            delete_element_dropdown.add_to_menu(obstacle.id, obstacle.id)
            motor_object1_dropdown.add_to_menu(obstacle.id, obstacle.id)
            motor_object2_dropdown.add_to_menu(obstacle.id, obstacle.id)
            joint_object1_dropdown.add_to_menu(obstacle.id, obstacle.id)
            joint_object2_dropdown.add_to_menu(obstacle.id, obstacle.id)
            return obstacle #if registerd, return obstacle object
 
    def create_anchor(space, anchor_id, anchor_coords):
        '''Creates an anchor at given coordinates.
        \nIf anchor has been succesfully created, it's information will be saved in anchors and s_anchors. '''
        anchor = Anchor(space, anchor_id, anchor_coords)
        if anchor.created: #if anchor was created, register it
            anchor.register(anchors, s_anchors)
            delete_element_dropdown.add_to_menu(anchor.id, anchor.id)
            motor_object1_dropdown.add_to_menu(anchor.id, anchor.id)
            motor_object2_dropdown.add_to_menu(anchor.id, anchor.id)
            joint_object1_dropdown.add_to_menu(anchor.id, anchor.id)
            joint_object2_dropdown.add_to_menu(anchor.id, anchor.id)
            return anchor #if registerd, return anchor object
       
    
    def create_motor(space, motor_id, object1, object2, speed, limits):
        '''Creates a motor that causes rotation between object1 and object2 at specified speeds and within angle limits.
        \nIf motor has been succesfully created, it's information will be saved in motors and s_motors. '''
        motor = Motor(space, motor_id, object1, object2, speed, limits)
        if motor.created: #if motor was created, register it
            motor.register(motors, s_motors)
            delete_element_dropdown.add_to_menu(motor.id, motor.id)
            return motor #if registerd, return motor object
        
    def find_object(id):
        '''Returns object with specified id, its shape and where it is stored.
        \nIf object is not found, displays error to user.
        \n\n@details
        \nLooks for object with specified id in all relevant dictionaries
        (joints, anchors, links, obstacles and motors)
        '''
        object, shape = None, None
        stored_in, saved_in = None, None
        if  id in links:
            object, shape = links[id][0], links[id][0].shape
            stored_in = [links, s_links]
        elif id in obstacles:
            object, shape = obstacles[id][0], obstacles[id][0].shape
            stored_in = [obstacles, s_obstacles]
        elif id in anchors:
            object, shape = anchors[id][0], anchors[id][0].shape
            stored_in = [anchors, s_anchors]
        elif id in joints:
            object = joints[id][0]
            stored_in = [joints, s_joints]
        elif id in motors:
            object = motors[id][0]
            stored_in = [motors, s_motors]
        else:
            message = '"' + str(id) + '"' + ': This body does not exist. Please ensure the ID is spelled correctly.'
            error(message)
        return object, shape, stored_in
    
    def get_from_text_inputs(object_type):
        '''Returns text from relevant text inputs for object_type.
        \nObject types are: link, joint, motor, anchor and obstacle.
        \nError is displayed if invalid object_type is entered.'''
        if object_type == 'link':
            link_id = link_id_input.get_text()
            x1 = link_x1_input.get_text()
            y1 = link_y1_input.get_text()
            x2 = link_x2_input.get_text()
            y2 = link_y2_input.get_text()
            link_type = link_type_dropdown.get_selected()
            link_color = link_color_input.get_text()
            return link_id, x1, y1, x2, y2, link_type, link_color
        elif object_type == 'joint':
            joint_id = joint_id_input.get_text()
            object1_id = joint_object1_dropdown.get_selected_text()
            object2_id = joint_object2_dropdown.get_selected_text()
            joint_coords = joint_coords_input.get_text()
            return joint_id, object1_id, object2_id, joint_coords
        elif object_type == 'obstacle':
            obstacle_id = obstacle_id_input.get_text()
            sides = obstacle_sides_input.get_text()
            vertices = obstacle_vertices_input.get_text()
            radius = obstacle_radius_input.get_text()
            obstacle_color = obstacle_color_input.get_text()
            obstacle_type = obstacle_type_dropdown.get_selected()
            return obstacle_id, sides, vertices, radius, obstacle_color, obstacle_type
        elif object_type == 'motor':
            motor_id = motor_id_input.get_text()
            object1_id = motor_object1_dropdown.get_selected_text()
            object2_id = motor_object2_dropdown.get_selected_text()
            speed = motor_speed_input.get_text()
            limits = motor_limits_input.get_text()
            return motor_id, object1_id, object2_id, speed, limits
        elif object_type == 'anchor':
            anchor_id = anchor_id_input.get_text()
            anchor_coords = anchor_coords_input.get_text()
            return anchor_id, anchor_coords
        else:
            error('Invalid object type.')

    def add_link():
        '''Gets link configuration from text inputs and adds link to space.
        \nError is displayed to the user if link with the same id already exists.'''
        link_id, x1, y1, x2, y2, link_type, link_color = get_from_text_inputs('link')
        if link_id not in links: #Check if link with same id exists
            create_link(space, link_id, x1, y1, x2, y2, link_type, link_color)
        else: 
            error('Link with id: ' + link_id + ' already exists! Use a different ID.')

    def add_joint():
        '''Gets joint configuration from text inputs and adds joint to space.
        \nError is displayed to the user if joint with the same id already exists or if connected objects are not found.'''
        joint_id, body1_id, body2_id, joint_coords = get_from_text_inputs('joint')
        if joint_id not in joints:
            object1, _, _ = find_object(body1_id) #get object1
            object2, _,  _ = find_object(body2_id) #get object2
            if object1 and object2: #if both objects found, create joint. Else display error.
                create_joint(space, joint_id, object1, object2, joint_coords)
        else:
            message = 'Joint with ID: "'+ joint_id +'" already exists! Please use a different ID.'
            error(message)

    def add_obstacle():
        '''Gets obstacle configuration from text inputs and adds obstacle to space.
        \nError is displayed to the user if obstacle with the same id already exists.'''
        obstacle_id, sides, vertices, radius, color, obstacle_type = get_from_text_inputs('obstacle')
        if obstacle_id not in obstacles: #check if obstacle already exists
            create_obstacle(space, obstacle_id, sides, vertices, radius, color, obstacle_type)
        else:
            message = 'Obstacle with ID: "' + obstacle_id + '''" already exists! Please use a different ID.'''
            error(message)
        
    def add_motor():
        '''Gets motor configuration from text inputs and adds motor to space.
        \nError is displayed to the user if motor with the same id already exists and if one or more connected object isn't found.'''
        motor_id, object1_id, object2_id, speed, limits = get_from_text_inputs('motor')
        try:
            if motor_id not in motors:
                object1, _, _ = find_object(object1_id) #get object1
                object2, _, _ = find_object(object2_id) #get object 2
                if object1 and object2: #if both objects found, create motor. Else display error.
                    create_motor(space, motor_id, object1, object2, speed, limits)
            else:
                message = 'Motor with ID: "'+ motor_id +'" already exists! Please use a different ID.'
                error(message)
        except:
            error('Please enter appropriate values for all the fields. Refer to documentation to know more.')

    def add_anchor():
        '''Gets anchor configuration from text inputs and adds anchor to space.
        \nError is displayed to the user if anchor with the same id already exists.'''
        anchor_id, anchor_coords = get_from_text_inputs('anchor')
        if anchor_id not in anchors:
            create_anchor(space, anchor_id, anchor_coords)
        else:
            message = 'Anchor with ID: "'+ anchor_id +'" already exists! Please use a different ID.'
            error(message)

    def update_gravity():
        '''Gets value of gravity from gravity text input and updates space gravity.
        \nError is displayed if invalid value is entered for gravity.'''
        try:
            #reset velocity of all links to 0, then change gravity for immediate effect.
            for l in links:
                links[l][0].body._set_velocity((0,0))
            g = -1 * float(gravity_input.get_text())
            space.gravity = (0, g)
        except:
            error('Incorrect value for gravity. Please use integer or float values only!')

    def open_file():
        '''Asks user to locate json file. If found, extracts information and adds all objects into the space.'''
        filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*")))
        if filename != '': #Check if file has been selected.
            try:
                f = open(filename,) #try opening file, if exception occurs, display error.
                try:
                    data = json.load(f) #try loading json data, if exception occurs, display error.
                    delete_all() #delete all objects from space to avoid conflicting ids
                    #add links
                    for l in data['links']:
                        link_x1_input.set_text(str(data['links'][l][0][0]))
                        link_y1_input.set_text(str(data['links'][l][0][1]))
                        link_x2_input.set_text(str(data['links'][l][0][2]))
                        link_y2_input.set_text(str(data['links'][l][0][3]))
                        link_id_input.set_text(l)
                        link_color_input.set_text(str(data['links'][l][1])[1:-1])
                        link_type_dropdown.set_selected(data['links'][l][2])
                        add_link()
                    #add obstacles
                    for o in data['obstacles']:
                        obstacle_sides_input.set_text(str(data['obstacles'][o][0]))
                        obstacle_radius_input.set_text(str(data['obstacles'][o][1]))
                        obstacle_vertices_input.set_text(str(data['obstacles'][o][2]))
                        obstacle_color_input.set_text(str(data['obstacles'][o][3])[1:-1])
                        obstacle_type_dropdown.set_selected(str(data['obstacles'][o][4]))
                        obstacle_id_input.set_text(o)
                        add_obstacle()
                    #add anchors
                    for a in data['anchors']:
                        anchor_id_input.set_text(a)
                        anchor_coords_input.set_text(str(data['anchors'][a])[1:-1])
                        add_anchor()
                    #add joints
                    for j in data['joints']:
                        joint_object1_dropdown.set_selected(str(data['joints'][j][0]))
                        joint_object2_dropdown.set_selected(str(data['joints'][j][1]))
                        joint_id_input.set_text(j)
                        joint_coords_input.set_text(str(data['joints'][j][2])[1:-1])
                        add_joint()
                    #add motors
                    for m in data['motors']:
                        motor_object1_dropdown.set_selected(str(data['motors'][m][0]))
                        motor_object2_dropdown.set_selected(str(data['motors'][m][1]))
                        motor_id_input.set_text(m)
                        motor_speed_input.set_text(str(data['motors'][m][2]))
                        motor_limits_input.set_text(str(data['motors'][m][3]))
                        add_motor()
                    #update gravity
                    space.gravity = (0, data['gravity'])
                except:
                    logging.exception('message')
                    error('Data could not be read! File may not match required type or data may be corrupted.')    
            except:
                error('File could not be opened.')
        else:
            pass       

    def save_file():
        '''Saves data from dictionaries in a json file named by the user.'''
        data = {'links':s_links,'obstacles':s_obstacles, 'anchors':s_anchors, 'joints':s_joints, 'motors':s_motors, 'gravity': space._get_gravity()[1]}
        save_filename = filedialog.asksaveasfilename(initialdir = "/",title = "Save file",filetypes = (("JSON files","*.json"),("all files","*.*")))
        if save_filename[-5:] != '.json': #check if user has already set filetype to json
            save_filename += '.json' #if not, set file type to json
        with open(save_filename, "w") as write_file:
            json.dump(data, write_file) #dump json data into file

    def clear_trace():
        '''Clears all traces displayed.'''
        global trace
        trace = False #reset trace flag
        links_to_trace.clear() #clear dictionary so that no links are traced

    def delete_connected_motors(element, iterables): #delete motor containing element in iterable
        '''Takes element id and iterables to look for element in.
        \nRemoves any connected motors to element from space and relevant dictionaries.'''
        for iterable in iterables:
            if element in iterable:
                for k in list(motors.items()): #loop through dictionary: motors
                        if iterable[element][0] in k[1]: #if value contains element delete the motor
                            m_id = k[0]
                            space.remove(motors[m_id][0].body)
                            motors.pop(m_id)
                            s_motors.pop(m_id)
                            delete_element_dropdown.remove_from_menu(m_id)
                            delete_element_dropdown.set_selected(delete_element_dropdown.default_text)
    
    def delete_connected_joints(element, iterables): #delete joint containing element in iterable 
        '''Takes element id and iterables to look for element in.
        \nRemoves any connected joints to element.'''
        for iterable in iterables:
            if element in iterable:
                for k in list(joints.items()): #loop through dictionary: joints
                    if iterable[element][0] in k[1]: #if value contains element delete the joint
                        j_id = k[0]
                        space.remove(joints[j_id][0].body)
                        joints.pop(j_id)
                        s_joints.pop(j_id)
                        delete_element_dropdown.remove_from_menu(j_id)

    def delete_element():
        '''Takes element id from delete_id_input and deletes object.
        \nError is displayed if no object with specified id exists. '''
        element = delete_element_dropdown.get_selected_text() #get id
        if element != 0:
            object, shape, stored_in = find_object(element) #find object with specified id
            if object and stored_in: #if object found, delete connected motors and obstacles, and remove object from space.
                delete_connected_joints(element, [links, anchors, obstacles]) 
                delete_connected_motors(element, [links, anchors, obstacles])
                if shape:
                    space.remove(shape)
                space.remove(object.body)
                for unit in stored_in: #remove object data from dictionary it is stored in.
                    unit.pop(element)
                delete_element_dropdown.remove_from_menu(element)
                delete_element_dropdown.main = delete_element_dropdown.default_text
            else: #if object is not found, display error.
                error('Body does not exist! Cannot delete this element. Please check the ID!')

    def toggle_grid():
        '''Toggles visibility of the grid.'''
        global grid_visible
        grid_visible = not grid_visible

    def draw_axes():
        '''Takes global variable origin and draws axes base don origin.'''
        global origin
        pygame.draw.rect(screen, black, (origin[0], 100, 2, 600))
        pygame.draw.rect(screen, black, (50,s_height - origin[1], 800, 2))

    def simulate():
        '''Starts simulation.'''
        global paused
        paused = False

    def pause():
        '''Pauses simulation.'''
        global paused
        paused = True

    def reset():
        '''Resets position of all bodies in the space.'''
        pause() #pause simulation
        for _, data in links.items(): #reset positon for all existing links
            link = data[0] #get link object
            initial_angle = data[-1] #get initial angle
            link.set_angle(initial_angle) #set link angle to initial angle
            link.body.position = (0,0) #set links position to initial position
        for _, data in obstacles.items(): #reset position of all dynamic obstacles
            obstacle = data[0] #get obstacle object
            if obstacle.sides == 1: #if obstacle has 1 side, only reset position
                obstacle.body.position = obstacle.vertices[:2] #reset position to initial position
            else: #if more than 1 side then reset angle and position
                initial_angle = data[-1]
                obstacle.body.angle = initial_angle
                obstacle.body.position = (0,0)
        space.step(1/50) #step space forward to update

    def toggle_label(): 
        '''Toggles label visibility on screen.'''
        global label
        reset() #reset position of all links.
        label = not label

    def toggle_trace():
        '''Toggles trace for link specified in trace_id text input.'''
        global trace
        trace = not trace
        try:
            if trace_object_dropdown.get_selected_text() in links: #check if link exists
                link = links[trace_object_dropdown.get_selected_text()][0] #get link object
                trace_pos = trace_pos_dropdown.get_selected() #get trace position
                if trace_pos == 'E' or trace_pos == 'S': #check if trace position is an accepted character
                    trace_color = list(map(int, trace_color_input.get_text().split(','))) #convert color to list
                    if link not in links_to_trace: # check if link is already being traced
                        links_to_trace[link] = (trace_color,[], trace_pos) #if not add link in links_to_trace
                    else:
                        links_to_trace.pop(link) #if link is already beign traced, pop link from dictionary
                else:
                    error('Please enter an appropriate value for the position of the trace. \n"0" = Start of Link\n"1" = End of Link\n\n Try again!')        
            else:
                error('Link does not exists, cannot trace!')
        except:
            error('Could not trace, please check the documentation for how to trace a link.')

    def draw_grid(width, height, color = pygame.Color('gainsboro')):
        '''Draws a colored grid on the screen for specified height and width.
        \nCell size is 50x50.'''
        for y in range(height//50): #divide height by cell height
            for x in range(width//50): #divide height by cell width
                rect = pygame.Rect(x*50, y*50, 50, 50) #rect of size 50x50 50 units away on x and y axis
                pygame.draw.rect(screen, color, rect, 1) #draw rect with specified color

    def delete_all():
        '''Deletes all elements in space and clears all dictionaries.'''
        global paused, open_forward_solution, open_inverse_solution, inverse_message, forward_message
        open_forward_solution = open_inverse_solution = {}
        forward_message = inverse_message = ''
        paused = True
        for i in motors:
            space.remove(motors[i][0].body)
        for i in joints:
            space.remove(joints[i][0].body)
        for i in links:
            space.remove(links[i][0].body, links[i][0].shape)
        for i in obstacles:
            space.remove(obstacles[i][0].body, obstacles[i][0].shape)
        for i in anchors:
            space.remove(anchors[i][0].body, anchors[i][0].shape)
        clear_dictionaries([links, s_links, joints, s_joints, motors, s_motors, obstacles, s_obstacles, anchors, s_anchors])
        clear_trace()
        for dd in DropDown.dropdowns.values():
            if dd.dd_type == 'mutable':
                dd.clear_options()

    def get_link_details(num_of_links):
        '''Gets configuration of number of links specified by user in Kinematic Analysis mode from text inputs.
        \nReturns all lengths angles and colors as lists.'''
        lengths, angles, colors = [], [], []
        for i in range(num_of_links*3):
            current_input = TextInput.get_section('kinematic')[i]
            if 'open_link_length' in current_input.id:
                length = current_input.get_text()
                lengths.append(length)
            if 'open_link_angle' in current_input.id:
                angle = current_input.get_text()
                angles.append(angle)
            if 'open_link_color' in current_input.id:
                color = current_input.get_text()
                try:
                    color = list(map(int, color.split(',')))
                except:
                    error('Invalid color entered.')
                    color = [0,0,0]
                colors.append(color)
        return lengths, angles, colors
    
    def draw_solution(origin, solution, colors):
        '''Draws kinematic analysis solution on screen.
        \nTakes origin, solution (includes start and end point for each link) and colors (for each link) as parameters.'''
        #add anchor at origin
        anchor = create_anchor(space, 'anchor', origin)
        #initialise counter 'j'
        j = 0
        for id, coordinates in solution.items():
            #update coordinates of link
            (x1, y1), (x2, y2) = coordinates
            try:
                #add links
                link = create_link(space, id, x1, y1, x2, y2, "F", colors[j])
                #add joints
                if j == 0:
                    create_joint(space, str(j), anchor, link, [x1,y1])
                else:
                    create_joint(space, str(j), previous_link, link, [x1,y1])
                previous_link = link
                j += 1
            except Exception as e:
                        delete_all()
                        message = 'Invalid configuration for ' + id + '! Please refer to documentation and revise values!'
                        error(message + str(e))
                        break
                    
    def forward_solve():
        '''Performs forward kinematics for specifed number of links and origin offset.
        \nSolution is drawn on the screen.'''
        start_time = time.clock()
        global open_forward_solution, forward_message, origin
        delete_all()
        num_links = int(num_of_links_input.get_text()) #get number of links
        origin_offset = origin_input.get_text() # get origin offset
        try:
            lengths, angles, colors = get_link_details(num_links) #get link configurations from text inputs
            origin, solution, end_effector_pos, error_message = forward_kinematics(num_links, lengths, angles, origin_offset) #get solution
            if error_message == '': #if error message is empty, draw solution
                forward_message = str(end_effector_pos) #update forward message
                open_forward_solution = solution #update forward solution   
                draw_solution(origin, solution, colors)
                print(time.clock() - start_time, 'seconds')
            else:
                forward_message = '' #no solution as error occured
                open_forward_solution = {}
                raise Exception(error_message)
        except Exception as e:
            delete_all()
            error(str(e))
            logging.exception('message')
            
    def identical(list1, list2):
        '''Checks if two lists (of floats or integers) are identical.'''
        if len(list1) == len(list2):
            for i in range(len(list1)):
                if round(list1[i], -1) == round(list2[i], -1):
                    pass
                else:
                    return False
            return True
        else:
            return False

    def inverse_solve():
        '''Performs inverse kinematics for specified number of links, origin offset and end effector position.
        \nSolution is drawn on the screen.'''
        start_time = time.clock()
        global open_inverse_solution, inverse_message, origin
        delete_all()
        num_links = int(num_of_links_input.get_text()) #get number of links
        origin_offset = origin_input.get_text() # get origin offset
        target = end_effector_pos_input.get_text() #get target end effector position
        try:
            lengths, _, colors = get_link_details(num_links) #get link configurations, initial angle is irrelevant
            origin, solution, end_effector_pos, angles, error_message = inverse_kinematics(num_links, lengths, target, origin_offset) #get solution
            if error_message == "": #if error message is empty, draw solution
                ee_plus_origin = list(a+b for a,b in zip(np.round(end_effector_pos, -1), origin)) #add origin to end_effector_pos for comparison with solution
                for i in range(len(angles)): #update angles as per solution in text inputs
                    TextInput.text_inputs['open_link_angle_' + str(i+1)].set_text(str(np.round(np.rad2deg(angles[i]))))
                if identical(ee_plus_origin, solution['link' + str(num_links)][1]): #check if end_effector position is same as target
                    inverse_message += 'Found!' #if true, means solution has been found
                else:
                    inverse_message = 'Target unreachable!' #if not true, means target is unreachable with current link configurations
                open_inverse_solution = solution #update inverse solution
                draw_solution(origin, solution, colors)
                print(time.clock() - start_time, 'seconds')
            else:
                open_inverse_solution = {} #no solution found because error occured
                raise Exception(error_message)
        except Exception as e:
            delete_all()
            error(str(e))
            logging.exception('message')
    
    #Create buttons
    sim_mode_button = Button('to_sim_mode','Simulation Mode',450,330,300,50,primary,primary_bright, simulationScreen.makeCurrent, 'm')
    analysis_mode_button = Button('to_analysis_mode', 'Kinematic Analysis',450,400,300,50,primary,primary_bright,analysisMenu.makeCurrent, 'm')
    
    open_loop_button = Button('to_open_loop', 'Open-Loop', 250, 350, 300, 100, primary, primary_bright, openLoopMenu.makeCurrent, size = 'l', section='kinematics')
    closed_loop_button = Button('to_closed_loop', 'Closed-Loop', 650, 350, 300, 100, grey, grey, size = 'l', section='kinematics')
    back_to_main_button = Button('back_to_main_menu', 'Back', 10, 10, 50, 50, grey, bright_grey, mainMenu.makeCurrent, section='sim_and_kin')

    add_link_button = Button('add_link_button', 'Add Link', 1010, title_y + 60, 180, 20, primary, primary_bright, add_link, section='simulation')
    add_joint_button = Button('add_joint_button', 'Add Joint', 1010, title_y + 140, 180, 20, primary, primary_bright, add_joint, section='simulation')
    add_obstacle_button = Button('add_obstacle_button', 'Add Obstacle', 1010, title_y + 240, 180, 20, primary, primary_bright, add_obstacle, section='simulation')
    add_motor_button = Button('add_motor_button', 'Add Motor', 1010, title_y + 320, 180, 20, primary, primary_bright, add_motor, section='simulation')
    add_anchor_button = Button('add_anchor_button', 'Add Anchor', 1010, title_y + 380, 180, 20, primary, primary_bright, add_anchor, section='simulation')
    update_gravity_button = Button('update_gravity_button', 'Update Gravity', 1010, title_y + 460, 180, 20, secondary, secondary_bright, update_gravity, section='simulation')
    delete_element_button = Button('delete_element_button', 'Delete Element', 1010, title_y + 520, 180, 20, secondary, secondary_bright, delete_element, section='simulation')
    toggle_trace_button = Button('toggle_trace_button', ' Toggle Trace', 1010, title_y + 580, 180, 20, secondary, secondary_bright, toggle_trace, section='simulation')
    clear_trace_button = Button('clear_trace_button', 'Clear traces', 1010, title_y + 610, 180, 20, secondary, secondary_bright, clear_trace, color = white, section='simulation')
    open_file_button = Button('open_file_button', 'Open', 70, 10, 50, 50, black, grey, open_file, section='simulation')
    save_file_button = Button('save_file_button', 'Save', 130, 10, 50, 50, black, grey, save_file, section='simulation')
    simulate_button = Button('simulate_button', 'Simulate', 1010, title_y + 650, 180, 30, pygame.Color('lightseagreen'), pygame.Color('mediumaquamarine'), simulate, 'm', section='simulation')
    pause_button = Button('pause_button', 'Pause', 1010, title_y + 690, 180, 30, pygame.Color('orangered'), pygame.Color('tomato'), pause, 'm', section='simulation')
    reset_button = Button('reset_button', 'Reset', 760, 10, 50, 50, primary, primary_bright, reset, section='simulation')

    forward_kin_button = Button('to_forward', 'Forward', 250, 380, 300, 50, primary, primary_bright, forwardOpen.makeCurrent, 'l', section='open_loop')
    inverse_kin_button = Button('to_inverse', 'Inverse', 650, 380, 300, 50, primary, primary_bright, inverseOpen.makeCurrent, 'l', section='open_loop')
    back_to_analysis_button= Button('back_to_kinematics', 'Back', 10, 10, 50, 50, grey, bright_grey, analysisMenu.makeCurrent, section='open_loop')

    forward_solve_button = Button('forward_solve', 'Solve', 1010, title_y + 690, 180, 30, pygame.Color('lightseagreen'), pygame.Color('mediumaquamarine'), forward_solve, 'm', section='forward')

    inverse_solve_button = Button('inverse_solve', 'Solve', 1010, title_y + 690, 180, 30, pygame.Color('lightseagreen'), pygame.Color('mediumaquamarine'), inverse_solve, 'm', section='inverse')
    
    back_to_open_loop_button = Button('back_to_open_loop', 'Back', 10, 10, 50, 50, bright_grey, grey, openLoopMenu.makeCurrent, section='forward_and_inverse')
    
    grid_button = Button('grid', 'Grid', 820, 10, 50, 50, primary, primary_bright, toggle_grid, section='common')
    label_button = Button('label', 'Label', 880, 10, 50, 50, primary, primary_bright, toggle_label, section='common')
    clear_button = Button('clear', 'Clear', 940, 10, 50, 50, pygame.Color('orangered'), pygame.Color('tomato'), delete_all, section='common')
       
    def draw_sim_mode(screen):
        '''Draws simulation mode screen.'''
        title_y = 20
        Text.draw(screen, 'Action Menu', mediumfont, black, 1100, title_y)
        pygame.draw.rect(screen, black, (1000,0,2,750))
        #Draw Text Inputs
        TextInput.draw_sections(screen, ['simulation', 'link', 'joint', 'anchor', 'obstacle', 'motor', 'gravity', 'trace', 'delete'])
        #Draw Buttons
        Button.draw_sections(screen, ['common', 'simulation', 'sim_and_kin'])
        #Draw Dropdowns
        for dd in DropDown.dropdowns.values():
            dd.draw(screen)
        #Separator
        pygame.draw.line(screen, (200,200,200),(1020, title_y + 420), (1180, title_y + 420))
        #Display Gravity
        pygame.draw.rect(screen, white, (850, 700, 120, 30))
        g_mssg = 'Gravity: ' + str(-1 * space._get_gravity()[1])
        Text.draw(screen, g_mssg, smallfont, black, 905, 725)


    def open_loop_forward(screen):
        '''Draws forward kinematics screen.'''
        global open_forward_solution, forward_message
        try:
            num_links = int(num_of_links_input.get_text()) #get number of links from previous screen
            if 1 <= num_links <= 7: #check if number of links is within range, if true, draw screen
                title_y = 20
                Text.draw(screen, 'Configure Links', mediumfont, black, 1100, title_y)
                pygame.draw.rect(screen, black, (1000,0,2,750))
                #Draw Text inputs
                for i in range(num_links*3):
                    TextInput.get_section('kinematic')[i].draw(screen)
                    TextInput.get_section('kinematic')[i].set_visible()
                for j in range(num_links):
                    Text.draw(screen, 'Link' + str(j+1), smallfont, primary, 1100, 50 + j*70)
                for ti in TextInput.get_section('simulation'):
                    ti.set_invisible()
                #Draw Buttons
                Button.draw_sections(screen, ['common', 'forward_and_inverse', 'forward'])
                draw_axes()
                #Origin
                Text.draw(screen, 'Origin:', smallfont, black, 1035, 658)
                origin_input.draw(screen)
                origin_input.set_visible()
                #Display Solution
                pygame.draw.rect(screen, black, (350, 10, 300, 50), border_radius = 150)
                solution = 'Solution: ' + forward_message
                Text.draw(screen, solution, mediumfont, pygame.Color('green'), 500, 35)
                #Label link coordinates
                try: #try block is to avoid crash when solution does not exists
                    pos = open_forward_solution['link' + str(num_links)][1] #get link end coordinates from solution
                    origin = open_forward_solution['link1'][0] #origin is start of first link in solution
                    label = list(a-b for a,b in zip(pos,origin)) #coordinates to label are difference between pos and origin.
                    #draw label on screen at correct location
                    pygame.draw.rect(screen, white, (pos[0] + 5, s_height - pos[1] + 5, 120, 25), border_radius = 100)
                    Text.draw(screen, str(label), smallfont, black, pos[0] + 65, s_height - pos[1] + 17)
                except:     
                    pass
            else:
                raise Exception
        except: #if incorrect number of links entered, go back to open-loop analysis menu
            openLoopMenu.makeCurrent()
            error('Invalid number of links! Please choose a value between 1-7.')
            logging.exception('message')

    def open_loop_inverse():
        '''Draws inverse kinematics screen.'''
        global open_inverse_solution, inverse_message
        try:
            num_links = int(num_of_links_input.get_text()) #get number of links from previous screen
            if 1 <= num_links <= 7: #check if number of links is within range, if true, draw screen
                title_y = 20
                Text.draw(screen, 'Configure Links', mediumfont, black, 1100, title_y)
                pygame.draw.rect(screen, black, (1000,0,2,750))
                draw_axes()
                #Draw Text_inputs
                for i in range(num_links*3):
                    TextInput.get_section('kinematic')[i].draw(screen)
                    TextInput.get_section('kinematic')[i].set_visible()
                for j in range(num_links):
                    Text.draw(screen, 'Link' + str(j+1), smallfont, primary, 1100, 50 + j*70)
                for ti in TextInput.get_section('simulation'):
                    ti.set_invisible()
                #Draw buttons
                Button.draw_sections(screen, ['common', 'forward_and_inverse', 'inverse'])
                #End Effector Position
                Text.draw(screen, 'Target Pos:', smallfont, black, 1050, title_y + 618 )
                end_effector_pos_input.draw(screen)
                end_effector_pos_input.set_visible()
                #Origin
                Text.draw(screen, 'Origin:', smallfont, black, 1035, 658)
                origin_input.draw(screen)
                origin_input.set_visible()
                #Display Solution
                pygame.draw.rect(screen, black, (350, 10, 300, 50), border_radius = 150)
                solution = 'Solution: ' + inverse_message
                Text.draw(screen, solution, mediumfont, pygame.Color('green'), 500, 35)
                #Label link coordinates if solution exists
                try: #try block is to avoid crash when solution does not exists
                    for i in range(num_links):
                        pos = np.round(open_inverse_solution['link' + str(i + 1)][1], -1) #get link end coordinates from solution
                        origin = open_inverse_solution['link1'][0] #origin is start of first link in solution
                        label = list(a-b for a,b in zip(pos,origin)) #coordinates to label are difference between pos and origin..
                        #draw label at correct position
                        pygame.draw.rect(screen, white, (pos[0] + 5, s_height - pos[1] + 5, 120, 25), border_radius = 100)
                        Text.draw(screen, str(label), smallfont, black, pos[0] + 65, s_height - pos[1] + 17)

                except Exception as e:
                    pass
            else:
                raise Exception
        except: #if incorrect number of links entered, go back to open-loop analysis menu
            openLoopMenu.makeCurrent()
            error('Invalid number of links! Please choose a value between 1-7.')
            logging.exception('message')

    def draw_open_loop_menu():
        '''Draws open loop analysis menu on screen'''
        global open_inverse_solution, open_forward_solution
        open_inverse_solution = open_forward_solution = {} #reset solutions
        draw_grid(1200,750, [80,80,80,100])
        Text.draw(screen, 'Number of Links: ', largefont, white, 500, 325)
        num_of_links_input.draw(screen)
        num_of_links_input.set_visible()
        Button.draw_sections(screen, ['open_loop'])

    def draw_analysis_menu(screen):
        '''Draws kinematic analysis menu on screen.'''
        draw_grid(1200,750, [80,80,80,100])
        Button.draw_sections(screen, ['kinematics', 'sim_and_kin'])

    def menuscreen():
        '''Draws main menu on screen.'''
        draw_grid(1200,750, [80,80,80,100])
        Text.draw(screen, 'Simulinkage', xlargefont, white, 600, 220 + sin(time.time()*5)*5 + 40)
        Button.draw_sections(screen, ['title'])
        Text.draw(screen, 'by Kaif Kutchwala', smallfont, white, 600, 500)
        Text.draw(screen, 'v1.00', smallfont, white, 600, 515)

    while True: #game loop
        #update screens
        mainMenu.screenUpdate()
        simulationScreen.screenUpdate()
        analysisMenu.screenUpdate()
        openLoopMenu.screenUpdate()
        forwardOpen.screenUpdate()
        inverseOpen.screenUpdate()

        #check for pygame events
        dropdowns = DropDown.dropdowns.values()
        text_inputs = TextInput.text_inputs.values()
        buttons = Button.buttons.values()
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        dropdown_active = False
        for event in pygame.event.get(): #check for user input
            if event.type == pygame.QUIT: #input to close game
                pygame.quit
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: #check if user left clicks
                    for dd in dropdowns:
                        if event.button == 1:
                            if dd.menu_active:
                                dd.draw_menu = not dd.draw_menu
                                dropdown_active = True
                            if dd.rect.collidepoint(mouse_pos):
                                dd.menu_active = not dd.menu_active
                            else:
                                dd.menu_active = False

                    for ti in text_inputs:
                        if event.button == 1:
                            if not dropdown_active:
                                if ti.input_rect.collidepoint(event.pos) and ti.is_visible(): #if the position of clcik collides with text input
                                    ti.input_active = not ti.input_active #toggle text input
                                else: #if position of clcik does not collide with text input
                                    ti.set_inactive() #set text input inactive
                            else:
                                ti.set_inactive()
                    
                    for button in buttons:
                        if button.rect.collidepoint(mouse_pos) and event.button == 1 and button.action != None and button.visible and not dropdown_active:
                            button.cooldown = True
                            button.action()
                            time.sleep(0.2)
            if event.type == pygame.MOUSEWHEEL:
               for dd in dropdowns:
                   if dd.menu_active and dd.draw_menu:
                        if event.y == -1:
                            if dd.range_upper < len(dd.options):
                                dd.range_lower -= event.y
                                dd.range_upper -= event.y
                        elif event.y == 1:
                            if dd.range_lower != 0:
                                dd.range_lower -= event.y
                                dd.range_upper -= event.y
                    
            if event.type == pygame.KEYDOWN: #if user types on keyboard
                for ti in text_inputs:
                    if ti.input_active == True: #if a text input is active
                        if event.key == pygame.K_BACKSPACE:
                            ti.delete_character()
                        elif event.key == pygame.K_v and keys[pygame.K_LCTRL]:
                            ti.add_text(root.clipboard_get())
                        elif event.key == pygame.K_c and keys[pygame.K_LCTRL]:
                            root.clipboard_clear()
                            root.clipboard_append(ti.get_text())
                        elif event.key == pygame.K_TAB and keys[pygame.K_LSHIFT]:
                            try:
                                if ti.prev.is_visible(): #set next text input active if it is visible and if user hits tab key
                                    ti.prev.set_active()
                                    ti.set_inactive()
                            except:
                                pass
                            break
                        elif event.key == pygame.K_DELETE:
                            ti.delete_text() #clear all text if user hits delete key
                        elif event.key == pygame.K_TAB:
                            try:
                                if ti.next.is_visible(): #set next text input active if it is visible and if user hits tab key
                                    ti.next.set_active()
                                    ti.set_inactive()
                            except:
                                pass
                            break
                        elif event.key == pygame.K_RETURN: #if user hits enter key
                            if ti.section == 'link': #if user is currently editing link text input
                                add_link() 
                            elif ti.section == 'anchor': #if user is currently editing anchor text input
                                add_anchor()
                            elif ti.section == 'motor': #if user is currently editing motor text input
                                add_motor()
                            elif ti.section == 'obstacle': #if user is currently editing obstacle text input
                                add_obstacle()
                            elif ti.section == 'joint': #if user is currently editing joint text input
                                add_joint()
                            elif ti.section == 'delete': #if user is currently editing delete element text input
                                delete_element()
                            elif ti.section == 'trace': #if user is currently editing trace text input
                                toggle_trace()
                            elif ti.section == 'gravity': #if user is currently editing gravity text input
                                update_gravity()
                            else:
                                pass
                        else: #if any other key is pressed, add unicode character in active text input
                            ti.add_text(event.unicode)
                        break

        if grid_visible and (simulationScreen.isCurrent() or forwardOpen.isCurrent() or inverseOpen.isCurrent()):
                draw_grid(1000,750) #draw grid only on aforementioned screens
        
        #draw all objects in space
        space.debug_draw(draw_options)

        if mainMenu.isCurrent():
            menuscreen()
            delete_all()
        
        if simulationScreen.isCurrent():
            draw_sim_mode(screen)
        
        if analysisMenu.isCurrent():
            draw_analysis_menu(screen)
            delete_all()
        
        if openLoopMenu.isCurrent():
            draw_open_loop_menu()
            delete_all()
        
        if forwardOpen.isCurrent():
            open_loop_forward(screen)
        
        if inverseOpen.isCurrent():
            open_loop_inverse()

        #trace 
        if trace:
            for link, value in links_to_trace.items():
                pos = link.start
                points = value[1] #points to trace
                color = value[0]
                length = sqrt((link.end[0]-pos[0])**2 + (link.end[1]-pos[1])**2)
                init_angle = asin((link.end[1] - pos[1])/length)
                angle = -link.body.angle - init_angle 
                start = link.body.local_to_world(pos) #caluclate start of link
                end = ((start[0] + length*cos(angle)), s_height - start[1] + length*sin(angle)) #caluclate end of link
                if value[2] == 'E': #if trace position is 1 trace end of link
                    if end not in points:
                        points.append(end)
                else: #else trace start of link
                    if start not in points:
                        points.append((start[0], s_height - start[1]))
                for point in points: #draw circle on all points to trace
                    pygame.draw.circle(screen, color, point, 2)
        #label
        if label:
            for link_id, data in links.items(): #place link's label at its center of gravity
                link = data[0]
                if link.link_type == 'D':
                    label_pos = link.body.center_of_gravity
                else:
                    label_pos = ((link.start[0] + link.end[0])//2, (link.start[1] + link.end[1])//2)
                surface , _ = text_objects(link_id, smallfont, black)
                w = surface.get_width()
                pygame.draw.rect(screen, white, (label_pos[0], s_height - label_pos[1] - 7.5, w + 10, 15), border_radius = 100)
                Text.draw(screen, link_id, smallfont, link.color, label_pos[0] + w//2 + 5, s_height - label_pos[1])
            for joint_id, data in joints.items(): #place joint's label below its position.
                label_pos = data[-1]
                surface , _ = text_objects(joint_id, smallfont, black)
                w = surface.get_width()
                pygame.draw.rect(screen, white, (label_pos[0] - w//2 , s_height - label_pos[1] + 7.5, w + 10, 15), border_radius = 100)
                Text.draw(screen, joint_id, smallfont, [100,0,100], label_pos[0] + 5, s_height - label_pos[1] + 15)
            for obstacle_id, data in obstacles.items(): #place obstacle's label at its center of gravity
                obstacle = data[0]
                if obstacle.obstacle_type == 'D':
                    label_pos = obstacle.body.center_of_gravity
                else:
                    label_pos = obstacle.vertices[0]
                surface , _ = text_objects(obstacle_id, smallfont, black)
                w = surface.get_width()
                pygame.draw.rect(screen, white, (label_pos[0] - w//2 , s_height - label_pos[1] - 25, w + 10, 15), border_radius = 100)
                Text.draw(screen, obstacle_id, smallfont, obstacle.color, label_pos[0] + 5, s_height - label_pos[1] - 17.5)
            for anchor_id, data in anchors.items(): #place anchors label to the left of its position
                anchor = data[0]
                label_pos = anchor.coords
                surface , _ = text_objects(anchor_id, smallfont, black)
                w = surface.get_width()
                pygame.draw.rect(screen, white, (label_pos[0] - w//2 , s_height - label_pos[1] - 25, w + 10, 15), border_radius = 100)
                Text.draw(screen, anchor_id, smallfont, black, label_pos[0] + 5, s_height - label_pos[1] - 17.5)
            
        #limit motors
        if not cooldown:
            for id, m in motors.items():
                #reverse angle's sign so anti-clockwise is negative.
                for object in [m[1], m[2]]:
                    if isinstance(object, Link):
                        angle = -(np.rad2deg(object.body.angle))
                        limits = m[-1]
                        if limits != [0,0]:
                            if angle <= min(limits) or angle >= max(limits):
                                m[0].set_speed(m[0].get_speed() * -1)
                                cooldown = True
        #Cooldown to ensure angle can change enough so motor rate is not toggled infinitely!
        if cooldown:
            cooldown_counter += 1
        if cooldown_counter == 5:
            cooldown = False
            cooldown_counter = 0

        # update space based on paused flag
        if paused:
            space.step(0)
        else:
            space.step(1/50)

        pygame.display.update() #render frame
        clock.tick(50) # fps to 120

if __name__ == "__main__":
    main()