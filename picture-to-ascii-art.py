#!/bin/env python

import os
from PIL import Image, ImageDraw, ImageFont
from numpy import tan, sin, cos, deg2rad, pi, linspace

########    helper functions #########################################

def provide_path(extension, expression):
    # TODO: use specific Exception or subclass it
    path = input(str(expression))
    PATH =[]
    if not os.path.isfile(path):
        if os.path.isdir(path):
            dir_files = os.listdir(path)
            for file in dir_files:
                if file.endswith(extension):
                    PATH.append(path + file)
            if PATH == []:
                return print('there is not image file in this directory')
            if (retval := select_valid('would you like to convert all image files from this directory ? (y/n)', 'y', 'n')) == 'y':
                return PATH
            PATH_COPY = [file for file in PATH]
            for file in PATH_COPY:
                file_name = file.removeprefix(path + '/')
                if (retval := select_valid(f"would you like to convert {file_name} ? (y/n)", 'y', 'n')) == 'n':
                    PATH.remove(file)
            if PATH == []:
                return print("you have not selected any image to convert")
            return PATH
        return print(f"file {path} doesn\'t exist")
    if path.endswith(extension):
        PATH.append(path)
        return PATH
    else:
        return print('file extension is not supported')

def select_valid(prompt, *args):
    while True:
        if (retval := input(prompt).lower()) in args:
            return retval

def select_val_in_interval(prompt, mini, maxi):
    while True:
        try:
            if mini <= (answer := int(input(prompt))) <= maxi:
                return answer
        except ValueError:
            continue

########    Engine Base class #######################################

