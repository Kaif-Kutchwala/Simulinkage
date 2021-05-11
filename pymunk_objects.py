import ast
import pymunk
import logging
from pymunk.vec2d import Vec2d
from error import error

def safe_literal_eval(string):
    try:
        string = ast.literal_eval(string)
    except:
        pass
    return string

class Anchor():
    def __init__(self, space, id, coords):
        self.error_details = '' #stores additional information on error to help user fix the issue.
        try:
            self.space = space
            self.id = id
            self.created = False
            self._parse_input(coords) #convert string inputs to appropriate data types
            valid_input = self._check_input(self.coords) #ensure inputs are in the required data types
            if valid_input: #add link if input is correct
                self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
                self.body.position = self.coords
                self.shape = pymunk.Circle(self.body,5)
                self.shape.filter = pymunk.ShapeFilter(group=2)
                space.add(self.body, self.shape)
                self.created = True
            else:
                raise Exception
        except:
            self.error_mssg = 'Invalid input for ' + self.id + '\nPlease ensure all values are in the appropriate format. Refer to documentation for more help.'
            if self.error_details != '':
                self.error_mssg += '\n\nError Details:\n' + self.error_details
            error(self.error_mssg)
            logging.exception('message')

    def _parse_input(self, coords):
        self.coords = safe_literal_eval(coords) #convert to tuple
        self.coords = list(self.coords) #convert tuple to list

    def _check_input(self, coords):
        try:
            assert isinstance(coords, list), 'Anchor Coordinates should be comma separated values only. '
            assert len(coords) == 2, 'Incorrect number of coordinates'
            for i in coords:
                assert isinstance(i, int) or isinstance(i, float), 'Anchor Coordinates should be comma separated values only. '
            assert (0 <= coords[0] <= 950), 'x-coordinate must be between 0-950.'
            assert (0 <= coords[1] <= 750), 'y-coordinate must be between 0-750.'
            return True
        except Exception as e:
            self.error_details = str(e)
            return False
    
    def register(self, anchors, s_anchors):
        anchors[self.id] = (self, self.coords)
        s_anchors[self.id] = (self.coords)

class Link():
    def __init__(self, space, id, x1, y1, x2, y2, link_type = 1, color = [0,0,255]):
        self.error_details = '' #stores additional information on error to help user fix the issue.
        try:
            self.space = space
            self.id = id
            self.created = False
            self._parse_input(x1, y1, x2, y2, link_type, color) #convert string inputs to appropriate data types
            valid_input = self._check_input(self.x1, self.y1, self.x2, self.y2, self.link_type, self.color) #ensure inputs are in the required data types
            if valid_input: #add link if input is correct                
                self.start = Vec2d(self.x1, self.y1)
                self.end = Vec2d(self.x2, self.y2)
                self.color = self.color + [255]
                if self.link_type == 'D':
                    self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
                else:
                    self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
                self.shape = pymunk.Segment(self.body, self.start, self.end, 5)
                self.shape.filter = pymunk.ShapeFilter(group=2)
                self.shape.mass = 10
                self.shape.friction = 1
                self.shape.color = self.color
                self.space.add(self.body, self.shape)
                self.created = True
            else:
                raise Exception
        except:
            self.error_mssg = 'Invalid input for ' + self.id + '\nPlease ensure all values are in the appropriate format. Refer to documentation for more help.'
            if self.error_details != '':
                self.error_mssg += '\n\nError Details:\n' + self.error_details
            error(self.error_mssg)
            logging.exception('message')
    
    def _parse_input(self, x1, y1, x2, y2, link_type, color):
        self.x1 = safe_literal_eval(x1)
        self.y1 = safe_literal_eval(y1)
        self.x2 = safe_literal_eval(x2)
        self.y2 = safe_literal_eval(y2)
        self.link_type = safe_literal_eval(link_type)
        self.color = safe_literal_eval(color)
        self.color = list(abs(x) for x in self.color)
        
    def _check_input(self, x1, y1, x2, y2, link_type, color):
        try:
            assert isinstance(x1, int) or isinstance(x1, float), 'Link Coordinates should be integer values only.'
            assert isinstance(y1, int) or isinstance(y1, float), 'Link Coordinates should be integer values only.'
            assert isinstance(x2, int) or isinstance(x2, float), 'Link Coordinates should be integer values only.'
            assert isinstance(y2, int) or isinstance(y2, float), 'Link Coordinates should be integer values only.'
            assert 0 <= x1 <= 950, 'x-coordinates must be between 0-950.'
            assert 0 <= x2 <= 950, 'x-coordinates must be between 0-950.'
            assert 0 <= y1 <= 750, 'y-coordinates must be between 0-750.'
            assert 0 <= y2 <= 750, 'y-coordinates must be between 0-750.'
            assert isinstance(link_type, str), 'Please select a value for Link Type.'
            assert isinstance(color, list), 'Link color should be 3 comma separated values (rgb).'
            assert len(color) == 3, 'Link color should be 3 comma separated values (rgb).'
            for i in color:
                assert isinstance(i, int), 'RGB values for Link Color must be integers between 0-255.'
                assert 0 <= i <= 255, 'RGB values for Link Color must be integers between 0-255.'
            return True
        except AssertionError as e:
            self.error_details = str(e)
            return False
    
    def get_angle(self):
        return self.body.angle
        
    def set_angle(self, angle):
        self.body._set_angle(angle)
    
    def register(self, links, s_links):
        links[self.id] = (self, (self.x1,self.y1,self.x2,self.y2), self.color, self.body.angle)
        s_links[self.id] = ((self.x1,self.y1,self.x2,self.y2), self.color[:-1], self.link_type)
    

