import numpy as np
import random
import re

from keras.models import Sequential
from keras.layers import *

import chess
from game import Player

def compileNN():
    model = Sequential()

    for i in range(3):
        model.add(Conv2D(filters = 32, kernel_size = 3, strides = 1, padding = "same", input_shape = (3, 8, 8)))
        model.add(BatchNormalization(axis = 1))
        model.add(Activation('relu'))

    model.add(Flatten())

    model.add(Dense(256, activation = 'relu'))
    model.add(Dense(1, activation = 'relu'))

    model.compile(optimizer = 'adam', loss = 'mse')
    model.summary()

    return model

class AIPlayer(Player):
    def __init__(self, color, model, exploreRate = 0.2):
        self.color = color
        self.model = model 
        self.exploreRate = exploreRate

        self.lastBoardArray = None
        self.lastMove = None

    def getNNInput(self, boardArray, action):
        board2d = np.reshape(boardArray, (8, 8))
        # TODO normalize this
        from2d = np.zeros((8, 8))
        from2d[action[0]//8][action[0]%8] = 1
        to2d = np.zeros((8, 8))
        to2d[action[1]//8][action[1]%8] = 1
        
        return np.reshape([board2d, from2d, to2d], (1, 3, 8, 8))

    def uciToN(self, uci):
        return (chess.SQUARE_NAMES.index(uci[:2]), chess.SQUARE_NAMES.index(uci[2:4]))

    def move(self, board):
        boardArray, legalMoves = board.toArrays()

        # Only do queen promotion if there's one
        onlyQueen = re.compile('.*[0-9q]$')
        legalMoves = [m for m in legalMoves if onlyQueen.match(m)]

        self.lastBoardArray = boardArray

        # explore random moves
        if random.random() < self.exploreRate:
            self.lastMove = random.choice(legalMoves)
        else:
            qs = [self.model.predict(self.getNNInput(boardArray, self.uciToN(a))) for a in legalMoves]
            maxQ = max(qs)
            self.lastMove = random.choice([legalMoves[i] for i in range(len(legalMoves)) if qs[i] == maxQ])

        return self.lastMove

    def reward(self, board, reward):
        if not self.lastMove or not self.lastBoardArray: return

        boardArray, legalMoves = board.toArrays()
        futureQ = max([self.model.predict(self.getNNInput(boardArray, self.uciToN(a))) for a in legalMoves])
        self.model.fit(self.getNNInput(self.lastBoardArray, self.uciToN(self.lastMove)), futureQ, verbose = 0)
