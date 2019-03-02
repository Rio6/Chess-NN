#!/usr/bin/env python

import chess
from window import Window
from game import Game, HumanPlayer
from ai import AIPlayer, compileNN

def main():

    model = compileNN()

    players = [
        #HumanPlayer(chess.BLACK),
        AIPlayer(color = chess.BLACK, model = model),
        HumanPlayer(chess.WHITE),
    ]
    game = Game(*players)

    def onBtn(n):
        p = players[game.turn]
        if isinstance(p, HumanPlayer):
            p.moveOrder(game, n)

    def updateGame():
        running = game.run()
        win.update(game.toArrays()[0])

        if not running:
            game.reset()

    win = Window(onButton = onBtn)
    win.loop(cb = updateGame)

if __name__ == "__main__":
    main()
