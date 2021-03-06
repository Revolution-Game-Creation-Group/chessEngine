import unittest as T

from chess_engine.core.board import (dump_board, fen_to_board,
                                load_board, print_board, sq_to_index,
                                BLACK, WHITE, Board)
from chess_engine.core.move import gen_successor
from chess_engine.core.piece_movement_rules import (_has_no_legal_moves,
                                               get_bishop_valid_squares,
                                               get_king_valid_squares,
                                               get_knight_valid_squares,
                                               get_pawn_valid_squares,
                                               get_piece_valid_squares,
                                               get_promotions,
                                               get_queen_valid_squares,
                                               get_rook_valid_squares,
                                               is_in_check, is_in_checkmate,
                                               is_in_stalemate, is_legal_move)


class PieceMovementTest(T.TestCase):
    def test_rook_starter_board_valid_squares(self):
        board = Board()
        index = sq_to_index("a1")
        assert [sq for sq in get_rook_valid_squares(board, index)] == []

    def test_rook_empty_board_valid_squares(self):
        board = load_board([
            ["", "", "", "", "", "", "", ""],
            ["", "R", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        rook_squares = sorted([sq_to_index(sq) for sq in
                               ["a7", "b1", "b2", "b3", "b4", "b5", "b6", "b8",
                                "c7", "d7", "e7", "f7", "g7", "h7"]])
        assert sorted(get_rook_valid_squares(board, sq_to_index("b7"))) == rook_squares

    def test_rook_blocked_capture_valid_squares(self):
        board = load_board([
            ["n", "R", "", "q", "", "", "", ""],
            ["", "r", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        rook_squares = sorted([sq_to_index(sq) for sq in ["a8", "b7", "c8", "d8"]])
        assert sorted(get_rook_valid_squares(board, sq_to_index("b8"))) == rook_squares

    def test_rook_blocked_own_piece_valid_squares(self):
        board = load_board([
            ["", "R", "", "Q", "", "", "", ""],
            ["", "N", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        rook_squares = sorted([sq_to_index(sq) for sq in ["a8", "c8"]])
        assert sorted(get_rook_valid_squares(board, sq_to_index("b8"))) == rook_squares

    def test_rook_valid_squares_capture_blocks_own_piece(self):
        board = load_board([
            ["R", "", "", "", "", "k", "", "K"],
            ["n", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        rook_squares = sorted([sq_to_index(sq) for sq in ["a7", "b8", "c8", "d8", "e8", "f8"]])
        assert sorted(get_rook_valid_squares(board, sq_to_index("a8"))) == rook_squares

    def test_bishop_valid_squares(self):
        board = Board()
        index = sq_to_index("c1")
        assert [sq for sq in get_bishop_valid_squares(board, index)] == []

    def test_queen_valid_squares(self):
        board = Board()
        index = sq_to_index("d1")
        assert [sq for sq in get_queen_valid_squares(board, index)] == []

    def test_king_valid_squares(self):
        board = Board()
        index = sq_to_index("e1")
        assert [sq for sq in get_king_valid_squares(board, index)] == []
        assert [sq for sq in get_king_valid_squares(board, index)] == []

    def test_pawn_valid_squares(self):
        board = Board()
        index = sq_to_index("e2")
        pawn_sq = sorted([sq_to_index(sq) for sq in ["e3", "e4"]])
        assert sorted(get_pawn_valid_squares(board, index)) == pawn_sq

    def test_knight_valid_squares(self):
        board = Board()
        index = sq_to_index("b1")
        knight_sq = sorted([sq_to_index(sq) for sq in ["a3", "c3"]])
        assert sorted(get_knight_valid_squares(board, index)) == knight_sq

    def test_piece_valid_squares(self):
        board = Board()
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("e1"))] == []
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("d1"))] == []
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("c1"))] == []
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("a1"))] == []
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("a8"))]  == []
        assert [sq for sq in get_piece_valid_squares(board, sq_to_index("e8"))] == []
        assert sorted(get_piece_valid_squares(board, sq_to_index("e2"))) == \
            sorted([sq_to_index(idx) for idx in ["e3", "e4"]])

    def test_is_legal_pawn_move(self):
        board = Board()
        assert is_legal_move(board, sq_to_index("e2"), sq_to_index("e3"))
        assert is_legal_move(board, sq_to_index("e2"), sq_to_index("e4"))
        assert not is_legal_move(board, sq_to_index("e2"), sq_to_index("e5"))
        assert not is_legal_move(board, sq_to_index("e2"), sq_to_index("f3"))
        assert is_legal_move(board, sq_to_index("e7"), sq_to_index("e6"))
        assert is_legal_move(board, sq_to_index("e7"), sq_to_index("e5"))
        assert not is_legal_move(board, sq_to_index("e7"), sq_to_index("e4"))

    def test_promotions_not_pawn(self):
        board = load_board([
            [" ", "", "", "", "", "k", "", "K"],
            ["R", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "],
            [" ", "", "", "", "", " ", "", " "]
        ])
        board = Board()
        assert get_promotions(board, sq_to_index("a7"), sq_to_index("a8")) == []

    def test_promotions_pawn_backwards(self):
        board = load_board([
            [" ", "", "", "", " ", "k", "", "K"],
            ["p", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "]
        ])
        assert get_promotions(board, sq_to_index("a7"), sq_to_index("a8")) == []

    def test_promotions_pawn_forward_two_spaces(self):
        board = load_board([
            [" ", "", "", "", " ", "k", "", "K"],
            [" ", "", "", "", " ", " ", "", " "],
            ["P", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "]
        ])
        assert get_promotions(board, sq_to_index("a6"), sq_to_index("a8")) == []

    def test_promotions_pawn_white_move(self):
        board = load_board([
            [" ", "", "", "", " ", "k", "", "K"],
            ["P", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "]
        ])
        assert sorted(get_promotions(board, sq_to_index("a7"), sq_to_index("a8"))) == \
            sorted(["Q", "R", "B", "N"])

    def test_promotions_pawn_black_move(self):
        board = load_board([
            [" ", "", "", "", " ", "k", "", "K"],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "],
            ["p", "", "", "", " ", " ", "", " "],
            [" ", "", "", "", " ", " ", "", " "]
        ])
        assert sorted(get_promotions(board, sq_to_index("a2"), sq_to_index("a1"))) == \
            sorted(["q", "r", "b", "n"])

    def test_promotions_pawn_black_capture(self):
        board = load_board([
            [" ", " ", "", "", " ", "k", "", "K"],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            ["p", " ", "", "", " ", " ", "", " "],
            [" ", "B", "", "", " ", " ", "", " "]
        ])
        assert sorted(get_promotions(board, sq_to_index("a2"), sq_to_index("a1"))) == \
            sorted(["q", "r", "b", "n"])
        assert sorted(get_promotions(board, sq_to_index("a2"), sq_to_index("b1"))) == \
            sorted(["q", "r", "b", "n"])

    def test_promotions_blocked(self):
        board = load_board([
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            [" ", " ", "", "", " ", " ", "", " "],
            ["k", " ", "", "", " ", " ", "", " "],
            ["p", " ", "", "", " ", " ", "", " "],
            ["K", " ", "", "", " ", " ", "", " "]
        ])
        assert get_promotions(board, sq_to_index("a2"), sq_to_index("a1")) == []
        assert get_promotions(board, sq_to_index("a2"), sq_to_index("b1")) == []


class CheckTest(T.TestCase):
    def test_bishop_check(self):
        board = fen_to_board("7k/8/8/4B3/8/8/8/K7 w")
        assert is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_pawn_can_defend(self):
        board = fen_to_board("7k/5p2/8/4B3/8/8/8/K7 w")
        print_board(board)
        assert is_in_check(board, BLACK)
        new_board = gen_successor(Board(board), sq_to_index("f7"), sq_to_index("f6"))
        print_board(new_board)
        assert not is_in_check(new_board, BLACK)
        # it follows that black is not in checkmate
        assert not is_in_checkmate(board, BLACK)

    def test_pawn_not_give_check_above(self):
        board = load_board([
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', 'k', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', 'P', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', 'K', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        ])
        assert not is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_pawn_give_check(self):
        board = load_board([
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', 'k', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', 'P', ' ', ' '],
            [' ', ' ', ' ', ' ', 'K', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        ])
        assert is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_is_in_check_starter_board(self):
        board = Board()
        assert not is_in_check(board, WHITE)
        assert not is_in_check(board, BLACK)

    def test_is_in_check_basic_rook(self):
        board = load_board([
            ["R", "", "", "", "k", "", "K", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_is_in_check_basic_rook_2(self):
        board = load_board([
            ["R", "", "", "", "k", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
            [" ", "", "", "", "K", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
            [" ", "", "", "", " ", "", "", ""],
        ])
        assert is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_is_in_check_basic_bishop(self):
        board = load_board([
            ["B", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "k", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "K", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert is_in_check(board, BLACK)
        assert not is_in_check(board, WHITE)

    def test_is_in_checkmate_simple_rook_mate(self):
        board = load_board([
            ["", "R", "", "k", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "K", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert is_in_checkmate(board, BLACK)
        assert not is_in_checkmate(board, WHITE)

    def test_is_in_checkmate_unprotected_attacker(self):
        board = load_board([
            ["k", "", "", "", "", "", "", ""],
            ["", "Q", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "K", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert not is_in_checkmate(board, BLACK)

    def test_is_in_checkmate_simple_rook_check(self):
        board = load_board([
            ["", "R", "", "", "k", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "K", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert not is_in_checkmate(board, BLACK)
        assert not is_in_checkmate(board, WHITE)

    def test_is_in_stalemate_with_rook(self):
        board = load_board([
            ["k", "", "", "", "", "", "", ""],
            ["", "R", "", "", "", "", "", ""],
            ["", "", "K", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
        ])
        assert is_in_stalemate(board, BLACK)
        assert not is_in_checkmate(board, BLACK)

    def test_not_in_mate_1(self):
        board = load_board([
            [' ', ' ', ' ', ' ', 'r', 'b', 'Q', 'k'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'p'],
            ['p', ' ', ' ', 'p', ' ', 'P', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', 'R', ' ', ' '],
            [' ', ' ', ' ', ' ', 'q', ' ', ' ', 'P'],
            [' ', 'P', ' ', ' ', 'P', ' ', ' ', ' '],
            ['P', 'B', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', 'K', ' ']
        ])

        b2 = gen_successor(Board(board), sq_to_index("h8"), sq_to_index("g8"))
        for row in dump_board(b2):
            print(row)
        assert not is_in_check(b2, BLACK)

        assert not is_in_checkmate(board, BLACK)
        assert not is_in_checkmate(board, WHITE)
        assert not is_in_stalemate(board, BLACK)
        assert not is_in_stalemate(board, WHITE)
        assert not _has_no_legal_moves(board, BLACK)
