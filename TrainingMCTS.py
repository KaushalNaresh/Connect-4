import numpy as np
import pandas as pd
import random
import pygame
import sys
import math
from math import sqrt
import datetime
from copy import copy, deepcopy
import csv

BLUE = (0,255,0)
BLACK = (128,128,128)
RED = (255,0,0)
YELLOW = (0,0,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def convert2string(board):
	s = ""
	t = []
	for x in board:
		for y in x:
			if y == 0:
				t.append('z')
			if y == 1:
				t.append('1')
			if y == 2:
				t.append('2')
	return "".join(map(str, t))

def write_to_plays_csv(plays):
	with open('plays.csv', 'w') as f:
		for key in plays.keys():
			f.write("%d,%s,%d\n"%(key[0], convert2string(key[1]), plays[key]))

def write_to_wins_csv(wins):
	with open('wins.csv', 'w') as f:
		for key in wins.keys():
			f.write("%d,%s,%d\n"%(key[0], convert2string(key[1]), wins[key]))

def read_from_plays_csv(plays):
	try:
		with open('plays.csv', 'r') as infile:
			reader = csv.reader(infile)
			for r in reader:
				p = int(r[0])
				str_board = r[1]
				key_board = convert2array(str_board)
				val = int(r[2])
				plays[(p, to_tuple(key_board))] = val
		
		
	except FileNotFoundError:
		return

def read_from_wins_csv(wins):
	try:
		with open('wins.csv', 'r') as infile:
			reader = csv.reader(infile)
			for r in reader:
				p = int(r[0])
				str_board = r[1]
				key_board = convert2array(str_board)
				val = int(r[2])
				wins[(p, to_tuple(key_board))] = val
		
	except FileNotFoundError:
		return

def convert2array(str_board):
	board_for_us = create_board()
	i = 0
	for char in str_board:
		if char == 'z':
			board_for_us[int(i / COLUMN_COUNT)][int(i % COLUMN_COUNT)] = 0
		elif char == '1':
			board_for_us[int(i / COLUMN_COUNT)][int(i % COLUMN_COUNT)] = 1
		elif char == '2':
			board_for_us[int(i / COLUMN_COUNT)][int(i % COLUMN_COUNT)] = 2
			
		i += 1
	return board_for_us


def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT), dtype = int)
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def turn(board):
	num_1 = 0
	num_2 = 0
	for i in range(0, 6):
		for j in range(0, 7):
			if(board[i][j] == 1):
				num_1 += 1
			elif board[i][j] == 2:
				num_2 += 1
	if num_1 > num_2:
		player = 2
	else:
		player = 1
	return player

def next_state_possible(board, col):
	row = get_next_open_row(board, col)
	player = turn(board)
	board_copy = deepcopy(board)
	drop_piece(board_copy, row, col, player)
	return board_copy

def next_state(board, col):
	row = get_next_open_row(board, col)
	player = turn(board)
	drop_piece(board, row, col, player)
	return board

def who_won(state, turn):
	if winning_move(state, turn):
		return turn
	return 0

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def to_tuple(arr):
	return tuple(map(tuple, arr))

