#!/bin/env python

import os
from PIL import Image, ImageDraw, ImageFont
from math import cos, sin, tan, radians

########    helper functions #########################################

def provide_path(extension, expression):
    # TODO: use specific Exception or subclass it
    PATH = input(str(expression))
    if not os.path.isfile(PATH):
        if os.path.isdir(PATH):
            raise Exception(PATH + ' is not file, it is a directory')
        raise Exception(f"file {PATH} doesn\'t exist")
    if not PATH.endswith(extension):
        raise Exception('file extension is not supported')
    return PATH

def select_valid(prompt, *args):
    while True:
        if (retval := input(prompt)) in args:
            return retval

def select_val_in_interval(prompt, mini, maxi):
    while True:
        if mini <= (answer := int(input(prompt))) <= maxi:
            return answer

########    Engine Base class #######################################

class My_ascii:
    def __init__(self):
        self.one_char_width = 5          # magic values defining "roof tiles" size
        self.one_char_height = 10        # probably need to modify according to policy
        self.char_ratio = self.one_char_height/self.one_char_width
        density = '@#W$?!;:+=-,.- '
        self.char_array = list(density)
        self.interval = len(self.char_array)/256
        self.font = self.is_font()
        self.original_image = Image.open(PATH)
        self.scale = self.scale()
        self.reduce_original_image = self.reduce_image(self.original_image, self.scale)
        self.width, self.height = self.reduce_original_image.size
        self.resized_picture = self.reduce_original_image.load()
        self.mode = self.original_image.mode

    def is_font(self):
        path_font = '/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Bold.otf'
        if not os.path.isfile(path_font):
            print(path_font, 'doesn\'t exist \nplease provide a path for the font you want to use \nto get a good result select a monospaced font \nusually in usr/share/fonts')
            path_font = provide_path(('.ttf', '.otf'),'Provide a font path : ')
        return path_font

    def reduce_image(self, image, scale):
        width, height = image.size
        width, height = int(width*scale*self.char_ratio), int(height*scale)
        image = image.resize((width, height), Image.Resampling.NEAREST)
        return image

    def convert_to_grayscale(self):
        pass

    def scale(self):
        user_input = select_valid('Would you like to change the output scale ? (y/n) : ', 'y', 'n')
        if user_input == 'n':
            return 0.1
        else:
            user_input = select_val_in_interval('Provide a pourcentage for the scale between 5 and 200% : ', 5, 200)
            return user_input * 0.001

    def select_char(self, value):
        return self.char_array[round(value * self.interval)-1]

    def background_color(self):
        if OUTPUT_FORMAT == 'i': #if output format is image, need a value to create self.new_image, answer can't be 'n' !!!
            user_input = 'y'
        else:
            user_input = select_valid('Would you like to change the background color ? (y/n) : ', 'y', 'n')
        if user_input == 'n':
            return None
        else:
            user_input = select_valid('select background color : white, black or custom (w/b/c) : ', 'w', 'b', 'c')
            if user_input == 'w':
                return (255, 255, 255)
            elif user_input == 'b':
                return (0, 0, 0)
            else:
                background = []
                for item in tuple(map(str, self.mode)):
                    while True:
                        if item == 'A' and OUTPUT_FORMAT == 't': #cause we ignore alpha canal in terminal !!!
                            break
                        val = input('provide a value for ' + item + ' : ')
                        try:
                            rv = int(val)
                            if rv in range(256):
                                background.append(rv)
                                break
                        except:
                            continue
                return tuple(background)

