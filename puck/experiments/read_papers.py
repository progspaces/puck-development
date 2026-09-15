#  Tkinter imports and set up, necessary before the rest of the imports for macOS
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
import cv2 as cv
from json import load
import importlib
from matplotlib import pyplot as plt
from collections import Counter
import threading 
import time
from queue import Queue
import logging
from actor import Actor

# Source - https://stackoverflow.com/a/1009864
# Posted by Ayman Hourieh, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-15, License - CC BY-SA 4.0

from argparse import ArgumentParser
# each file should have it's own logger
logger = logging.getLogger(__name__)


DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
program_lookup = {}
with open('puck/program_store/program_lookup.json') as f:
    program_lookup = dict(load(f))
encoding_to_actor = dict()

def average_pt(corners):
    sum_x = 0
    sum_y = 0 
    for pair in corners:
        sum_x += pair[0]
        sum_y += pair[1]
    return (int(sum_x/4), int(sum_y/4))

def paper_frame_based(frame):
    input = frame
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    if ids is not None and len(ids)==4:
        bads = [x for x in ids if x>4]
        if len(bads) >0 :
                ## SAVE WHERE IT SEES THE BAD THING
                copy = cv.aruco.drawDetectedMarkers(input, corners, ids)
                plt.figimage = copy
                plt.savefig('test.png') ##??
        corners_a = corners[0][0]
        corners_b = corners[1][0]
        corners_c = corners[2][0]
        corners_d = corners[3][0]
        averaged_paper = [average_pt(corners_a),
                          average_pt(corners_b),
                          average_pt(corners_d),
                          average_pt(corners_c)]
        return [(averaged_paper, ids)]
    else:
        return[(None,None)]


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
    # print(scaled_list)
    return scaled_list



####
""""
message formating
tuple casing ((),())
first message 
("drawing_queue", drawing_queue)

subsequent messages
("kill")
("new_shape", ())
("canvas_id", ("id":id))
("update_shape",())


new_shape, canvas_id, update_shape
"""
####


def test_run(self:Actor):
    logger.log(level = 17, msg = f"test_run has been called sucessfully")
    first_message=self.recieve()
    assert first_message[0]=="drawing_queue"  ## THIS IS WHAT YOU SHOULD GET
    ## local variables
    drawing_queue= first_message[1]
    associated_canvas_ids=[]
    spawned_actors=[]
    message= self.recieve()
    logger.log(level = 17, msg = f"test_run has been gotten {message}")
    match message:
        case ("kill"):
            self.end()
        case ("new_shape",("type", type),("coordinates", coordinates)):
            drawing_queue.put(("action", ("new", ("type", type), ("sender", self), ("coordinates", coordinates))))
        case ("update_shape",("id", id), ("coordinates", coordinates)):
            drawing_queue.put(("action", ("update", ("id", id), ("coordinates", coordinates))))
        case ("information", *info):
            match info:
                case ("add_ids", id_list):
                    # print("GOT INFO")
                    associated_canvas_ids.append(id_list)
                case _ as info:
                    # print("GOT INFO")
                    print(info)
    logger.log(level = 17, msg = f"test_run has ended...")


def draw_loop(drawing_queue:Queue,canvas:Canvas):
    if drawing_queue.empty() == False:
        message = drawing_queue.get()
        logger.log(level = 17, msg = f"draw loop has been called and has gotten message, {message}")
        # print(f"draw loop {message}")
        match message:
            case "kill"| "Kill":
                print('hmm, not sure yet what to do with this as I am a queue and not an actor.')
            case ("action", _ as action, ):
                match action:
                    case (("new", ("type", type), ("sender", sender), ("coordinates", coordinates))):
                        match type:
                            # sender.send(("id",id))
                            case "rectangle" | "polygon":
                                id = canvas.create_polygon(coordinates)
                                sender.send(("information", ("add_ids", [id])))
                            case _:
                                print(f"You've given me the type '{type}'. I do not know type '{type}', "\
                                    "please try something else, such as 'rectangle' or 'polygon'")
                    case ("new", *invalid_new):
                        print(f"You have provided me this message, {invalid_new}," \
                            "to create a new graphical object, but I'm not sure what type of object. \n " \
                            "It would help if you specified the type of object you want to add.")
                    case ("update", ("id", id), ("coordinates", coordinates), *further_info):
                        canvas.coords(id, coordinates)
                    case _ as invalid_action:
                        print(f"You have provided an invalid action message, '{invalid_action}' is not an action I understand")
            case _ as invalid_message: 
                print(f"You have provided an invalid message, '{invalid_message}' is not a message I understand")
        logger.log(level = 17, msg = f"drawing loop has been reached its end")



