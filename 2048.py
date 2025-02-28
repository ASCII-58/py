import tkinter as tk
import random

class counter:
    def __init__(self):
        self.fraction=0

    def ShowScore(self):
        return self.fraction
    def AddScore(self,score):
        self.fraction+=score
class player:
    def __init__(self):
        self.Chessboard2048=[[0 for i in range(4)] for j in range(4)]
        self.count2048=counter()
    def ShowChessboard(self):
        return self.Chessboard2048
    def GenerateRandomNumber(self):
        Board=[]
        for i in range(4):
            for j in range(4):
                if self.Chessboard2048[i][j]==0:
                    Board.append((i,j))
        a=random.choice(Board)
        self.Chessboard2048[a[0]][a[1]]=random.choice([2,4])
    def RowMove(self,a:bool):# a=True:left a=False:right
        NewChessboard=[[],[],[],[]]
        for i in range(4):
            for j in range(4):
                if self.Chessboard2048[i][j]!=0:
                    NewChessboard[i].append(self.Chessboard2048[i][j])
        if a:
            for i in range(4):
                while len(NewChessboard[i])<4:
                    NewChessboard[i].append(0)
            else:
                for i in range(4):
                    while len(NewChessboard[i])<4:
                        NewChessboard[i].insert(0,0)
        self.Chessboard2048=NewChessboard
    def ColumnMove(self,a:bool):# a=True:up a=False:down
        NewChessboard=[[],[],[],[]]
        for i in range(4):
            for j in range(4):
                if self.Chessboard2048[j][i]!=0:
                    NewChessboard[i].append(self.Chessboard2048[j][i])
        if a:
            for i in range(4):
                while len(NewChessboard[i])<4:
                    NewChessboard[i].append(0)
            else:
                for i in range(4):
                    while len(NewChessboard[i])<4:
                        NewChessboard[i].insert(0,0)
        for i in range(4):
            for j in range(4):
                self.Chessboard2048[i][j]=NewChessboard[j][i]
    