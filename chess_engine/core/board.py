import sys
from typing import List, Tuple, Optional, Iterator

PieceName = str
Color = bool
# Board = List[str]

E = "E"
G = "G"

# colors (note that colors can be none)
WHITE = True
BLACK = False

PAWN = "P"
KNIGHT = "N"
BISHOP = "B"
ROOK = "R"
QUEEN = "Q"
KING = "K"

PIECES = frozenset([PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING])


# the default board, with guard regions
starter_board = [
    G, G, G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G, G, G,
    G, "r", "n", "b", "q", "k", "b", "n", "r", G,
    G, "p", "p", "p", "p", "p", "p", "p", "p", G,
    G, E, E, E, E, E, E, E, E, G,
    G, E, E, E, E, E, E, E, E, G,
    G, E, E, E, E, E, E, E, E, G,
    G, E, E, E, E, E, E, E, E, G,
    G, "P", "P", "P", "P", "P", "P", "P", "P", G,
    G, "R", "N", "B", "Q", "K", "B", "N", "R", G,
    G, G, G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G, G, G,
]

BOARD_SIZE = len(starter_board)
MIN_PIECE_INDEX = 21
MAX_PIECE_INDEX = 98


class Board:
    def __init__(self, board: Optional[list] = None):
        """
        Make a copy of the given board array
        """
        if board:
            self._board = board[:]
        else:
            self._board = starter_board[:]
        # Move (but no typing for circular imports)
        self._moves = []  # type: list

        # computed properties
        self._ep_possible = False
        # index of the pawn that just moved, the one that will be captured
        self._ep_pawn_index = -1
        # index of the place where the capturing pawn will move to
        self._ep_capture_index = -1
        self._ep_computed = False

        self._check_computed = {
            WHITE: False,
            BLACK: False,
        }
        self._is_in_check = {
            WHITE: False,
            BLACK: False
        }

    def __getitem__(self, index: int) -> PieceName:
        return self._board[index]

    def __setitem__(self, index: int, piece: PieceName) -> None:
        self._board[index] = piece

    def __iter__(self) -> Iterator[PieceName]:
        return iter(self._board)

    def add_move(self, move):
        self._moves.append(move)

    def set_check(self, color: Color, in_check: bool):
        self._is_in_check[color] = in_check
        self._check_computed[color] = True

    def get_check(self, color: Color) -> bool:
        assert self._check_computed[color]
        return self._is_in_check[color]

    def compute_ep_index(self) -> None:
        """if en-passant is valid, there is precisely one index where capture is possible
        Fill up the self._ep* variables
        Additionally set self._ep_computed to true regardless
        """
        if self._moves == []:
            # no previous moves
            self._ep_possible = False
            self._ep_computed = True
            return
        last_move = self._moves[-1]
        if (get_raw_piece(last_move.piece) != PAWN or \
                abs(index_to_row(last_move.src) - index_to_row(last_move.dest)) != 2):
            # last move was not a 2-space pawn move
            self._ep_possible = False
            self._ep_computed = True
            return
        self._ep_possible = True
        self._ep_computed = True
        color = get_piece_color(last_move.piece)
        dy = (1 if color == WHITE else -1)
        self._ep_pawn_index = last_move.dest
        self._ep_capture_index = slide_index(last_move.src, 0, dy)

    def is_en_passant_possible(self) -> bool:
        if not self._ep_computed:
            self.compute_ep_index()
        return self._ep_possible

    def get_ep_capture_index(self) -> int:
        if not self._ep_computed:
            self.compute_ep_index()
        return self._ep_capture_index

    def get_ep_pawn_index(self) -> int:
        if not self._ep_computed:
            self.compute_ep_index()
        return self._ep_capture_index

    def move_piece(self, move) -> None:
        """Convenient way to add the given move"""
        move_piece(self, move.src, move.dest,
                   promotion_piece=move.promotion,
                   is_castle=move.is_castle,
                   is_en_passant=move.is_en_passant)
        self.add_move(move)
        # after a move has been registered, reset ep calculation
        self._ep_computed = False
        self._check_computed = {
            WHITE: False,
            BLACK: False,
        }


def get_piece_list(board: Board, color: Color) -> Iterator[Tuple[int, PieceName]]:
    """
    Return the list of pieces for this color
    :returns: (index, piece name)
    """
    for index in range(MIN_PIECE_INDEX, MAX_PIECE_INDEX + 1):
        piece = board._board[index]
        if get_piece_color(piece) == color:
            yield index, piece


def index_to_sq(index: int) -> str:
    row = index_to_row(index)
    col = index_to_col(index)
    return "%s%d" % (chr(col + 97), row)


def index_to_col(index: int) -> int:
    """
    col is index into letters (0-7)
    """
    return index % 10 - 1


