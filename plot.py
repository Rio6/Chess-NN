import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
from datetime import datetime

xList = []
yList = []
figure = None
plot = None
canvas = None

def makePlotWindow(upper):
    global figure
    global plot
    global canvas

    root = Tk.Toplevel(upper)
    root.wm_title("loss")
    root.attributes('-type', 'dialog')

    figure = Figure(figsize=(5, 4), dpi=100)
    plot = figure.add_subplot(111)

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    return (xList, yList)

def update(x):
    xList.append(x)
    yList.append(datetime.now())
    plot.plot_date(yList, xList, 'b-')
    canvas.draw()
