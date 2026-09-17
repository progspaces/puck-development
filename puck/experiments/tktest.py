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

import logging
from queue import Queue
import logging
import cv2 as cv
from actor import Actor

logger = logging.getLogger(__name__)



points = [(100, 100), (150, 100), (150, 150)]
outline = "blue"
fill = "white"
width = 2

def run(self:Actor):
    print("Actor is running")

def spawn_first_actor():
    t = Actor(target = run)
    t.start()
    return t

def main():
    cheight, cwidth = 1080,1920
    canvas = Canvas(base, height= cheight, width = cwidth, background='black')
    # v = StringVar(value= "FOR NOW") 
    # text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White"
    canvas.pack()
    logger.log(level = 1, msg = "Created and packed Canvas")
    
    drawing_queue = Queue()
    actor = spawn_first_actor()

    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    def draw_loop(cam, i):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        polygon_id = canvas.create_polygon(points, fill=fill, outline=outline, width=width)
        canvas.pack()
        if cv.waitKey(1) == ord('q'): ## stopping condition
            actor.end()
            actor.join()
            base.quit()
        else:
            i = i + 1
            print(i)
        #     print("hm")
        base.after(16, draw_loop, cam, i)


    # start the main loop
    i = 0
    base.after(20, draw_loop, cam, i)
    base.mainloop()


if __name__ == "__main__":
    main()
