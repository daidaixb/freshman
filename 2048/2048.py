#_*_ coding:utf-8 _*_

import curses
from random import randrange, choice
from collections import defaultdict

letter_codes = [ord(ch) for ch in 'WSADRQwsadrq']
actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'RESTART', 'EXIT']
actions_dict = dict(zip(letter_codes, actions * 2))
# zip: return a list of tuple  #

def get_user_action(keyboard):
	char = 'N'
	while char not in actions_dict:
		char = keyboard.getch()
	return actions_dict[char]

def transpose(field):
	return [list(row) for row in zip(*field)]

def inver(field):
	return [row[::-1] for row in field]

class GameField(object):
	def __init__(self, height=4, width=4, win=2048):
		self.height = height
		self.width = width
		self.win_value = win
		self.score = 0
		self.highscore = 0
		self.reset()

	def reset(self):
		if self.score > self.highscore:
			self.highscore = self.score
		self.score = 0
		# self.field = [[0 for i in range(self.width)] for j in range(self.height)]
		self.field = [[0] * self.width] * self.height
		self.spawn()
		self.spawn()

	def move(self, direction):
		def move_row_left(row):
			def tighten(row):
				new_row = [i for i in row if i != 0]
				new_row += []