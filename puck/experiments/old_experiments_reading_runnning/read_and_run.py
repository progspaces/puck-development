# Tkinter imports and set up, necessary before the rest of the imports for macOS
from tkinter import *
base = Tk()
base.tk.call('tk', 'scaling', 2.0)
## Name of the window you're opening
base.title('Tkinter Widget Size')
## 1920x1080, display size, +0+-1080 repositioning
base.geometry("1920x1080+0+-1080")
## set to be fullscrean
base.wm_attributes("-fullscreen", True)

## Other Imports
import cv2
from puck.code_modules.dot_finding.dot_finder import find_centers_hough, find_centers_hough_frames
from puck.code_modules.colour_conversion.colour_finding import get_colors_and_coords, get_black_dot
from puck.code_modules.calibration.calibration import get_calibration_colors
from puck.code_modules.geometry.clockwise_dots import order_rectangle
from puck.code_modules.geometry.rectangles import get_all_rects
from puck.code_modules.permutation_guessing.permutation_guessing import get_color_perm_and_dist
from collections import Counter
from puck.image_annotation.annotator import run_radius
from json import load
import importlib

## Errors
NOT_4_DOTS = "not 4 dots"
NOT_RECT = "not rectangular"
NOT_SEEING_FULL_DOTS = "can't see all dots properly",
WARMING_UP = "Warming up"

## Other Constants
CALIBRATION_MIN_DIST = 5
PROGRAM_MIN_DIST= 100
n_colours = 3

## Storage dictionaries and sets
program_lookup = {}
with open('puck/program_store/program_lookup.json') as f:
    program_lookup = dict(load(f))
recognized_in_run = set()
graphics_storage = dict()


def calibration_frame(path, tolerance, radius_already_set = False, preset_radius_range = [16,21], side_add_on = 4):
    ''''
    Takes in the path of an image that is going to be used for calibration
    You set a tolerance I suggest about .2 which is how much error the algorithm 
    will accept when looking for circles in the radius you've selected.
    If you've previously set the radius, please et the radius_already_set to true
    and update preset_radius_range accordingly.
    When it looks at each circle it will grab the surroundings to get a white balance
    That number will be a certain number above the radius range, that is side_add_on, 
    It is preset to 4, you can change it.
    '''
    if radius_already_set:
        rad_range = preset_radius_range 
    else:
        ## Runs a small function that allows the user to click and drag to set a radius of circles in the given image
        print("please click and drag your mouse around one of the calibration circles, " \
              "so we have an approximent size of the circle from the camera's perspective," \
              "press enter when you are satisfied with your circle. click again to draw a new circle.")
        rad_range = run_radius(path,tolerance, name = "Find Circle Radius")
    ## Find the centres of the images circles and returns the image
    cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=False)
    ## If you cannot find all 9 circles, you need to redo the radius size, 
    # and it calls the previous bit on a loop until that condition is satisfied
    while len(cal_centers) < 9:
        print("the sought for circles are not the size specified, please redraw them")
        rad_range = run_radius(path,tolerance, "Nine circles not yet found, redraw radius")
        cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=False)
    ## Get the colors and coordinates of the circles found in the image
    colors_and_coords=get_colors_and_coords(cal_centers,side = int(rad_range[1]) +side_add_on, image =cal_image,colorspace= "RGB")
    ## Figure out which one of these is the black starting dot
    black_dot_cal_coords = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    ## Determine the colors that each circle is (relative to the white paper that surrounds it)
    calibration_colors =get_calibration_colors(black_dot_cal_coords,colors_and_coords,n_colours)
    print(rad_range)
    return calibration_colors, rad_range

def check_coords(colors_and_coords):
     """
     Tells you if there has been a rectangle found in the set of colors and coordinates that represent the circles
     False if no rectangles found at all.
     """
     rect = [[pair[0] for pair in colors_and_coords ]][0]
     return len(get_all_rects(rect)) >0

def single_frame(frame, calibration_colors,radius_range = (17,21), side_set = 10):
    '''
    takes in a frame, and then using the pre-established calibration colors determines what color code is shown
    will return error codes and a fake set of coordinates if runs into any of the following:
        - seeing only a partial dot side, this means some of the dot is occluded and it needs a new frame
        - no rectangle found
        - any number of dots that isn't 4: this is so that we only see one prgoram at a time, will be removed in future iters
    '''
    centers,image = find_centers_hough_frames(frame, min_dist=PROGRAM_MIN_DIST,minRadius=int(radius_range[0]), maxRadius=int(radius_range[1]), grayscale=True)
    try:
        colors_and_coords=get_colors_and_coords(centers,side = side_set, image =image,colorspace= "RGB")
    except:
        return (NOT_SEEING_FULL_DOTS, [(0,0), (0,50), (50,50),(50,0)])
    ### HERES WHERE I NEED TO START MESSING WITH THINGS BECAUSE THE FOUND_RECTANGLE ALONE IS NO LONGER VALID CODE TO TEST




    # found_rectangle = check_coords(colors_and_coords)
    # if len(colors_and_coords) ==4 and found_rectangle:
    #     black_dot = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
    #     ordered_rectangle = order_rectangle(colors_and_coords, black_dot[0]) 
    #     perm,_ = get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
    #     coords_only = ([black_dot[0]] + [x[0] for x in ordered_rectangle])
    #     return (perm,coords_only)
    # elif not found_rectangle:
    #     return (NOT_RECT, [(0,0), (0,50), (50,50),(50,0)]) # error code for not a rectangle
    # else:
    #     return (NOT_4_DOTS,[(0,0), (0,50), (50,50),(50,0)]) ## error code for not 4 dots