class Joint():
    def __init__(self, space, id, object1, object2, joint_coords):
        self.error_details = ''
        try:
            self.id = id
            self.created = False
            self.space = space
            self._parse_input(joint_coords)
            valid_input = self._check_input(self.coords)
            if valid_input:
                self.object1 = object1
                self.object2 = object2
                self.body = pymunk.PivotJoint(self.object1.body, self.object2.body, self.coords)
                self.space.add(self.body)
                self.created = True
            else:
                raise Exception
        except Exception as e:
            self.error_mssg = 'Invalid input for ' + self.id + '\nPlease ensure all values are in the appropriate format. Refer to documentation for more help.'
            if self.error_details != '':
                self.error_mssg += '\n\nError Details:\n' + self.error_details
            error(self.error_mssg)
            logging.exception('message')
    
    def  _parse_input(self, coords):
        self.coords = safe_literal_eval(coords)
        self.coords = list(self.coords)
    
    def _check_input(self, coords):
        try: 
            assert isinstance(coords, list), 'Joint coordinates should be 2 comma separated values (x,y) '
            assert len(coords) == 2, 'Incorrect number of coordinates for Joint.'
            for i in coords:
                assert isinstance(i, int) or isinstance(i, float), 'Joint coordinates should be 2 comma separated values (x,y) '
            assert 0 <= coords[0] <= 950, 'x-coordinate must be an integer between 0-950.'
            assert 0 <= coords[1] <= 750, 'y-coordinate must be an integer between 0-750.'
            return True
        except AssertionError as e:
            self.error_details = str(e)
            return False
    
    def register(self, joints, s_joints):
        joints[self.id] = (self, self.object1, self.object2, self.coords)
        s_joints[self.id] = (self.object1.id, self.object2.id, self.coords)
    
class Motor():
    def __init__(self, space, id, object1, object2, speed, limits):
        self.error_details = ''
        try:
            self.id = id
            self.created = False
            self.space = space
            self.object1 = object1
            self.object2 = object2
            self._parse_input(speed, limits)
            valid_input = self._check_input(self.speed, self.limits)
            if valid_input:
                self.body = pymunk.constraints.SimpleMotor(self.object1.body, self.object2.body, self.speed)
                self.space.add(self.body)
                self.created = True
            else:
                raise Exception
        except:
            self.error_mssg = 'Invalid input for ' + self.id + '\nPlease ensure all values are in the appropriate format. Refer to documentation for more help.'
            if self.error_details != '':
                self.error_mssg += '\n\nError Details:\n' + self.error_details
            error(self.error_mssg)
            logging.exception('message')

    def _parse_input(self, speed, limits):
        self.speed = safe_literal_eval(speed)
        self.limits = safe_literal_eval(limits)
        self.limits = list(self.limits)
    
    def _check_input(self, speed, limits):
        try:
            assert isinstance(speed, int), 'Motor Speed must be a integer.'
            assert isinstance(limits, list), 'Limits must be entered as comma separated integers.\nHint: \nLimits are in degrees. \nFor 360 rotation set limits to "0,0"'
            assert len(limits) == 2, 'Only 2 values are required for Motor limits i.e. max and min limits.'
            for i in limits:
                assert isinstance(i, int) or isinstance(i, float), 'Limits must be integer of float values representing the angles in degrees.'
            return True
        except AssertionError as e:
            self.error_details = str(e)
            return False
    
    def register(self, motors, s_motors):
        motors[self.id] = (self, self.object1, self.object2, self.limits)
        s_motors[self.id] = (self.object1.id, self.object2.id, self.speed, self.limits)
    
    def set_speed(self, speed):
        self.speed = speed
        self.body._set_rate(self.speed)
    
    def get_speed(self):
        return self.speed

