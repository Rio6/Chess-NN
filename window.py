import tkinter as tk

pieces = [' ', '♙', '♘', '♗', '♖', '♕', '♔', '♟', '♞', '♝', '♜', '♛', '♚']

class Window:
    def __init__(self, onButton = None):
        self.finished = False

        self.root = tk.Tk()
        self.root.title("Chess")
        self.root.attributes('-type', 'dialog')

        frame = tk.Frame(self.root, background = 'gray20')
        frame.grid()

        self.btns = [None] * 8*8

        for x in range(8):
            for y in range(8):
                n = 8*8-1 - (x + y*8)
                btn = tk.Label(frame,
                        text = ' ', font = ('Mono', 50),
                        width = 2, height = 1,
                        foreground = 'black', background = 'white' if (n%2+n//8)%2 == 0 else 'gray40',
                        highlightbackground = 'black')
                btn.grid(column = x, row = y)
                btn.bind('<Button-1>', lambda e,_n=n: onButton(_n))
                self.btns[n] = btn

    def loop(self, cb = None):
        def cbLoop():
            cb()
            self.root.after(100, cbLoop)
        if cb:
            self.root.after(100, cbLoop)
        self.root.mainloop()
        self.finished = True

    def update(self, board):
        for n,p in enumerate(board):
            self.btns[n].config(text = pieces[p])