def buffer(buffer, input):
    ''' 
    Literally just controls putting things into the buffer and 
    taking things out, a glorified function to pop and append.
    '''
    buffer.pop(0)
    buffer.append(input)
    return buffer

def max_freq(buffer):
    ''' 
    Grabs the most frequent Id in the buffer
    Then gives you back that most fequent ID
    and the coordinate of the last seen copy of that ID
    '''
    ids = [x[0] for x in buffer]
    most_freq = Counter(ids).most_common(1)[0][0]
    most_freq_coords = [x[1] for x in buffer if x[0]==most_freq][-1]
    return (most_freq, most_freq_coords)


def scale(cwidth, cheight, fheight, fwidth, coord_list):
    '''
    An attempt to scale the coordinate system to the webcam space 
    by taking in the width and height of the coordinates space
    and the width and height of the frames taken in
    and scaling all coordinates that are inputted in.
    '''
    scaled_list = [(int(pair[0] * (cwidth/fwidth)), int(pair[1] * (cheight/fheight)) ) for pair in coord_list]
    print(scaled_list)
    return scaled_list


def combined_errors(value):
        return value != NOT_4_DOTS and value != WARMING_UP and value != NOT_RECT and value != NOT_SEEING_FULL_DOTS

def run_spawn(int_form, canvas, box):
        print(program_lookup)
        print(str(int_form))
        print(program_lookup.get(str(int_form)))
        module_name = "puck.program_store." + program_lookup.get(str(int_form))
        module = importlib.import_module(module_name)
        graphics_storage.update({int_form:[]})
        module.on_start(graphics_storage.get(int_form),canvas, box)
        return module


def webcamManyCaptures(calibration_colours, rad_range,base, buffer_size = 35):
    cam = cv2.VideoCapture(0)
    _, frame = cam.read()
    fheight, fwidth, fchannel = frame.shape
    buffer_arr = [("Warming up",[(100,200),(100,400),(200,400),(200,200)])] * buffer_size
    v = StringVar(value= "Warming up") 
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()
    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0), outline='blue',fill="white", width=2)

    def handle_currently_recognized(current_recognized,v):
        if combined_errors(current_recognized[0]): ## it is a paper and thus might have code that needs you to spawn graphics
            int_form = int(current_recognized[0],n_colours)
            if int_form >= 0 and int_form <= 2 or int_form == 7 or int_form == 9: ## in other words the int form is a good value and we like it.
                module_name = "puck.program_store." + program_lookup.get(str(int_form))##
                module = importlib.import_module(module_name)##
                if current_recognized[0] not in recognized_in_run:## Case one: We've never seen this ever before 
                    recognized_in_run.add(current_recognized[0])
                    graphics_storage.update({int_form:[]}) ## create an entry in the graphics storage
                    module.on_start(graphics_storage.get(int_form),canvas, box)
                    print("IT's A NEW PAPER")
                else: ## Case two: We have seen this before
                    previous = v.get()
                    if current_recognized[0] != previous:
                        ## if recognizing a new item, update the label.
                        v.set(current_recognized[0])
                    ## Okay now we need to check if it is a paper program
                    current = v.get()
                    print(f"Current is {current}")
                    v.set(current)
                    scaled = scale(cwidth = cwidth, cheight = cheight, fwidth = fwidth, fheight= fheight, coord_list=current_recognized[1])
                    canvas.coords(box, scaled)
                    module.on_update(graphics_storage.get(int_form),canvas, box)
            else:
                print("we do not have a valid program")
                int_form = -13 ## we do not have a valid programm associated with this
                print(current_recognized[0])
        else:
            # if current_recognized[0] not in recognized_in_run:## we've never seen this error, please add to the list
                # recognized_in_run.add(current_recognized[0])
            v.set(current_recognized[0])
            print(current_recognized[0])
            int_form = -12 ## this is not a paper as we recognize papers


    def update(cam,canvas, box):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv2.namedWindow(window_name, cv2.WINDOW_FREERATIO,)
        cv2.moveWindow(window_name, 0, 300)
        cv2.resizeWindow(window_name, 600, 500)
        cv2.imshow(window_name, frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        response = single_frame(frame,calibration_colours, rad_range)
        buffer(buffer_arr, response)
        canvas.itemconfig(tagOrId = text_label_replace, text=v.get())
        current_recognized = (max_freq(buffer_arr))
        handle_currently_recognized(current_recognized,v)
        if cv2.waitKey(1) == ord('q'): ## stopping condition
            base.quit()
        base.after(10, update, cam, canvas, box)  # Timed Check, adding itself back onto the queue to run 20ms later

    base.after(20,update, cam, canvas, box)
    base.mainloop()
    print(recognized_in_run)
    print(graphics_storage)
    cam.release()
    cv2.destroyAllWindows()


calibration_colors, rad_range = calibration_frame("puck/output/test_cal_higher_projection.jpg", tolerance= .3, radius_already_set=True ,preset_radius_range= [6.3, 11.7])
webcamManyCaptures(calibration_colors, rad_range,base)

