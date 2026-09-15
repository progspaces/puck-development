import logging
import time
import tkinter as tk

from puck.actors import ActorID, me, receive, run_main, send, spawn

logger = logging.getLogger(__name__)

# setup the window and canvas
root = tk.Tk()
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()


def triangle_actor(main_id: ActorID):
    # polygon properties
    points = [(0, 0), (16, 0), (16, 16)]
    outline = "blue"
    fill = "white"
    width = 2

    # the position of the polygon
    SPEED = 0.01
    x, y = 0.0, 0.0

    # create the polygon and get it's id back
    polygon_id: int | None = None
    send(main_id, (me(), "create_polygon", points, fill, outline, width))
    match receive():
        case ("polygon_created", poly_id):
            polygon_id = poly_id
        case _:
            logger.error("Unexpected message.")

    # update the animation
    while True:
        # pause for a second
        time.sleep(0.01)

        # move the points
        points = [(p[0] + int(x), p[1] + int(y)) for p in points]

        # update state of the polygon
        send(main_id, ("update_polygon", polygon_id, points))

        # move the point about
        x += SPEED
        y += SPEED


def draw_loop():
    # loop until there is nothing in the drawing queue
    while True:
        match receive(block=False):
            case (sender_id, "create_polygon", points, fill, outline, width):
                polygon_id = canvas.create_polygon(
                    points, fill=fill, outline=outline, width=width
                )
                send(sender_id, ("polygon_created", polygon_id))
            case ("update_polygon", polygon_id, points):
                canvas.coords(polygon_id, *points)
            case None:
                break
            case _:
                print("Error: unknown message")

    # once the queue is processed, schedule the next draw
    root.after(16, draw_loop)


def main():
    # spawn the triangle actor
    spawn(triangle_actor, me())

    # start the main loop
    root.after(16, draw_loop)
    root.mainloop()


if __name__ == "__main__":
    # setup the main loop as an actor and run the main function on it
    run_main(main)
