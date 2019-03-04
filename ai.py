import os
import numpy as np
import random
import re
from collections import deque

from keras.models import Sequential
from keras.layers import *
from keras.optimizers import Adam

import chess
from game import Player

import plot

weightFile = 'weight.h5'

def buildModel():
    model = Sequential()

    model.add(Conv2D(filters = 32, kernel_size = 3, strides = 1, padding = "same", input_shape = (3, 8, 8)))
    model.add(BatchNormalization(axis = 1))
    model.add(Activation('relu'))

    model.add(Conv2D(filters = 64, kernel_size = 5, strides = 2, padding = "same", input_shape = (3, 8, 8)))
    model.add(BatchNormalization(axis = 1))
    model.add(Activation('relu'))

    model.add(Conv2D(filters = 128, kernel_size = 5, strides = 2, padding = "same", input_shape = (3, 8, 8)))
    model.add(BatchNormalization(axis = 1))
    model.add(Activation('relu'))

    model.add(Flatten())

    model.add(Dense(512, activation = 'relu'))
    model.add(Dense(256, activation = 'relu'))
    model.add(Dense(1, activation = 'relu'))

    adam = Adam(lr = 0.1e-5, decay = 0)
    model.compile(optimizer = adam, loss = 'mse')
    model.summary()

    if os.path.isfile(weightFile):
        print("Loading weight from", weightFile)
        model.load_weights(weightFile)

    return model

def saveModel(model):
    print("Saving weight")
    model.save(weightFile)

class AIPlayer(Player):
    def __init__(self, color, model, exploreRate = 0.2, gamma = 0.9):
        self.color = color
        self.model = model 
        self.exploreRate = exploreRate
        self.gamma = gamma

        self.lastBoardArray = None
        self.lastMove = None

        self.memory = deque(maxlen = 1024)
        self.batchSize = 64

    def getNNInput(self, boardArray, move):
        board2d = np.reshape(boardArray, (8, 8)).astype('float')
        if self.color == chess.BLACK:
            # reverse board color
            for i,j in np.ndindex(board2d.shape):
                if board2d[i][j] > 0:
                    board2d[i][j] = (board2d[i][j] + 6) % 12 or 12
            # rotate the board
            board2d = np.rot90(board2d, 2)
        board2d /= 13 # 12 pieces + empty
        from2d = np.zeros((8, 8))
        from2d[move[0]//8][move[0]%8] = 1
        to2d = np.zeros((8, 8))
        to2d[move[1]//8][move[1]%8] = 1

        return np.reshape([board2d, from2d, to2d], (1, 3, 8, 8))

    def move(self, board):
        boardArray, legalMoves = board.toArrays()

        # Only do queen promotion if there's one
        legalMoves = [m for m in legalMoves if m[2] is None or m[2] == chess.QUEEN]

        self.lastBoardArray = boardArray

        # explore random moves
        if random.random() < self.exploreRate:
            self.lastMove = random.choice(legalMoves)
        else:
            qs = [self.model.predict(self.getNNInput(boardArray, a)) for a in legalMoves]
            maxQ = max(qs)
            self.lastMove = random.choice([legalMoves[i] for i in range(len(legalMoves)) if qs[i] == maxQ])
            if maxQ[0][0] != 0: print("Getting", self.lastMove, maxQ[0][0])

        return self.lastMove

    def reward(self, board, reward):
        if not self.lastMove or not self.lastBoardArray: return

        boardArray, legalMoves = board.toArrays()

        if len(legalMoves) > 0:
            # factor in future rewards
            reward = (1-self.gamma) * reward + self.gamma * max([self.model.predict(self.getNNInput(boardArray, a))[0][0] for a in legalMoves])

        if reward > 0: # see if ignoring 0s would do something
            #print("Learn  ", self.lastMove, reward)
            self.memory.append((self.getNNInput(self.lastBoardArray, self.lastMove), [reward]))


    def gameEnd(self):
        if len(self.memory) < self.batchSize: return

        trainData = random.sample(self.memory, self.batchSize)
        loss = self.model.fit_generator((data for data in trainData), self.batchSize, verbose = 1).history['loss']
        plot.update(loss)
