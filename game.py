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
        self.captured = None

    def _push_capture(self, move, capture_square, piece_type, was_promoted):
        self.captured = piece_type

    def run(self):
        if self.turn:
            p1, p2 = self.players
        else:
            p1, p2 = self.players[::-1]

        move = Move(*p1.move(self))

        if move not in self.legal_moves:
            # Ignore invalid moves
            return True

        self.captured = None
        self.push(move)
        captured = self.captured # can_claim_draw() changes self.captured, so need to make a local copy

        if captured:
            reward = 0.15 * 1.3 ** captured
            p1.reward(self, reward)
            p2.reward(self, -reward)
        else:
            p2.reward(self, 0)

        # check/stale mate or draw
        if not any(self.generate_legal_moves()):
            p1.reward(self, 1)
            p2.reward(self, -1)
            self.gameEnd()
            return False

        if self.can_claim_draw():
            self.gameEnd()
            return False

        return True

    def gameEnd(self):
        for p in self.players:
            p.gameEnd()

    def toArrays(self):
        builder = []
        for square in SQUARES:
            piece = self.piece_at(square)
            if piece:
                builder.append(piece.piece_type + (6 if piece.color == BLACK else 0))
            else:
                builder.append(0)
            moves = [(m.from_square, m.to_square, m.promotion) for m in self.legal_moves]
        return (builder, moves)

class Player:
    def move(self, board):
        pass
    def reward(self, board, reward):
        pass
    def gameEnd(self):
        pass


class HumanPlayer(Player):
    def __init__(self, color):
        self.color = color
        self.selected = None
        self.legalMoves = None
        self.order = None

    def moveOrder(self, board, n):
        if self.order: return

        def select(n):
            piece = board.piece_at(n)
            if piece and piece.color == self.color:
                self.selected = n

        if self.selected is not None:
            promotion = None
            if board.piece_at(self.selected).piece_type == PAWN and n // 8 == self.color * 7: # black = 0, white = 7
                promotion = QUEEN
            order = (self.selected, n, promotion)
            if order in self.legalMoves:
                self.order = order
                self.selected = None
            else:
                select(n)
        else:
            select(n)

    def move(self, board):
        _, self.legalMoves = board.toArrays()
        move = self.order
        self.order = None
        return move or (0, 0)

    def reward(self, board, reward):
        print("Human reward", reward)
