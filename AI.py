from random import choice
from xiangqi import Board, BLACK, RED

class Engine:
    def __init__(self, color):
        assert color in [BLACK, RED]
        self.color = color

    def find_moves(self, board: Board) -> list:
        if board.game_over:
            return None
        if board.current_player != self.color:
            return None
        ai_pieces = [p for p in board.pieces if p.color == self.color]
        ai_moves = []
        for piece in ai_pieces:
            moves = board.get_valid_moves(piece)
            ai_moves.extend([(piece, move) for move in moves])

        return ai_moves

class RandomEngine(Engine):
    def __init__(self, color):
        super().__init__(color)

    def move(self, board: Board):
        self.ai_moves = self.find_moves(board)
        # No possible move found
        if not self.ai_moves:
            board.game_over = True
            board.winner = RED if board.AI.color == BLACK else BLACK
            return None
        
        # Randomly pick a move
        selected_piece, selected_move = choice(self.ai_moves)
        board.last_move = selected_piece.position
        board.move_piece(selected_piece, selected_move)

        board.current_player = RED if board.current_player == BLACK else BLACK

        # Check for endgame condition
        if board.is_checkmate():
            board.game_over = True
            board.winner = self.AI.side
        elif board.check_stalemate():
            board.game_over = True
            board.is_stalemate = True