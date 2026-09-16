import logging
import tkinter as tk

logger = logging.getLogger(__name__)

# setup the window and canvas
root = tk.Tk()


points = [(0, 0), (16, 0), (16, 16)]
outline = "blue"
fill = "white"
width = 2


def main():
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()

    def draw_loop():
        polygon_id = canvas.create_polygon(
            points, fill=fill, outline=outline, width=width
        )
        canvas.pack()

        # canvas.coords(polygon_id, *points)

        # once the queue is processed, schedule the next draw
        root.after(16, draw_loop)

    # start the main loop
    root.after(16, draw_loop)
    root.mainloop()


if __name__ == "__main__":
    main()