class Obstacle():
    def __init__(self, space, id, sides, vertices, radius, color, obstacle_type):
        self.error_details = ''
        try:
            self.id = id
            self.created = False
            self.space = space
            self._parse_input(sides, vertices, radius, color, obstacle_type) #convert string inputs to appropriate data types
            valid_input = self._check_input(self.sides, self.vertices, self.radius, self.color, self.obstacle_type) #ensure inputs are in the required data types
            if valid_input:
                if self.obstacle_type == 'D':
                    self.body = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
                if self.obstacle_type == 'F':
                    self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
                self.color = self.color + [255]
                if self.sides == 1:
                    self.body.position = self.vertices
                    self.shape = pymunk.Circle(self.body, self.radius)
                elif self.sides == 2:
                    self.shape = pymunk.Segment(self.body, self.vertices[0:2], self.vertices[2:], self.radius)
                else:
                    self.shape = pymunk.Poly(self.body, self._group_vertices(self.vertices), None, self.radius)
                self.shape.friction = 1
                self.shape.mass = 10
                self.shape.color = self.color
                self.space.add(self.body, self.shape)
                self.vertices = self._group_vertices(self.vertices)
                self.created = True
            else:
                raise Exception
        except:
            self.error_mssg = 'Invalid input for ' + self.id + '\nPlease ensure all values are in the appropriate format. Refer to documentation for more help.'
            if self.error_details != '':
                self.error_mssg += '\n\nError Details:\n' + self.error_details
            error(self.error_mssg)

    def _parse_input(self, sides, vertices, radius, color, obstacle_type):
        self.sides = safe_literal_eval(sides)
        self.vertices = list(safe_literal_eval(vertices))
        self.radius = float(safe_literal_eval(radius))
        self.color = list(safe_literal_eval(color))
        self.obstacle_type = safe_literal_eval(obstacle_type)   
        self.color = list(abs(x) for x in self.color)
    
    def _check_input(self, sides, vertices, radius, color, obstacle_type):
        try:
            assert isinstance(sides, int), 'Number of sides must be a positive integer.'
            assert sides > 0, 'Number of sides must be a positive integer.'
            assert isinstance(vertices, list), 'Vertices must be entered as comma separated integers only.'
            assert len(vertices) == self.sides * 2, 'Incorrect number of vertices entered.'
            assert isinstance(radius, float), 'Obstacle Radius must be an integer'
            assert radius > 0, 'Obstacle Radius must be an integer greater than zero.'
            assert isinstance(color, list), 'Obstacle color should be 3 comma separated values (rgb).'
            assert len(color) == 3, 'Obstacle color should be 3 comma separated values (rgb).'
            for i in color:
                assert isinstance(i, int), 'RGB values for Obstacle Color must be integers between 0-255.'
                assert 0 <= i <= 255, 'RGB values for Obstacle Color must be integers between 0-255.'
            assert isinstance(obstacle_type, str), 'Please select an Obstacle Type.'
            return True
        except AssertionError as e:
            self.error_details = str(e)
            return False
    
    def _group_vertices(self, vertices):
        grouped = []
        for i in range(0, len(vertices), 2):
            grouped.append((vertices[i], vertices[i+1]))
        return grouped

    def register(self, obstacles, s_obstacles):
        obstacles[self.id] = (self, self.vertices, self.color, self.body.angle)
        s_obstacles[self.id] = (self.sides, self.radius, self.vertices, self.color[:-1], self.obstacle_type)

    def delete(self, space, obstacles, s_obstacles):
        obstacles.pop(self.id)
        s_obstacles.pop(self.id)
        space.remove(self.body, self.shape)