class Text(My_ascii):
    def transform_to_ascii(self):
        user_input = select_valid('Would you like to get a .txt file,a .py file, or print on terminal (txt/py/p) ? : ', 'txt','py', 'p')
        if user_input == 'txt':
            self.ascii_text_file()
        else:
            self.background_color = self.background_color()
            if user_input == 'py':
                self.ascii_py_file()
            elif user_input == 'p':
                self.ascii_terminal()

    def ascii_text_file(self):
        with open("my_ascii.txt", "w") as text:
            for y in range(self.height):
                for x in range(self.width):
                    try:
                        r,g,b = self.resized_picture[x,y]
                    except ValueError:
                        r,g,b,a = self.resized_picture[x,y]
                    average = int((r+g+b)/3)
                    text.write(self.select_char(average))
                text.write('\n')

    def _round_rgb_greyscale(self, value, container):
        rv = 0
        for i, container_value in enumerate(container):
            if value == 0:
                break
            elif value <= container_value:
                if 2*value - container_value - container[i-1] <= 0:
                    rv = container[i-1]
                    break
                else:
                    rv = container_value
                    break
        return (rv,rv,rv)

    def _round_rgb_colors(self, rgb_tuple, container1, container2):
        flag = 0
        output = []
        for rgb_value in rgb_tuple:
            if rgb_value in container1:     #avoid to round a color system with 128 value
                flag += 1
            for i, container2_value in enumerate(container2):
                if rgb_value == 0:
                    output.append(rgb_value)
                    break
                elif rgb_value <= container2_value:
                    if 2*rgb_value - container2_value - container2[i-1] <= 0:
                        output.append(container2[i-1])
                        break
                    else:
                        output.append(container2_value)
                        break
        if flag == 3 :
            return rgb_tuple
        else:
            return tuple(output)

    def ascii_py_file(self):
        colors_system = [0, 128] # not inclued 192 cause it's only for greyscale / not inclued 255 cause it will rounded to 255
        greyscale = [0, 18, 28, 38, 48, 58, 68, 78, 88, 95, 98, 108, 118, 128, 135, 138, 148, 158, 168, 178, 188, 192, 198, 208, 215, 218, 228, 238, 255]
        colors = [0, 95, 135, 175, 215, 255]
        round_rgb = ()
        buffer = []
        file_name = input('give a name to your file : ')
        array_name = input('give a name to your final array : ')
        with open(f"{file_name}.py", "w") as text:
            if not self.background_color:
                bg = 'm'
            else:
                try:
                    R_bg, G_bg, B_bg = self._round_rgb_colors(self.background_color, colors_system, colors)
                except ValueError:
                    R_bg, G_bg, B_bg, A_bg = self._round_rgb_colors(self.background_color, colors_system, colors)
                bg = f";48;2;{R_bg};{G_bg};{B_bg}m"
            text.write(f"{array_name} = [\n")
            for y in range(self.height):
                line_buffer = []
                text.write('[')
                for x in range(self.width):
                    try:
                        r,g,b = self.resized_picture[x,y]
                    except ValueError:
                        r,g,b,a = self.resized_picture[x,y]
                    average = int((r+g+b)/3)
                    if r == g == b :
                        round_rgb = self._round_rgb_greyscale(r, greyscale)
                    else:
                        round_rgb = self._round_rgb_colors((r,g,b), colors_system, colors)
                    fg = f"\\x1b[38;2;{r};{g};{b}"
                    text.write(''.join("'" + fg + bg + self.select_char(average)+"\\x1b[0m'"))
                    if x != self.width-1 :
                        text.write(', ')
                if y != self.height-1:
                    text.write('],\n')
                else:
                    text.write(']]\n')

    def ascii_terminal(self):
        colors_system = [0, 128] # not inclued 192 cause it's only for greyscale / not inclued 255 cause it will rounded to 255
        greyscale = [0, 18, 28, 38, 48, 58, 68, 78, 88, 95, 98, 108, 118, 128, 135, 138, 148, 158, 168, 178, 188, 192, 198, 208, 215, 218, 228, 238, 255]
        colors = [0, 95, 135, 175, 215, 255]
        round_rgb = ()
        buffer = []
        if not self.background_color:
            bg = 'm'
        else:
            try:
                R_bg, G_bg, B_bg = self._round_rgb_colors(self.background_color, colors_system, colors)
            except ValueError:
                R_bg, G_bg, B_bg, A_bg = self._round_rgb_colors(self.background_color, colors_system, colors)
            bg = f";48;2;{R_bg};{G_bg};{B_bg}m"
        for y in range(self.height):
            for x in range(self.width):
                try:
                    r,g,b = self.resized_picture[x,y]
                except ValueError:
                    r,g,b,a = self.resized_picture[x,y]
                average = int((r+g+b)/3)
                if r == g == b :
                    round_rgb = self._round_rgb_greyscale(r, greyscale)
                else:
                    round_rgb = self._round_rgb_colors((r,g,b), colors_system, colors)
                fg = f"\x1b[38;2;{r};{g};{b}"
                buffer.append(fg + bg + self.select_char(average))
            buffer.append('\n')
        print(''.join(buffer) + '\x1b[0m')

