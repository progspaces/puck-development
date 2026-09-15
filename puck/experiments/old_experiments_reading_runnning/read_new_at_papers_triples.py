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


DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)

def area_of_frame(frame):
    x0 = frame[0][0]
    x1 = frame[1][0]
    y0 = frame[0][1]
    y1 = frame[1][1]
    return abs(y0-y1)* abs(x0-x1)

def bigger_smaller_frame(frame_0, frame_1):
 if area_of_frame(frame_0)> area_of_frame(frame_1):
    return (frame_0, frame_1)
 else:
    return (frame_1, frame_0)

def frame_to_polygon_list(frame):
    x0 = int(frame[0][0])
    x1 = int(frame[1][0])
    x2 = int(frame[2][0])
    y0 = int(frame[0][1])
    y1 = int(frame[1][1])
    y2 = int(frame[2][1])
    mid_x = (x0+ x2)/2
    mid_y=  (y0+ y2)/2
    return [(x0,y0),(x1,y1), (x2,y2),(int(2*mid_x-x1),int(2*mid_y-y1)) ]


def frames_path_based(path):
    input = cv.imread(path)
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    ## grab the first three ids and their coordinates, that's all we're considering rn
    corners_a = corners[0][0]
    corners_b = corners[1][0]
    corners_c = corners[2][0]
    print(corners_a)
    print(corners_b)
    print(corners_c)
    # frame_0 = (corners_a[1], corners_b[3])
    # frame_1 = (corners_a[3], corners_b[1])
    # outer_frame, inner_frame = (bigger_smaller_frame(frame_0, frame_1))
    # return (outer_frame, inner_frame, ids)

# # outer_frame, inner_frame, ids= frames_path_based("puck/apriltag_stills/test_0.png")
# outer_polygon = frame_to_polygon_list(outer_frame)
# inner_polygon = frame_to_polygon_list(inner_frame)
def average_pt(corners):
    sum_x = 0
    sum_y = 0 
    for pair in corners:
        sum_x += pair[0]
        sum_y += pair[1]
    return (int(sum_x/4), int(sum_y/4))

def frames_frame_based(frame):
    input = frame
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    ## grab the first two ids and their coordinates, that's all we're considering rn
    if ids is not None and len(ids)>=3:
        print(ids)
        corners_a = corners[0][0]
        corners_b = corners[1][0]
        corners_c = corners[2][0]
        print(average_pt(corners_c))
        average_frame = [average_pt(corners_a),average_pt(corners_b),average_pt(corners_c)]
        return (average_frame, ids)
    else:
        return (0,0)


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


def webcamManyCaptures(base,buffer_size = 35):
    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    avg_frame, ids = (frames_frame_based(frame))
    v = StringVar(value= "Warming up") 
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()
    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0), outline='blue',fill="white", width=2)

    def update(cam, canvas, box):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        avg_frame, ids = (frames_frame_based(frame))
        if avg_frame != 0:
            canvas.coords(box, frame_to_polygon_list(avg_frame))
        if cv.waitKey(1) == ord('q'): ## stopping condition
            base.quit()
        base.after(10, update, cam, canvas, box)  # Timed Check, adding itself back onto the queue to run 20ms later
        
    base.after(20,update, cam, canvas, box)
    base.mainloop()
    cam.release()
    cv.destroyAllWindows()

webcamManyCaptures(base= base)