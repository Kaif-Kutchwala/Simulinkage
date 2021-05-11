import ast
import logging
from math import cos, sin
import numpy as np
import tinyik
import time

error_message = ''

def _add_lists(list1, list2):
    sum_list = list(a+b for a,b in zip(list1, list2))
    return sum_list

def _subtract_lists(list1, list2):
    result = list(a-b for a,b in zip(list1, list2))
    return result

def _convert_to_list(k):
    global error_message
    converted_list = ast.literal_eval(k)
    if isinstance(converted_list, tuple):
        return list(converted_list)
    else:
        error_message = 'Invalid origin! Using 0,0 as origin.'
        return [0,0]  

def _convert_to_number(k):
    global error_message
    converted = ast.literal_eval(k)
    if isinstance(converted, int) or isinstance(converted, float):
        return converted
    else:
        error_message = 'Cannot convert to integer or float'
        raise Exception

def _calculate_end_coordinates(x1, y1, angle, length):
    x2 = x1 + length * cos(np.deg2rad(angle))
    y2 = y1 + length * sin(np.deg2rad(angle))
    return x2,y2

def _create_element(dictionary, key, value):
    dictionary[key] = value

def _convert_to_list_of(type, k):
    global error_message
    try:
        converted = list(map(type, (i for i in k)))
        return converted
    except:
        error_message = "Invalid angle or length! \nPlease ensure lengths and angles are entered as numbers only."
        raise Exception

def get_coordinates_from_lengths_and_angles(num_of_links, origin, angles, lengths):
    solution = {}
    current_angle = 0
    x1, y1 = origin
    for i in range(num_of_links):
        current_angle += angles[i] #final angle is sum of all angles
        x2, y2 = _calculate_end_coordinates(x1, y1, current_angle, _convert_to_number(lengths[i]))
        _create_element(solution, 'link' + str(i+1), np.round([(x1,y1), (x2,y2)]))
        x1, y1 = x2, y2
        end_effector_pos = np.round(_subtract_lists([x2,y2], origin))
    return solution, end_effector_pos

def forward_kinematics(num_of_links, lengths, angles, origin_offset):
    global error_message
    try:
        origin = _add_lists([50,50], _convert_to_list(origin_offset))
        angles = _convert_to_list_of(float, angles)
        solution, end_effector_pos = get_coordinates_from_lengths_and_angles(num_of_links, origin, angles, lengths)        
        return origin, solution, end_effector_pos, error_message
    except Exception as e:
        error_message += '\nFailed.\n' + str(e)
        logging.exception('message')
        return [50,50], 0, 0, error_message
    
def inverse_kinematics(num_of_links, lengths, target, origin_offset):
    global error_message
    try:
        target = _convert_to_list(target) + [0]
        if len(target) == 3:
            origin = _add_lists([50,50], _convert_to_list(origin_offset))
            inverse_paramters = []
            for i in lengths:
                inverse_paramters.extend(('z', [_convert_to_number(i), 0,0]))
            arm = tinyik.Actuator(inverse_paramters)
            arm.ee = target
            angles = np.round(np.rad2deg(arm.angles))
            solution, _ = get_coordinates_from_lengths_and_angles(num_of_links, origin, angles, lengths)
            return origin, solution, arm.ee, arm.angles, error_message
        else:
            error_message = "Invalid End Effector target position. Please enter 2 comma separated values only."
    except Exception as e:
        error_message += '\nFailed.\n' + str(e)
        logging.exception('message')
        return 0, 0, 0, error_message
    