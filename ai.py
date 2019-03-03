import os
import numpy as np
import random
import re

from keras.models import Sequential
from keras.layers import *

import chess
from game import Player

weightFile = 'weight.h5'

def buildModel():
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

    if os.path.isfile(weightFile):
        print("Loading weight from", weightFile)
        model.load_weights(weightFile)

    return model

def saveModel(model):
    print("Saving weight")
    model.save(weightFile)

class AIPlayer(Player):
    def __init__(self, color, model, exploreRate = 0.2, gamma = 0.9999):
        self.color = color
        self.model = model 
        self.exploreRate = exploreRate
        self.gamma = gamma

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
            print("Getting ", self.lastMove, maxQ[0][0])

        return self.lastMove

    def reward(self, board, reward):
        if not self.lastMove or not self.lastBoardArray: return

        boardArray, legalMoves = board.toArrays()

        if len(legalMoves) > 0:
            # factor in future rewards
            reward = (1-self.gamma) * reward + self.gamma * max([self.model.predict(self.getNNInput(boardArray, self.uciToN(a)))[0][0] for a in legalMoves])

        print("Learning", self.lastMove, reward)
        self.model.fit(self.getNNInput(self.lastBoardArray, self.uciToN(self.lastMove)), [reward], verbose = 0)