def to_arr(tup):
	return [list(item) for item in tup]

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax_pruned(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 100000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, AI_PIECE))
	if maximizingPlayer:
		value = -100000000000000
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax_pruned(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = 10000000000000
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax_pruned(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000 
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

class MonteCarlo():
	def __init__(self, board, **kwargs):
		self.board = deepcopy(board)
		self.states = [deepcopy(board)]
		self.seconds = kwargs.get('time', 5)
		self.calculation_time = datetime.timedelta(seconds=seconds)
		self.max_moves = kwargs.get('max_moves', 100)
		self.wins = {}
		self.plays = {}
		self.c = kwargs.get('C', 1.4)
		self.history = []

	def update(self, state):
		self.states.append(deepcopy(state))
		self.board = deepcopy(state)
	
	def get_play(self):
		self.max_depth = 0
		state = deepcopy(self.states[-1])
		player = turn(self.states[-1])
		legal = get_valid_locations(self.states[-1])
		if not legal:
			return
		if len(legal) == 1:
			return legal[0]
		games = 0

		begin = datetime.datetime.utcnow()
		while datetime.datetime.utcnow() - begin < self.calculation_time:
			self.run_simulation()
			self.states.append(self.board)
			games += 1

		moves_states = [(p, to_tuple(next_state_possible(state, p))) for p in legal]
		print(games)
		print(datetime.datetime.utcnow() - begin)
		percent_wins, move = max((self.wins.get((player, s), 0) / self.plays.get((player, s), 1), p) for p, s in moves_states)
		for x in sorted(((100*self.wins.get((player, s), 0) / self.plays.get((player, s), 1), self.wins.get((player, s), 0), self.plays.get((player, s), 0), p)for p, s in moves_states), reverse = True):
			print("{3}: {0:.2f}% ({1} / {2})".format(*x))

		print("maximum depth searched:", self.max_depth)

		return move



	def run_simulation(self):
		visited_states = set()
		#states_copy = self.states
		plays = self.plays
		wins = self.wins
		states_copy = deepcopy(self.states)
		state = self.states[-1]
		player = turn(state)
		winning_player = 0
		expand = True
		# c = 0
		for t in range(1, self.max_moves+1):
			legal = get_valid_locations(states_copy[-1])
			if not legal:
				break
			state = states_copy[-1]
			player = turn(state)
			moves_states = [(p, to_tuple(next_state_possible(state, p))) for p in legal]
			for p in legal:
				if all(plays.get((player, s)) for p, s in moves_states):
					req_sum = sum(plays[(player, s)] for p, s in moves_states)
					if req_sum:
						log_total = math.log(req_sum)
					else:
						log_total = 0
					value, move, state = max(((wins[(player, s)] / plays[(player, s)]) + self.c * sqrt(log_total / plays[(player, s)]), p, to_arr(s)) for p, s in moves_states)
					
				else:
					move, temp = random.choice(moves_states)
					state = deepcopy(to_arr(temp))
				states_copy.append(state)
				temp = to_tuple(state)
				if expand and (player, temp) not in plays:
					expand = False
					plays[(player, temp)] = 0
					wins[(player, temp)] = 0
					if t > self.max_depth:
						self.max_depth = t
				visited_states.add((player, to_tuple(state)))
				winner = who_won(state, player)
				if winner:
					winning_player = player
					break

				#print(pd.DataFrame(self.states[-1]))
				#print(pd.DataFrame())
				# c += 1
				# if c == 2:
				# 	sys.exit()
			for player, state_tup in visited_states:
				if (player, state_tup) not in self.plays:
					continue
				self.plays[(player, state_tup)] += 1
				if player == winning_player:
					self.wins[(player, state_tup)] += 1


BLUE = (0,255,0)
BLACK = (128,128,128)
RED = (255,0,0)
YELLOW = (0,0,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

m_board = create_board()
print_board(m_board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(m_board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

whosturn = random.randint(PLAYER, AI)

temp_board = copy(m_board)

myAi = MonteCarlo(temp_board)
myAi.update(temp_board)

#convert2string(temp_board)
read_from_plays_csv(myAi.plays)
read_from_wins_csv(myAi.wins)


while not game_over:
	if whosturn == PLAYER and not game_over:				

		#col = random.randint(0, COLUMN_COUNT-1)
		#col = pick_best_move(board, AI_PIECE)
		col, minimax_score = minimax_pruned(m_board, 5, -10000000000000, 10000000000000, True)
		# col = myAi.get_play()
		# myAi.calculation_time = datetime.timedelta(seconds = 5)
		if is_valid_location(m_board, col):
			#pygame.time.wait(500)
			row = get_next_open_row(m_board, col)
			drop_piece(m_board, row, col, PLAYER_PIECE)
			myAi.history.append((PLAYER_PIECE, deepcopy(m_board)))
			myAi.update(m_board)

			if winning_move(m_board, PLAYER_PIECE):
				label = myfont.render("Player 1 wins!!", 1, RED)
				screen.blit(label, (40,10))
				game_over = True

			draw_board(m_board)

			whosturn += 1
			whosturn = whosturn % 2
####################################################################
	# for event in pygame.event.get():
	# 	if event.type == pygame.QUIT:
	# 		sys.exit()

	# 	if event.type == pygame.MOUSEMOTION:
	# 		pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
	# 		posx = event.pos[0]
	# 		if whosturn == PLAYER:
	# 			pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

	# 	pygame.display.update()

	# 	if event.type == pygame.MOUSEBUTTONDOWN:
	# 		pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
	# 		#print(event.pos)
	# 		# Ask for Player 1 Input
	# 		if whosturn == PLAYER:
	# 			posx = event.pos[0]
	# 			col = int(math.floor(posx/SQUARESIZE))

	# 			if is_valid_location(m_board, col):
	# 				row = get_next_open_row(m_board, col)
	# 				drop_piece(m_board, row, col, PLAYER_PIECE)
	# 				myAi.update(m_board)

	# 				if winning_move(m_board, PLAYER_PIECE):
	# 					label = myfont.render("Player 1 wins!!", 1, RED)
	# 					screen.blit(label, (40,10))
	# 					game_over = True

	# 				whosturn += 1
	# 				whosturn = whosturn % 2

	# 				print_board(m_board)
	# 				draw_board(m_board)

###################################################################################
	# # Ask for Player 2 Input
	if whosturn == AI and not game_over:				

		#col = random.randint(0, COLUMN_COUNT-1)
		#col = pick_best_move(board, AI_PIECE)
		#col, minimax_score = minimax_pruned(board, 5, -10000000000000, 10000000000000, True)
		col = myAi.get_play()
		myAi.calculation_time = datetime.timedelta(seconds = 5)
		if is_valid_location(m_board, col):
			#pygame.time.wait(500)
			row = get_next_open_row(m_board, col)
			drop_piece(m_board, row, col, AI_PIECE)
			myAi.history.append((AI_PIECE, deepcopy(m_board)))
			myAi.update(m_board)

			if winning_move(m_board, AI_PIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			draw_board(m_board)

			whosturn += 1
			whosturn = whosturn % 2

	if game_over:

		write_to_plays_csv(myAi.plays)
		write_to_wins_csv(myAi.wins)
		#for p, state in myAi.history:
			#decrement 1 from wins[(p, ())]
		pygame.time.wait(3000)
