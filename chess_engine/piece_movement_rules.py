import logging

from .utils import opposite_color

from .board import is_valid_square
from .board import is_empty_square
from .board import slide_index
from .board import get_color
from .board import sq_to_index
from .board import index_to_sq
from .board import index_to_row
from .board import get_piece_list
from .board import print_board
from .board import get_piece_color
from .board import get_raw_piece
from .board import is_capture

from .move import gen_successor

#logging.basicConfig(level=logging.DEBUG)


def valid_and_empty(board, index):
    return is_valid_square(index) and is_empty_square(board, index)


def empty_or_capture(board, index, piece):
    return is_valid_square(index) and (
        is_empty_square(board, index) or is_capture(board, index, piece))

def valid_capture(board, index, piece):
    return is_valid_square(index) and is_capture(board, index, piece)


def slide_and_check(board, index, piece, d_row, d_col, squares):
    """Extend squares array with valid squares.
    TODO, in the future, write this to be easily parallelisable"""
    while True:
        index = slide_index(index, d_col, d_row)

        if not is_valid_square(index):
            break
        if is_empty_square(board, index):
            squares.append(index)
        else:
            #logging.debug("square occupied by %s" % board[index])
            #logging.debug("attacking piece is %s" % piece)
            if get_piece_color(piece) != get_color(board, index):
                squares.append(index)
            return


def get_rook_valid_squares(board, index):
    piece = board[index]
    squares = []
    slide_and_check(board, index, piece, 0, 1, squares)
    slide_and_check(board, index, piece, 0, -1, squares)
    slide_and_check(board, index, piece, 1, 0, squares)
    slide_and_check(board, index, piece, -1, 0, squares)
    return squares


def get_bishop_valid_squares(board, index):
    piece = board[index]
    squares = []
    slide_and_check(board, index, piece, 1, 1, squares)
    slide_and_check(board, index, piece, 1, -1, squares)
    slide_and_check(board, index, piece, -1, 1, squares)
    slide_and_check(board, index, piece, -1, -1, squares)
    return squares


def get_queen_valid_squares(board, index):
    piece = board[index]
    squares = []
    squares.extend(get_rook_valid_squares(board, index))
    squares.extend(get_bishop_valid_squares(board, index))
    return squares


def get_king_valid_squares(board, index):
    """This is easily parallelisable."""
    piece = board[index]
    squares = [
        slide_index(index, 1, -1),
        slide_index(index, 1, 0),
        slide_index(index, 1, 1),
        slide_index(index, 0, -1),
        slide_index(index, 0, 1),
        slide_index(index, -1, -1),
        slide_index(index, -1, 0),
        slide_index(index, -1, 1),
    ]

    # TODO, this does not check whether capture is possible by the king
    # this will be implemented later
    return [
        index for index in squares
        if empty_or_capture(board, index, piece)
    ]


def get_pawn_valid_squares(board, index, capture_only=False):
    piece = board[index]
    d_row = (-1 if get_piece_color(piece) == "W" else 1)
    row = index_to_row(index)

    if capture_only:
        squares = []
    else:
        l1 = [slide_index(index, 0, d_row)]
        if (row == 1 and get_piece_color(piece) == "B") or (row == 6 and get_piece_color(piece) == "W"):
            l1.append(slide_index(index, 0, 2 * d_row))

        # should be empty
        squares = [i for i in l1 if valid_and_empty(board, i)]
    l2 = [slide_index(index, 1, d_row), slide_index(index, -1, d_row)]
    # should be capture
    squares.extend(
        [index for index in l2 if valid_capture(board, index, piece)]
    )
    return squares


def get_knight_valid_squares(board, index):
    piece = board[index]
    squares = [
        slide_index(index, 1, 2),
        slide_index(index, 1, -2),
        slide_index(index, -1, 2),
        slide_index(index, -1, -2),
        slide_index(index, 2, 1),
        slide_index(index, 2, -1),
        slide_index(index, -2, 1),
        slide_index(index, -2, -1),
    ]

    return [index for index in squares
        if empty_or_capture(board, index, piece)
    ]


def _get_piece_valid_squares(board, index):
    piece = board[index]
    squares = {
        "N": get_knight_valid_squares,
        "R": get_rook_valid_squares,
        "Q": get_queen_valid_squares,
        "K": get_king_valid_squares,
        "P": get_pawn_valid_squares,
        "B": get_bishop_valid_squares
    }[get_raw_piece(piece)](board, index)
    return squares


def get_piece_valid_squares(board, sq):
    return _get_piece_valid_squares(board, sq_to_index(sq))


def is_legal_move(board, src, dest):
    """No turn checking."""

    if is_empty_square(board, src):
        raise ValueError("There is no piece at square %s" % index_to_sq(src))

    piece = board[src]
    color = get_color(board, src)

    if dest not in _get_piece_valid_squares(board, src):
        return False

    has_check = is_in_check(gen_successor(board, src, dest), color)
    return not has_check


def is_in_check(board, color):
    # find the king
    king_index = [
        index for index, piece in get_piece_list(board, color)
        if get_raw_piece(piece) == "K"
    ]
    if king_index == []:
        print_board(board)
        raise ValueError("King for color %s not present on board" % color)

    king_pos = king_index[0]

    opp_color = opposite_color(color)
    # get everything for that color
    for index, piece in get_piece_list(board, opp_color):
        vs = _get_piece_valid_squares(board, index)
        if king_pos in vs:
            return True

    return False

def _has_no_legal_moves(board, color):
    # get all possible moves
    for pos, piece in get_piece_list(board, color):
        for dest in _get_piece_valid_squares(board, pos):
            b_new = gen_successor(board, pos, dest)
            if not is_in_check(b_new, color):
                return False

    return True

def is_in_checkmate(board, color):
    """Criteria for checkmate:
    1. is in check
    2. no move will bring the player out of check
    """
    return is_in_check(board, color) and _has_no_legal_moves(board, color)


def is_in_stalemate(board, color):
    return not is_in_check(board, color) and _has_no_legal_moves(board, color)

def get_promotions(board, src, dest):
    if not is_legal_move(board, src, dest):
        return []
    else:
        return _get_promotions(board[src], src, dest)

def _get_promotions(piece, src, dest):
    """Does not check if the move is valid."""
    if get_raw_piece(piece) != "P":
        return []

    if get_piece_color(piece) == "W" and index_to_row(dest) == 0:
        return ["Q", "B", "R", "N"]
    elif get_piece_color(piece) == "B" and index_to_row(dest) == 7:
        return ["q", "b", "r", "n"]
    else:
        return []
