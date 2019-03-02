#!/usr/bin/env python

from threading import Thread

from window import Window
from game import *
import chess

def main():

    players = [
        HumanPlayer(chess.BLACK),
        HumanPlayer(chess.WHITE)
    ]
    game = Game(*players)

    running = True
    def gameLoop():
        while running:
            game.run()
            game.reset()

    def onBtn(n):
        p = players[game.turn]
        if isinstance(p, HumanPlayer):
            p.moveOrder(game, n)

    win = Window(onButton = onBtn)
    thread = Thread(target = gameLoop)
    thread.start()

    win.loop(cb = lambda: win.update(game.toArray()))
    running = False

    for p in players:
        if isinstance(p, HumanPlayer):
            p.stop()

if __name__ == "__main__":
    main()