def handle_currently_recognized(program_encoding,current_coords, drawing_queue):
        # print("went into currently recognized")
        if program_encoding is not None: ## in other words the int form is a good value and we like it.
            if program_lookup.get(str(program_encoding)) is not None:
                module_name = "puck.program_store." + program_lookup.get(str(program_encoding))##
                module = importlib.import_module(module_name) ##
                if program_encoding not in encoding_to_actor: ## Case one: We've never seen this ever before 
                    t = Actor(target = test_run)
                    encoding_to_actor[program_encoding] = t
                    t.start()
                    t.send(("drawing_queue",drawing_queue)) ## First messsage
                    t.send(("new_shape",("type", "rectangle"),("coordinates", current_coords)))
                # Case two we have seen this before and the thread is running.
                else:
                    t = encoding_to_actor.get(program_encoding)
                    t.send(("update_shape",("id", id), ("coordinates", current_coords)))
            else: # No associated program
                print(f"There is no associated program with the encoding: {program_encoding}")


def handle_raw_ids(ids,coords,drawing_queue):
    if ids is not None:
        program_encoding = int("".join(map(str, ids)),4)
        if program_encoding == 192 or program_encoding == 48 or program_encoding == 12:
            program_encoding = 3
        logger.log(level = 16, msg = f"Raw id: {ids} to interpreted id: {program_encoding}")
        handle_currently_recognized(program_encoding,coords,drawing_queue)
        return program_encoding
    else:
        return None

def webcamManyCaptures(base,buffer_size = 35):
    logger.log(level = 1, msg = "Started WebcamManyCaptures without a hitch")
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    # v = StringVar(value= "FOR NOW") 
    # text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White"
    canvas.pack()
    logger.log(level = 1, msg = "Created and packed Canvas")
    drawing_queue = Queue()

    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    papers_and_ids = paper_frame_based(frame)
    for paper, id, in papers_and_ids:
        program_encoding = handle_raw_ids(id, paper, drawing_queue)
        logger.log(level = 20, msg = f"First program encoding found is {program_encoding}")
    # v = StringVar(value= str(program_encoding)) 
    
    def update(cam):
        logger.log(level = 19, msg = f"Called the Update Function")
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)## we do not want to be rid of the drawing actor unless q is pressed
        for coords, ids in paper_frame_based(frame):
        ## whatever it "sees" is "in the scene" by this point. whatever it doesn't "see" should be killed off.
        # for coords, ids in frames_frame_based(frame): ## needs to return a list of tuples
            program_encoding = handle_raw_ids(ids, coords, drawing_queue)
            # print(program_encoding)
            logger.log(level = 18, msg = f"Saw program encoding, {program_encoding}")

   
                ## using discard so it doesn't throw an error when pre_existing_encodings doesn't have it
                ## use remove to throw an error when the set of pre_existing_encordings doesn't have it.
        #     # canvas.coords(box, frame_to_polygon_list(avg_box)) ## outline of paper
        # for encoding in (pre_existing_encodings):
        #     actor = encoding_to_actor.get(encoding)
        #     assert False
        #     actor.end()
        #     encoding_to_actor.pop(encoding)
        # print('got to draw loop')
        draw_loop(drawing_queue=drawing_queue, canvas= canvas)
        if cv.waitKey(1) == ord('q'): ## stopping condition
            logger.log(level = 17, msg = f"In the stopping condition")
            for encoding,a in encoding_to_actor.items():
                a.end()
                logger.log(level = 16, msg = f"encoding asscoiated is : {encoding}")
                logger.log(level = 16, msg = "Got past the end, onto Join now")
                a.join()
            logger.log(level = 17, msg = f"finished the joining and ending")
            base.quit()
        base.after(200, update, cam)  # Timed Check, adding itself back onto the queue to run 20ms later
        
    base.after(20, update, cam)
    logger.log(level = 20, msg = f"Pre mainloop start")
    base.mainloop()
    logger.log(level = 20, msg = f"Post mainloop start")
    
    cam.release()
    cv.destroyAllWindows()



parser = ArgumentParser()
parser.add_argument('--logging',action='store_true')   
parser.add_argument('--llevel', type = int)   
args = parser.parse_args()
print(args)
if (args.logging):
    log_level = args.llevel
    logging.basicConfig(level=log_level)
    ## higher logging levels don't include lower logging levels
    ## Lower logging levels include all higher logging levels
    logger.log(level = log_level, msg= f"Logging working at level {log_level}")
webcamManyCaptures(base= base)