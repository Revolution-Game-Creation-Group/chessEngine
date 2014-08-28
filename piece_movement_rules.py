from utils import is_valid_square
from utils import index_to_sq
from utils import sq_to_index
from utils import opposite_color
from board import Board

def valid_and_empty(row, col, board):
	return is_valid_square(row, col) and board.is_empty(row, col)

def empty_or_capture(row, col, board, piece):
	return is_valid_square(row, col) and (
		board.is_empty(row, col) or is_capture(row, col, board, piece))

def is_capture(row, col, board, piece):
	return board.get_color(row, col) is not None and board.get_color(row, col) != piece[0]

def valid_capture(row, col, board, piece):
	return is_valid_square(row, col) and is_capture(row, col, board, piece)

def slide_and_check(board, row, col, piece, d_row, d_col, squares):
	"""Extend squares array with valid squares.
	TODO, in the future, write this to be easily parallelisable"""
	while True:
		row += d_row
		col += d_col

		if not is_valid_square(row, col):
			break
		if board.is_empty(row, col):
			squares.append((row, col))
		else:
			if piece[0] != board.get_color(row, col):
				squares.append((row, col))
			break

	return

def get_rook_valid_squares(board, row, col, piece):
	squares = []
	slide_and_check(board, row, col, piece, 0, 1, squares)
	slide_and_check(board, row, col, piece, 0, -1, squares)
	slide_and_check(board, row, col, piece, 1, 0, squares)
	slide_and_check(board, row, col, piece, -1, 0, squares)
	return [index_to_sq(sq[0], sq[1]) for sq in squares]

def get_bishop_valid_squares(board, row, col, piece):
	squares = []
	slide_and_check(board, row, col, piece, 1, 1, squares)
	slide_and_check(board, row, col, piece, 1, -1, squares)
	slide_and_check(board, row, col, piece, -1, 1, squares)
	slide_and_check(board, row, col, piece, -1, -1, squares)
	return [index_to_sq(sq[0], sq[1]) for sq in squares]

def get_queen_valid_squares(board, row, col, piece):
	squares = []
	squares.extend(get_rook_valid_squares(board, row, col, piece))
	squares.extend(get_bishop_valid_squares(board, row, col, piece))
	return squares

def get_king_valid_squares(board, row, col, piece):
	"""This is easily parallelisable."""

	squares = [
		(row + 1, col),
		(row - 1, col),
		(row + 1, col + 1),
		(row - 1, col + 1),
		(row + 1, col - 1),
		(row - 1, col - 1),
		(row, col + 1),
		(row, col - 1)
	]

	# TODO, this does not check whether capture is possible by the king
	# this will be implemented later
	return [
		index_to_sq(sq[0], sq[1]) for sq in squares
		if empty_or_capture(sq[0], sq[1], board, piece)
	]

def get_pawn_valid_squares(board, row, col, piece):
	d_row = (-1 if piece[0] == "W" else 1)

	l1 = [(row + d_row, col)]
	if (row == 1 and piece[0] == "B") or (row == 6 and piece[0] == "W"):
		l1.append((row + 2 * d_row, col))

	# should be empty
	squares = filter(lambda sq: valid_and_empty(sq[0], sq[1], board), l1)
	l2 = [(row + d_row, col + 1), (row + d_row, col - 1)]
	# should be capture
	squares.extend(
		filter(lambda sq: valid_capture(sq[0], sq[1], board, piece), l2)
	)
	return [index_to_sq(sq[0], sq[1]) for sq in squares]

def get_knight_valid_squares(board, row, col, piece):
	squares = [
		(row + 1, col + 2),
		(row + 1, col - 2),
		(row - 1, col + 2),
		(row - 1, col - 2),
		(row + 2, col + 1),
		(row + 2, col - 1),
		(row - 2, col + 1),
		(row - 2, col - 1),
	]
	
	return [index_to_sq(sq[0], sq[1]) for sq in squares
		if empty_or_capture(sq[0], sq[1], board, piece)
	]

def get_piece_valid_squares(board, sq):
	row, col = sq_to_index(sq)
	piece = board._board[row][col]

	return {
		"N": get_knight_valid_squares,
		"R": get_rook_valid_squares,
		"Q": get_queen_valid_squares,
		"K": get_king_valid_squares,
		"P": get_pawn_valid_squares,
		"B": get_bishop_valid_squares
	}[piece[1]](board, row, col, piece)

def is_legal_move(board, src, dest):
	"""src and dest are squares, not indices.
	No turn checking."""
	piece = board.get_piece(src)
	if piece == Board.EMPTY:
		raise ValueError("There is no piece at square %s" % src)
	color = piece[0]

	if dest not in get_piece_valid_squares(board, src):
		return False

	# apply the move
	board.move_piece(src, dest)
	has_check = is_in_check(board, color)
	# undo the move
	board.move_piece(dest, src)
	return not has_check

def is_in_check(board, color):
	attacked_squares = set([])
	opp_color = opposite_color(color)
	# get everything for that color
	for piece, coord_list in board._piece_map[opp_color].items():

		for (row, col) in coord_list:
			attacked_squares.update(
				get_piece_valid_squares(board, index_to_sq(row, col))
			)

	return board._piece_map[color][color + "K"][0] in attacked_squares
