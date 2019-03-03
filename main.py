#!/usr/bin/env python

import sys
import chess

from window import Window
from game import Game, HumanPlayer
from ai import AIPlayer, buildModel, saveModel

SAVE_INTERVAL = 5

def main():

    model = buildModel()

    if 'play' in sys.argv:
        players = [
            AIPlayer(color = chess.BLACK, model = model),
            HumanPlayer(chess.WHITE)
        ]
    elif 'debug' in sys.argv:
        players = [
            HumanPlayer(chess.BLACK),
            HumanPlayer(chess.WHITE)
        ]
    elif 'train' in sys.argv or 'watch' in sys.argv:
        players = [
            AIPlayer(color = chess.BLACK, model = model),
            AIPlayer(color = chess.WHITE, model = model),
        ]
    else:
        print("No command")
        quit(1)

    game = Game(*players)

    def onBtn(n):
        p = players[game.turn]
        if isinstance(p, HumanPlayer):
            p.moveOrder(game, n)

    def updateGame():
        running = game.run()
        if not running:
            print("Game ended", game.result(claim_draw = True))
            game.reset()
            updateGame.count += 1

        if win: win.update(game.toArrays()[0])

        if updateGame.count >= SAVE_INTERVAL:
            saveModel(model)
            updateGame.count = 0
    updateGame.count = 0

    win = None
    try:
        if 'train' in sys.argv:
            while(True):
                updateGame()
        else:
            win = Window(onButton = onBtn)
            win.loop(cb = updateGame)
    except KeyboardInterrupt:
        pass
    finally:
        saveModel(model)

if __name__ == "__main__":
    main()