def index_to_row(index: int) -> int:
    """
    Returned row is algebraic (1-8)
    """
    return 8 - (index // 10 - 2)


def sq_to_row_col(sq: str) -> Tuple[int, int]:
    assert isinstance(sq, str)
    assert len(sq) == 2
    row = 8 - int(sq[1])
    col = ord(sq[0]) - 97
    return (row, col)


def sq_to_index(sq: str) -> int:
    """
    square is the square in UCI chess notation
    index is into into board array
    """
    assert isinstance(sq, str)
    assert len(sq) == 2
    row, col = sq_to_row_col(sq)
    return (row + 2) * 10 + col + 1


def is_valid_square(index: int) -> bool:
    return starter_board[index] != G


def is_empty_square(board: Board, index: int) -> bool:
    return board._board[index] == E


def get_color(board: Board, index: int) -> Optional[Color]:
    return get_piece_color(board._board[index])


def slide_index(index: int, dx: int, dy: int) -> int:
    """
    dy operates with respect to algebraic rows
    So a oppositive dy will take you from row 2 to row 3
    Makes it easier to work with rows
    """
    return index + (-10 * dy) + dx


def get_castle_rook_index(board: Board, from_index: int, to_index: int) -> Tuple[int, int]:
    """return (from_index, to_index) for the rook"""
    if from_index < to_index:
        # castle right (short)
        return slide_index(from_index, 3, 0), slide_index(from_index, 1, 0)
    else:
        # castle left (long)
        return slide_index(from_index, -4, 0), slide_index(from_index, -1, 0)


def find_king_index(board: Board, color: Color) -> int:
    target_piece = get_piece_of_color(KING, color)
    for i in range(MIN_PIECE_INDEX, MAX_PIECE_INDEX + 1):
        if board._board[i] == target_piece:
            return i
    raise Exception("King not found")


def move_piece_castle(board: Board, from_index: int, to_index: int) -> None:
    # this should refer to the king only
    piece = board._board[from_index]
    assert get_raw_piece(piece) == KING
    board._board[from_index] = E
    board._board[to_index] = piece
    # find the rook and move it
    rook_from_index, rook_to_index = get_castle_rook_index(board, from_index, to_index)
    piece = board._board[rook_from_index]
    board._board[rook_from_index] = E
    board._board[rook_to_index] = piece


def move_piece_en_passant(board: Board, from_index: int, to_index: int) -> None:
    """
    Must be called with a pawn move
    """
    piece = board._board[from_index]
    color = get_piece_color(piece)
    assert get_raw_piece(piece) == PAWN
    board._board[from_index] = E

    # location of the target pawn
    if color == WHITE:
        en_passant_capture_index = slide_index(to_index, 0, -1)
    else:
        en_passant_capture_index = slide_index(to_index, 0, 1)
    board._board[en_passant_capture_index] = E
    board._board[to_index] = piece


def move_piece(board: Board, from_index: int, to_index: int,
               promotion_piece: Optional[PieceName] = None,
               is_castle=False,
               is_en_passant=False) -> None:
    """No check on this.
    :param promotion: name of the promotion piece"""
    if is_castle:
        move_piece_castle(board, from_index, to_index)
    elif is_en_passant:
        move_piece_en_passant(board, from_index, to_index)
    elif promotion_piece:
        promotion_piece = promotion_piece.upper()
        assert promotion_piece in PIECES
        piece = board._board[from_index]
        color = get_piece_color(piece)
        assert get_raw_piece(piece) == PAWN
        assert color is not None
        assert index_to_row(to_index) in [1, 8]
        board._board[from_index] = E
        board._board[to_index] = get_piece_of_color(promotion_piece, color)
    else:
        piece = board._board[from_index]
        board._board[from_index] = E
        board._board[to_index] = piece


def get_piece_of_color(piece_name: PieceName, color: Color) -> PieceName:
    return (piece_name.upper() if color == WHITE else piece_name.lower())


def get_piece_color(piece: PieceName) -> Optional[Color]:
    if piece == E or piece == G:
        return None
    else:
        return (WHITE if piece.isupper() else BLACK)


def get_raw_piece(piece: PieceName) -> PieceName:
    return piece.upper()


def fen_to_board(fen: str) -> Board:
    """Convert FEN to a row-array"""
    flat_arr = [G]

    for c in fen:
        if c.isdigit():
            for i in range(int(c)):
                flat_arr.append(E)
        elif c.isalpha():
            flat_arr.append(c)
        elif c == " ":
            # ignore the other info
            break
        elif c == "/":
            flat_arr.extend([G, G])

    flat_arr.append(G)
    assert len(flat_arr) == 80
    return Board(([G] * 20) + flat_arr + ([G] * 20))


def load_board(arr) -> Board:
    # this is an array of arrays
    # each sub-array is a row
    # return a proper representation
    # I will mutate arr in place, beware!
    # treat empty strings as empties

    board = [G] * 20
    for row in arr:
        board.extend([G] + [(E if sq.rstrip() == "" else sq) for sq in row] + [G])
    board.extend([G] * 20)
    return Board(board)


def dump_board(board: Board) -> List[List[str]]:
    """dump the board to a relatively simple array-based format"""
    simple_arr = [
        (" " if sq == E else sq) for sq in board
        if sq != G
    ]
    assert len(simple_arr) == 64
    # now split this up into sub-arrays by row
    rows = []
    for i in range(0, 64, 8):
        rows.append(simple_arr[i: i + 8])
    return rows


def print_board(board: Board) -> None:
    print("*" * 18)
    for i, piece in enumerate(board):
        if not is_valid_square(i):
            continue
        if i % 10 == 1:
            print("")
            sq = index_to_sq(i)
            sys.stdout.write("%s " % sq[1])
        if piece == E:
            sys.stdout.write("  ")
        else:
            sys.stdout.write("%s " % piece)

    print("")
    sys.stdout.write("  ")
    for i in range(8):
        sys.stdout.write("%s " % (chr(i + 97)))
    print("")
    print("*" * 18)


def is_capture(board: Board, dest_index: int, piece: PieceName) -> bool:
    """Return True iff the move is a capture.
    :param piece: the piece that is moving"""
    return get_color(board, dest_index) is not None and get_color(board, dest_index) != get_piece_color(piece)