class Picture(My_ascii):
    def __init__(self):
        My_ascii.__init__(self)
        self.font_size = select_val_in_interval('Choose the policy size between 6 and 12pts : ', 6, 12)
        self.font = ImageFont.truetype(self.font, self.font_size)
        self.background_color = self.background_color()

    def create_new_image(self):
        if self.mode == 'RGB':
            R,G,B = self.background_color
            self.new_image = Image.new(self.mode, (self.width*self.one_char_width, self.height*self.one_char_height), color = (R,G,B))
        elif self.mode == 'RGBA':
            try:
                R,G,B,A = self.background_color
            except ValueError:
                R,G,B = self.background_color
                A = select_val_in_interval('Provide alpha canal value in range [0,255] : ', 0, 255)
            self.new_image = Image.new(self.mode, (width*self.one_char_width, height*self.one_char_height), color = (R,G,B,A))
        else :
            raise Exception("the mode " + self.mode + " isn't compatible ! only for RGB or RGBA")
        return self.new_image

    def transform_to_ascii(self):
        my_ascii_art = self.create_new_image()
        ascii_art = ImageDraw.Draw(my_ascii_art)
        if self.mode == 'RGB':
            for y in range(self.height):
                for x in range(self.width):
                    r,g,b = self.resized_picture[x,y]
                    average = int((r+g+b)/3)
                    self.resized_picture[x,y]=(average,average,average)
                    ascii_art.text((x*self.one_char_width, y*self.one_char_height),
                                    self.select_char(average),
                                    font = self.font,
                                    fill = (r,g,b))
        else:
            for y in range(self.height):
                for x in range(self.width):
                    r,g,b,a = self.resized_picture[x,y]
                    average = int((r+g+b)/3)
                    self.resized_picture[x,y]=(average,average,average, a)
                    ascii_art.text((x*self.one_char_width, y*self.one_char_height),
                                    self.select_char(average),
                                    font = self.font,
                                    fill = (r,g,b))
        while True:
            fp = input('Give a name to the file (will be saved in current directory, else provide path) : ')
            try:
                my_ascii_art.save(fp)
                self.fp = fp
                break
            except Exception as e :
                print(type(e))
                continue

    def provide_width_diffusion(self):
        user_input = select_val_in_interval('Provide a pourcentage for the width diffusion effect : ', 1, 100)
        return user_input*self.width/100

    def provide_angle(self):
        user_input = select_val_in_interval("Provide an angle in degrees for the effect between -180 and 180 (0 = vertical / 90 = horizontal) : ", -180, 180)
        return user_input

    def provide_origine_effect(self, angle):
        if abs(angle) != 90:
            abscissa = int(select_val_in_interval(f"Provide the origine abscissa in range [0;{self.width-1}] : ", 0, self.width-1))
        else:
            abscissa = 0
        if angle != 0 and abs(angle) != 180 :
            ordinate = int(select_val_in_interval(f"Provide the origine ordinate in range [0;{self.height-1}] : ", 0, self.height-1))
        else:
            ordinate = 0
        return (abscissa, ordinate)

    def fusion_ascii_and_original(self):
        im1 = Image.open(self.fp)
        self.width, self.height = im1.size
        width_diffusion = ascii_art.provide_width_diffusion()
        angle = ascii_art.provide_angle()
        origine_effect = ascii_art.provide_origine_effect(angle)
        x_origine, y_origine = origine_effect
        ascii_im = Image.open(self.fp)
        if self.scale == 0.1:
            original_im = self.original_image
        else:
            original_im = self.original_image.resize((self.width, self.height), Image.Resampling.NEAREST)
        future_output = Image.new(self.mode, (self.width, self.height), color = (0,0,0))
        straight_array = [0,90,180]
        if abs(angle) in straight_array:
            output = self.fusion_straight(width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, future_output)
        else:
            output = self.fusion_angle(width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, future_output)
        while True:
            fp = input('Give a name to the file (will be saved in current directory, else provide path) : ')
            try:
                output.save(fp)
                self.fp = fp
                break
            except Exception as e :
                print(type(e))
                continue

    def fusion_straight(self, width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, output):
        if angle == 90:
            ascii_im = ascii_im.rotate(90)
            original_im = original_im.rotate(90)
            output = output.rotate(90)
            x_origine, y_origine = y_origine, x_origine
        elif angle == -90:
            ascii_im = ascii_im.rotate(270)
            original_im = original_im.rotate(270)
            output = output.rotate(270)
            x_origine, y_origine = y_origine, x_origine
        elif abs(angle) == 180:
            ascii_im, original_im = original_im, ascii_im
        im1 = ascii_im.load()
        im2 = original_im.load()
        pixels_fusion = output.load()
        start_x = int(x_origine - width_diffusion/2)
        end_x = int(x_origine + width_diffusion/2)
        if end_x > self.width:
            end_x = self.width
        for y in range(self.height):
            x = 0
            if start_x >= 0:
                i = 1
            else:
                i = abs(start_x + 1)
            interval = i * 100 / width_diffusion
            while x < start_x:
                if x >= self.width:
                    break
                pixels_fusion[x,y] = im1[x,y]
                x += 1
            while x <= end_x:
                if x >= self.width:
                    break
                interval = i * 100 / width_diffusion
                pixels_fusion[x,y] = tuple(map(lambda i,j : int((i*(100-interval)+j*interval)/100), im1[x,y], im2[x,y]))
                x += 1
                i += 1
            while x != self.width:
                pixels_fusion[x,y] = im2[x,y]
                x += 1
        if angle == 90:
            output = output.rotate(270)
        elif angle == -90:
            output = output.rotate(90)
        return output

    def y_origine_for_x_origine_plus_1(self, angle):
        interval = tan(radians(angle))
        change_statement = []
        ret_val = round(interval)
        for i in range(self.height):
            temp_val = round(i*interval)
            if temp_val != ret_val:
                change_statement.append(i)
                ret_val = temp_val
            i += 1
        return change_statement

    def new_width_diffusion(self, width_diffusion, angle):
        new_width_diffusion = width_diffusion/cos(radians(angle))
        return new_width_diffusion

    def fusion_angle(self, width_diffusion, angle, x_origine, y_origine, ascii_im, original_im, output):
        first_angle_value = angle
        if not -45 <= angle <= 45:
            if 45 < angle < 135:
                new_angle = 90 - angle
                ascii_im = ascii_im.rotate(90)
                original_im = original_im.rotate(90)
                self.width, self.height = self.height, self.width
            elif  -135 < angle < -45:
                new_angle = 90 + angle
                ascii_im = ascii_im.rotate(270)
                original_im = original_im.rotate(270)
                self.width, self.height = self.height, self.width
            elif 135 <= angle < 180:
                ascii_im, original_im = original_im, ascii_im
                new_angle = angle - 180
            elif -135 >= angle > -180:
                ascii_im, original_im = original_im, ascii_im
                new_angle = angle + 180
            angle = new_angle
        if angle > 0:
            increment = -1
        else:
            increment = 1
        starting_central_pixel_value = round(tan(radians(angle))*y_origine) + x_origine
        change_central_pixel_value = self.y_origine_for_x_origine_plus_1(angle)[::-1]
        new_width_diffusion = self.new_width_diffusion(width_diffusion, angle)
        output = Image.new(self.mode, (self.width, self.height), color = (0,0,0))
        im1 = ascii_im.load()
        im2 = original_im.load()
        pixels_fusion = output.load()
        start_x = int(starting_central_pixel_value - new_width_diffusion/2)
        end_x = int(starting_central_pixel_value + new_width_diffusion/2)
        next_step = change_central_pixel_value.pop()
        for y in range(self.height):
            x = 0
            if start_x >= 0:
                i = 1
            else:
                i = abs(start_x + 1)
            while x < start_x:
                if x == self.width:
                    break
                pixels_fusion[x,y] = im1[x,y]
                x += 1
            while x <= end_x:
                if x == self.width:
                    break
                pixels_fusion[x,y] = im1[x,y]
                interval = i * 100 / new_width_diffusion
                pixels_fusion[x,y] = tuple(map(lambda a,b : int((a*(100-interval)+b*interval)/100), im1[x,y], im2[x,y]))
                x += 1
                i += 1
            while x != self.width:
                pixels_fusion[x,y] = im1[x,y]
                pixels_fusion[x,y] = im2[x,y]
                x += 1
            if y == next_step:
                start_x += increment
                end_x += increment
                try:
                    next_step = change_central_pixel_value.pop()
                except:
                    pass
        if 45 < first_angle_value < 135:
            output = output.rotate(270)
        elif  -135 < first_angle_value < -45:
            output = output.rotate(90)
        return output

if __name__ == '__main__':
    # TODO: those two next globals should be given to __init__ 
    #       and become private.

    PATH = provide_path(('.png', '.jpg', '.jpeg'),'Provide an image path : ')
    OUTPUT_FORMAT = select_valid('Do you want an txt file or an image ? (t/i) ', 't', 'i')

    if OUTPUT_FORMAT == 't':
        ascii_art = Text()
    elif OUTPUT_FORMAT == 'i':
        ascii_art = Picture()

    ascii_art.transform_to_ascii()

    if OUTPUT_FORMAT == 'i':
        user_input = select_valid('Do you want to merge the original file with the ascci art file ? (y/n) ', 'y', 'n')
        if user_input == 'y':
            ascii_art.fusion_ascii_and_original()
