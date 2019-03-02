from threading import Condition
from chess import *

class AttrDict(dict):
    """ Syntax candy https://stackoverflow.com/a/12639689/6023997 """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, **args):
        self.__dict__ = {**self.__dict__, **args}

class Game(Board):
    def __init__(self, p1, p2):
        super().__init__()

        self.players = [p2, p1] # black is False is 0

    def run(self):
        while True:
            if self.turn:
                p1, p2 = self.players
            else:
                p1, p2 = self.players[::-1]

            move = Move.from_uci(p1.move(self.toArray(), [m.uci() for m in self.legal_moves]))

            if move not in self.legal_moves:
                p1.reward(self.toArray, -99)
                break

            self.push(move)

            if not any(self.generate_legal_moves()):
                p1.reward(self.toArray(), 1)
                p2.reward(self.toArray(), -1)
                break

            if self.can_claim_draw():
                p1.reward(self.toArray(), .5)
                p2.reward(self.toArray(), .5)
                break

            p2.reward(self.toArray(), 0)

    def toArray(self):
        builder = []
        for square in SQUARES:
            piece = self.piece_at(square)
            if piece:
                builder.append(piece.piece_type + piece.color * 6)
            else:
                builder.append(0)
        return builder

class Player:
    def move(self, boardArray, legalMoves):
        pass
    def reward(self, boardArray, reward):
        pass


class HumanPlayer(Player):
    def __init__(self, color):
        self.cond = Condition()

        self.color = color
        self.selected = None
        self.legalMoves = None
        self.order = None
        self.lastAction = None

    # this function gets called from ui thread
    def moveOrder(self, board, n):
        self.cond.acquire()

        if self.order or not self.legalMoves: return

        def select(n):
            piece = board.piece_at(n)
            if piece and piece.color == self.color:
                self.selected = n

        if self.selected is not None:
            order = SQUARE_NAMES[self.selected] + SQUARE_NAMES[n]
            if order in self.legalMoves:
                self.order = order
                self.selected = None
                self.cond.notify()
            else:
                select(n)
        else:
            select(n)

        self.cond.release()

    def move(self, board, legalMoves):
        self.cond.acquire()

        self.legalMoves = legalMoves
        self.order = None
        self.cond.wait()
        self.lastAction = self.order

        self.cond.release()
        return self.lastAction or '0000'

    def reward(self, boardArray, reward):
        print("Human reward", reward)

    def stop(self):
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()