class Ascii_art:
    def __init__(self, parser_dict = None): 
        self.SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg']
        self.ratio = 0.5                     # shall we put this value as variable ? increase number of characters  
        self.one_char_width = 8*self.ratio   # 8x16pixels was the standard for terminal char size, 
        self.one_char_height = 16*self.ratio # the resolution was 640x480 for 80x20 characters
        self.char_ratio = self.one_char_height/self.one_char_width
        #TODO one day, it should be good to make it possible to decide how many chars in density
        density = self.select_density()
        self.char_array = list(density)
        self.interval = len(self.char_array)/256
        if parser_dict is None:
            self.MY_IMAGES = provide_path(tuple(self.SUPPORTED_EXTENSIONS),'Provide an image path or a directory containing images : ')
            if isinstance(self.MY_IMAGES, list):
                self.AVAILALE_OUTPUT = ['text', 'image', 'python', 'terminal']
                self.SCALE = self.scale() 
                self.BACKGROUND_COLOR = self.background_color()
        else:
            self.__dict__.update(**parser_dict)
            # the parser should provide a dict containing keys : 'MY_IMAGES', 'AVAILALE_OUTPUT', 'SCALE', 'BACKGROUND_COLOR'
            # if parser_dict['AVAILABLE_OUTPUT'] == 'image' 
            # parser_dict['IM_ARG'] = tuple( width_diffusion, angle, origine_effect) Cf self.fusion_ascii_and_original
    
    def select_density(self):
        if (user_input := select_valid('Would you like to use 70 or 10 differents characters ? (70/10) : ', '70', '10')) == '70':
            return "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
        else:
            return " .:-=+*#%@"

    def scale(self, size = None):
        if not size:
            if (user_input := select_valid('Would you like to change the output scale ? (y/n) : ', 'y', 'n')) == 'n':
                return 1/self.one_char_height
            else:
                user_input = select_val_in_interval('Provide a pourcentage for the scale between 5 and 200% : ', 5, 200)
                return user_input/100/self.one_char_height
        else:   #if size != None, it means self.OUTPUT_TYPE == 'terminal' and the image need to be reduced 
            col,lin = os.get_terminal_size() 
            width, height = size
            if col/lin <= width/height :
                ratio = col/width
            else:
                ratio = (lin - 1)/height #-1 to keep a line for request
            return ratio * self.SCALE
    
    def select_output_type(self):
        if len(self.AVAILALE_OUTPUT) > 1:
            return select_valid(f"Which output type would you want to create ? ({'/'.join(self.AVAILALE_OUTPUT)}) : ", *self.AVAILALE_OUTPUT)
        return ''.join(self.AVAILALE_OUTPUT)
    
    def make_array(self):
        return [self.create_datas_tuple(file) for file in self.MY_IMAGES]
    
    def create_datas_tuple(self,PATH, scale = None):
        if not scale :          #if scale, it's because of the fact output is terminal and need to be resized
            scale = self.SCALE
        array_pixels_datas = []
        original_image = Image.open(PATH)
        original_width,original_height = original_image.size #method from PIL which return a tuple defining the size of an image
        image = original_image.resize((int(original_width * scale * self.char_ratio), int(original_height * scale)), Image.Resampling.NEAREST)
        width, height = image.size
        resized_picture = image.load() #Allocates storage for the image and loads the pixel data as tuple 
        for y in range(height):
            line = []
            for x in range(width):
                r,g,b,*A = resized_picture[x,y]
                char = self.select_char(int((r+g+b)/3))
                line.append((char, (r,g,b,(a:=A if A else 255))))
            array_pixels_datas.append(line)
        return (PATH, (width, height), array_pixels_datas, (original_width, original_height))

    def select_char(self, value):
        return self.char_array[round(value * self.interval)-1]

    def background_color(self):
        if (user_input := select_valid('Would you like to define a background color ? (y/n) : ', 'y', 'n')) == 'n':
            return None
        else:
            user_input = select_valid('select background color : white, black or custom (w/b/c) : ', 'w', 'b', 'c')
            if user_input == 'w':
                return (255, 255, 255, 255)
            elif user_input == 'b':
                return (0, 0, 0, 255)
            else:
                background = []
                nota_bene = ''
                for item in tuple(map(str, 'RGBA')):
                    if item == 'A':
                        nota_bene = " (will be usefull only for 'image' output)" 
                    val = select_val_in_interval(f"provide a value for {item}{nota_bene} : ", 0, 255)
                    background.append(val)
                return tuple(background)

    def transform_to_ascii(self, datas):
        PATH, size, array_pixels_datas, original_size = datas
        if self.OUTPUT_TYPE == 'text':
            new_path = self.new_path(PATH) + '.txt'
            My_ascii = self.ascii_for_text(PATH, size, array_pixels_datas, new_path)
        elif self.OUTPUT_TYPE == 'python':
            new_path = self.new_path(PATH) + '.py'
            My_ascii = self.ascii_for_python(PATH, size, array_pixels_datas, new_path)
        elif self.OUTPUT_TYPE == 'terminal':
            if (need_modification := self.check_terminal_size(size)) == None:
                My_ascii = self.ascii_for_terminal(PATH, size, array_pixels_datas)
            else:
                My_ascii = self.ascii_for_terminal(PATH, size, array_pixels_datas, resize = True)
        elif self.OUTPUT_TYPE == 'image':
            new_path = self.new_path(PATH) + '-ascii_art.png'
            width, height = size
            size = (width * self.one_char_width, height * self.one_char_height)
            My_ascii = self.ascii_for_image(PATH, size, original_size, array_pixels_datas, new_path)
            if (user_input := select_valid('Do you want to merge the original file with the ascii art file to create effect ? (y/n) ', 'y', 'n')) == 'y':
                self.fusion_ascii_and_original(PATH, size, new_path)

    def new_path(self, path):
        for extension in self.SUPPORTED_EXTENSIONS:
            if path.endswith(extension):
                path = path.removesuffix(extension)
                return path

    def ascii_for_text(self, PATH, size, array_pixels_datas, new_path):
         with open(f"{new_path}", "w") as text:
            for line in array_pixels_datas:
                for pixel in line:
                    (char, color) = pixel 
                    text.write(char)
                text.write('\n')

    def ascii_for_python(self, PATH, size, array_pixels_datas, new_path):
        width, height = size
        if not self.BACKGROUND_COLOR:
            bg_start = bg_end = ''
        else:
            R_bg, G_bg, B_bg, A_bg = self.BACKGROUND_COLOR
            bg_start = f"\\x1b[48;2;{R_bg};{G_bg};{B_bg}m"
            bg_end = '\\x1b[1m'
        array_name = input('give a name to your final array : ')
        with open(f"{new_path}", "w") as text:
            text.write(f"{array_name} = [\n")
            for y,line in enumerate(array_pixels_datas):
                line_buffer = []
                text.write('[' + bg_start)
                for x, pixel_datas in enumerate(line):
                    char, pixel_color = pixel_datas
                    r,g,b = tuple([canal for canal in pixel_color][:3]) #don't take in consideration alpha canal if there is one 
                    fg = f"\\x1b[38;2;{r};{g};{b}"
                    text.write(''.join("'" + fg +'m' + char + "'"))
                    if x != width-1 :
                        text.write(', ')
                if y != height-1:
                    text.write('],\n')
                else:
                    text.write(']\n]\n')

    def ascii_for_terminal(self, PATH, size, array_pixels_datas, resize = None):
        if resize :
            temp_scale = self.scale(size)
            temp_path, temp_size, datas, original_size = self.create_datas_tuple(PATH, scale = temp_scale)
        else:
            datas = array_pixels_datas
        bg_end = '\x1b[1m'
        if not self.BACKGROUND_COLOR:
            bg_start = ''
        else:
            R_bg, G_bg, B_bg, A_bg = self.BACKGROUND_COLOR
            bg_start = f"\x1b[48;2;{R_bg};{G_bg};{B_bg}m"
        for line in datas:
            line_buffer = []
            line_buffer.append(bg_end + bg_start)
            for pixel_datas in line:
                char, pixel_color = pixel_datas
                r,g,b = tuple([canal for canal in pixel_color][:3]) 
                fg = f"\x1b[38;2;{r};{g};{b}"
                line_buffer.append(fg + 'm' + char)
            line_buffer.append(bg_end)
            print(''.join(line_buffer) + '\x1b[0m')

    def check_terminal_size(self, size):
        col,lin = os.get_terminal_size()
        width, height = size
        if col < width or lin < height:
            return True
        return None

    def ascii_for_image(self, PATH, size, original_size, array_pixels_datas, new_path):
        width, height = int(original_size[0]*(scale := self.SCALE*self.one_char_height)),int(original_size[1]*scale)
        if self.BACKGROUND_COLOR:
            R,G,B,A = self.BACKGROUND_COLOR
        else:
            R = G = B = A = 255
        my_ascii_art = Image.new('RGBA', (width, height), color = (R,G,B,A))
        ascii_art = ImageDraw.Draw(my_ascii_art)
        FONT_SIZE = select_val_in_interval('Choose the policy size between 6 and 10pts : ', 6, 10)
        FONT = ImageFont.truetype(self.is_font(), FONT_SIZE)
        for y, line in enumerate(array_pixels_datas):
            for x, pixel_datas in enumerate(line):
                char, (r,g,b,a) = pixel_datas
                ascii_art.text((x*self.one_char_width, y*self.one_char_height), char, font = FONT, fill = (r,g,b))
        my_ascii_art.save(new_path)

    def is_font(self):
        path_font = '/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Bold.otf'
        if not os.path.isfile(path_font):
            print(path_font, 'doesn\'t exist \nplease provide a path for the font you want to use \nto get a good result select a monospaced font \nusually in usr/share/fonts')
            path_font = provide_path(('.ttf', '.otf'),'Provide a font path : ')
        return path_font

    def another_output(self):
        return (user_input := select_valid('Would you like to try an other output type ? (y/n) : ', 'y', 'n'))

    def provide_width_diffusion(self, width):
        user_input = select_val_in_interval('Provide a pourcentage for the width diffusion effect : ', 1, 100)
        return user_input*width/100

    def provide_angle(self):
        user_input = select_val_in_interval("Provide an angle in degrees for the effect between -180 and 180 (0 = horizontal/ 90 = vertical) : ", -180, 180)
        return user_input

    def provide_origine_effect(self,width, height, angle):
        abscissa = ordinate = 0
        if abs(angle) not in [0,180]:
            abscissa = int(select_val_in_interval(f"Provide the origine abscissa in range [0;{width-1}] : ", 0, width-1))
        if abs(angle) != 90 :
            ordinate = int(select_val_in_interval(f"Provide the origine ordinate in range [0;{height-1}] : ", 0, height-1))
        return (abscissa, ordinate)

    def fusion_ascii_and_original(self, PATH, size, new_path):
        width, height =[int(el) for el in size]
        width_diffusion = self.provide_width_diffusion(width)               #
        angle = self.provide_angle()                                        # if not parser_dict
        origine_effect = self.provide_origine_effect(width, height, angle)  #
        # TODO 
        # width_diffusion, angle, origine_effect = self.__dict__.get('IM_ARG', (50, 0,size([0]/2,size[1]/2)))
        x_origine, y_origine = origine_effect
        ascii_im = Image.open(new_path)
        original_im = Image.open(PATH).resize((width, height), Image.Resampling.NEAREST)
        future_output = Image.new('RGB', (width, height), color = (0,0,0))
        output = self.fusion(width, height, width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, future_output)
        new_path = self.new_path(PATH) + '_fusion_effects.png'
        output.save(new_path)
    
    def fusion(self,width, height, width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, future_output):
        im1 = ascii_im.load()
        im2 = original_im.load()
        pixels_fusion = future_output.load()
        tan_angle = tan(deg2rad(angle))
        half_width_dif = width_diffusion/2
        const = y_origine - (tan_angle*x_origine)
        delta = half_width_dif/sin(deg2rad(90 - angle))
        f = lambda x : tan_angle*x + const
        start = lambda x : f(x) + delta
        end = lambda x : f(x) - delta
        if abs(angle)>90:
            im1,im2,start,end  = im2,im1,end,start
        if abs(angle) != 90:
            for y in range(height-1,0,-1):
                for x in range(width):
                    Y = height-y
                    if y > start(x):
                        pixels_fusion[x,Y] = im1[x,Y]
                    elif end(x) <= y <= start(x):
                        ratio = abs((y - end(x))/(2*delta)) #if abs(angle)>90 : ratio < 0
                        pixels_fusion[x,Y] = tuple(map(lambda i,j : int(j*(1-ratio)+i*ratio), im1[x,Y], im2[x,Y]))
                    else:
                        pixels_fusion[x,Y] = im2[x,Y]
        else:        
            start_x = x_origine - half_width_dif 
            end_x = x_origine + half_width_dif
            if angle < 0:
                im1,im2 = im2,im1
            for y in range(height):
                for x in range(width):
                    if x < start_x:
                        pixels_fusion[x,y] = im1[x,y]
                    elif start_x <= x <= end_x:
                        ratio = (end_x - x)/ width_diffusion
                        pixels_fusion[x,y] = tuple(map(lambda i,j : int(j*(1-ratio)+i*ratio), im1[x,y], im2[x,y]))
                    else:
                        pixels_fusion[x,y] = im2[x,y]
        return future_output 

if __name__ == '__main__':
    while True:
        try:
            project = Ascii_art()
            if isinstance(project.MY_IMAGES, list):
                ARRAY = project.make_array() #composed of array for each file which represents pixels datas (char and color)
                while True:
                    project.OUTPUT_TYPE = project.select_output_type()
                    for i, array in enumerate(ARRAY):
                        project.transform_to_ascii(array)
                        if project.OUTPUT_TYPE == 'terminal' and len(ARRAY) > 1 and i != len(ARRAY) - 1:
                            input('press enter to print next image')
                    project.AVAILALE_OUTPUT.remove(project.OUTPUT_TYPE)
                    if not project.OUTPUT_TYPE or project.another_output() == 'n':
                        break
                if (user_input := select_valid('Would you like to start an other project ? (y/n) : ', 'y', 'n')) == 'n':
                        raise KeyboardInterrupt
        except KeyboardInterrupt:
            print('\x1b[H\x1b[2J', end='')
            break
