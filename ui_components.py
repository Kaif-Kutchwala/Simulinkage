import pygame
import time

pygame.init()

#Colors
white = [255,255,255]
black = [0,0,0]
grey = [100,100,100]
bright_grey = [150,150,150]
primary = [26,150,227]
primary_bright = [46,180,247]
secondary = pygame.Color('palevioletred')
secondary_bright = pygame.Color('pink')

#Define font sizes
xsmallfont = pygame.font.Font('freesansbold.ttf', 10)
smallfont = pygame.font.Font('freesansbold.ttf', 16)
mediumfont = pygame.font.Font('freesansbold.ttf', 20)
largefont = pygame.font.Font('freesansbold.ttf', 40)
xlargefont = pygame.font.Font('freesansbold.ttf', 100)

def text_objects(text, font, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    return surf,rect

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

class Screen():
        screens = {}
        def __init__(self, screen, title, fill = [255,255,255]):
            self.title = title
            self.fill = fill
            self.current = False
            self.screen = screen
            Screen.screens[self.title] = self
        
        def makeCurrent(self):
            self.current = True
            #endCurrent for all other screens
            for s in Screen.screens.items():
                if s[1].title != self.title:
                    s[1].endCurrent()
        
        def endCurrent(self):
            self.current = False
        
        def isCurrent(self):
            return self.current
        
        def screenUpdate(self):
            if self.current:
                self.screen.fill(self.fill)
        
        def title(self):
            return self.title

class DropDown():
    dropdowns = {}
    def __init__(self, id, x, y, w, h, font, default, options,  color_menu = [grey, black], color_option = [grey, primary_bright, primary], dd_type = 'mutable'):
        self.id = id
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = default
        self.default_text = default
        self.options = options
        self.selected = ''
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.range_lower = 0
        self.range_upper = 5
        self.dd_type = dd_type
        DropDown.dropdowns[self.id] = self
    
    def draw(self, screen):
        mpos = pygame.mouse.get_pos()
        self.active_option = -1
        #if no options, display default text
        if len(self.options) == 0:
            self.main = self.default_text
        
        if self.rect.collidepoint(mpos):
            self.menu_active = True

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False
        
        if self.draw_menu and self.menu_active:
            if len(self.options) != 0:
                longest = max(self.options.values(), key=len)
                for i, text in enumerate(list(self.options.values())[self.range_lower:self.range_upper]):
                    rect = self.rect.copy()
                    rect.h += 10
                    width = max(rect.w ,text_objects(longest, self.font, black)[0].get_width() + 10)
                    rect.y += (i) * rect.h
                    if not i < 0:
                        rect.x -= rect.w
                    rect.x -= width - rect.w
                    rect.w = width
                    if rect.collidepoint(mpos):
                        self.active_option = i
                        self.main = list(self.options.keys())[i + self.range_lower]
                    if i%2 == 0:
                        color = self.color_option[1]
                    else:
                        color = self.color_option[2]
                    pygame.draw.rect(screen, white if i == self.active_option else color, rect, 0)
                    msg = self.font.render(text, 1, [white, primary][1 if i == self.active_option else 0])
                    screen.blit(msg, msg.get_rect(center = rect.center))

                if len(self.options) > (self.range_upper - self.range_lower):
                    hint_rect = pygame.Rect(rect.x + rect.w//4, self.rect.y - rect.h, rect.w//2, rect.h)
                    draw_rect_alpha(screen, white + [240],hint_rect)
                    Text.draw(screen, 'scroll', xsmallfont, grey, (rect.x + rect.w//2), (self.rect.y - rect.h//2))              

        #display selected option
        pygame.draw.rect(screen, self.color_menu[self.rect.collidepoint(mpos)], self.rect, 2, border_top_right_radius = self.rect.h//2, border_bottom_right_radius = self.rect.h//2)
        msg = xsmallfont.render(self.main, 1, grey if self.main == self.default_text else black)
        screen.blit(msg, msg.get_rect(center = (self.rect.center[0],self.rect.center[1] + 1)))

    def add_to_menu(self, key, value):
        if self.dd_type == 'mutable':
            self.options[key] = value
    
    def remove_from_menu(self, key):
        if self.dd_type == 'mutable':
            self.options.pop(key)
    
    def get_selected(self):
        return self.main
    
    def get_selected_text(self):
        if self.main != self.default_text:
            try:
                return self.options[self.main]
            except:
                return 0
        else:
            return 0
    def set_selected(self, value):
        if value in self.options:
            self.main = value
    
    def clear_options(self):
        if self.dd_type == 'mutable':
            self.options = {}

class TextInput():
    text_inputs = {}
    def __init__(self, id, x, y, w ,h, default_text = '', font = xsmallfont, color = black, input_active = False, prev = None, section = 'simulation'):
        self.id = id
        self.x, self.y, self.w, self.h = x,y,w,h
        self.default_text = default_text
        self.user_text = ''
        self.font = font
        self.color = color
        self.input_active = input_active
        self.prev = prev
        self.next = None
        if self.prev !=None:
            self.prev.next = self
        self.section = section
        self.visible = False
        self.input_rect = pygame.Rect(self.x,self.y,self.w,self.h)
        if self.id not in TextInput.text_inputs:
            TextInput.text_inputs[self.id] = self
        else:
            del self
            raise Exception
        
    def draw(self, screen):
        if self.input_active:
            pygame.draw.rect(screen, primary, (self.x,self.y,self.w,self.h), 2, border_radius = self.w//10)
            draw_rect_alpha(screen, white + [240],(self.x , self.y  - self.h, self.w, self.h))
            Text.draw(screen, self.default_text, self.font, primary, (self.input_rect.x + self.input_rect.w//2), (self.input_rect.y - self.input_rect.height//2))
        else:
            pygame.draw.rect(screen, grey, (self.x,self.y,self.w,self.h), 2, border_radius = self.w//10)
            if self.user_text == '':
                Text.draw(screen, self.default_text, self.font, grey, (self.input_rect.x + self.input_rect.w//2), (self.input_rect.y + self.input_rect.height//2))
        
        #draw user text
        self.surface, self.rect = text_objects(self.user_text, self.font, self.color)
        screen.blit(self.surface, (self.input_rect.x + 5, self.input_rect.y + 3))
    
    def set_text(self, text):
        self.user_text = text
    
    def get_text(self):
        return self.user_text.replace(' ','')
    
    def set_active(self):
        self.input_active = True
        for ti in TextInput.text_inputs.values():
            if ti != self:
                ti.set_inactive()         
        time.sleep(0.2)   
    
    def set_inactive(self):
        self.input_active = False
    
    def set_visible(self):
        self.visible = True
    
    def set_invisible(self):
        self.visible = False
    
    def is_visible(self):
        return self.visible
    
    def add_text(self, text):
        self.user_text += text
    
    def delete_character(self):
        self.user_text = self.user_text[:-1]
    
    def delete_text(self):
        self.user_text = ''
    
    def get_section(section):
        inputs = []
        for ti in TextInput.text_inputs.values():
            if ti.section == section:
                inputs.append(ti)
        return inputs
    
    def draw_sections(screen, sections):
        for ti in TextInput.text_inputs.values():
            if ti.section in sections: ti.draw(screen)
        TextInput.make_sections_visible(sections)

    def make_sections_visible(sections):
        for ti in TextInput.text_inputs.values():
            if ti.section in sections: ti.set_visible()
            else: ti.set_invisible()

class Button():
    buttons = {}
    def __init__(self, id, text, x, y, w, h, inactive_color, active_color, action=None, size = 's', color = white, section = 'title'):
        self.id = id
        self.x, self.y, self.w, self.h = x,y,w,h
        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
        self.rect_copy = self.rect.copy()
        self.cooldown = False
        self.cooldown_counter = True
        self.text = text
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.action = action
        self.size = size
        self.text_color = color
        self.visible = False
        self.section = section
        if self.id not in Button.buttons:
            Button.buttons[self.id] = self
        else:
            del self
            raise Exception
    
    def draw(self, screen):
        if self.cooldown:
            self.rect = pygame.Rect(self.x-2.5,self.y-2.5,self.w+5,self.h+5)
            self.cooldown_counter +=1
            if self.cooldown_counter >= 8:
                self.rect = self.rect_copy
                self.cooldown = False
                self.cooldown_counter = 0

        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            pygame.draw.rect(screen, self.active_color, self.rect, border_radius = self.w//2)
        else:
            pygame.draw.rect(screen, self.inactive_color,self.rect, border_radius = self.w//2)

        if self.size == 'xs':
            font = xsmallfont
        elif self.size == 's':
            font = smallfont
        elif self.size == 'm':
            font = mediumfont
        elif self.size == 'l':
            font = largefont
        else:
            font = xlargefont
        Text.draw(screen, self.text, font, self.text_color, (self.x + (self.w/2)), (self.y + (self.h/2)))
    
    def set_visible(self):
        self.visible = True
    
    def set_invisible(self):
        self.visible = False
    
    def draw_sections(screen, sections):
        for button in Button.buttons.values():
            if button.section in sections: button.draw(screen)
        Button.make_sections_visible(sections)

    def make_sections_visible(sections):
        for button in Button.buttons.values():
            if button.section in sections: button.set_visible()
            else: button.set_invisible()

class Text():
    def draw(screen, text, font, color, x, y):
        surf, rect = text_objects(text, font, color)
        rect.center = (x,y)
        screen.blit(surf,rect)
        