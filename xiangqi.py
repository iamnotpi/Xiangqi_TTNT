import pygame
import os
import random

import AI

# Initialize pygame
pygame.init()

# Set up the game window
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Chinese Chess (Xiangqi)")

# Define colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
WOOD = (210, 180, 140)
HIGHLIGHT = (0, 255, 0, 128)  # Semi-transparent green for highlighting

# Define game board
BOARD_SIZE = (9, 10)
SQUARE_SIZE = 60
PIECE_RADIUS = 25
BOARD_OFFSET_X = 30
BOARD_OFFSET_Y = 30

# Load font
font_path = os.path.join(os.path.dirname(__file__), "SimHei.ttf")
if not os.path.exists(font_path):
    print(f"Font file not found: {font_path}")
    print("Please download SimHei.ttf and place it in the same directory as this script.")
    pygame.quit()
    exit()

FONT = pygame.font.Font(font_path, 30)

class Piece:
    def __init__(self, color, type, position):
        self.color = color
        self.type = type
        self.position = position

    def draw(self, screen):
        x, y = self.position
        pygame.draw.circle(screen, WHITE,
                           (x * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y),
                           PIECE_RADIUS)
        pygame.draw.circle(screen, self.color,
                           (x * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y),
                           PIECE_RADIUS - 2, 2)
        text = FONT.render(self.type, True, self.color)
        text_rect = text.get_rect(center=(x * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y))
        screen.blit(text, text_rect)

    def get_valid_moves(self, board):
        moves = []
        x, y = self.position
        if self.type in ["車", "車"]:  # Chariot
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(1, 10):
                    new_x, new_y = x + dx * i, y + dy * i
                    if not (0 <= new_x < 9 and 0 <= new_y < 10):
                        break
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None:
                        moves.append((new_x, new_y))
                    elif piece.color != self.color:
                        moves.append((new_x, new_y))
                        break
                    else:
                        break
        elif self.type in ["馬", "馬"]:  # Horse
            for dx, dy in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 9 and 0 <= new_y < 10:
                    # Check if the horse's movement is blocked
                    block_x, block_y = x, y
                    if abs(dx) > abs(dy):  # Moving more horizontally
                        block_x += dx // 2
                    else:  # Moving more vertically
                        block_y += dy // 2
                    if board.get_piece_at((block_x, block_y)) is None:
                        piece = board.get_piece_at((new_x, new_y))
                        if piece is None or piece.color != self.color:
                            moves.append((new_x, new_y))
        elif self.type in ["象", "象"]:  # Elephant
            for dx, dy in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 9 and (0 <= new_y < 5 if self.color == BLACK else 5 <= new_y < 10):
                    block_x, block_y = x + dx // 2, y + dy // 2
                    if board.get_piece_at((block_x, block_y)) is None:
                        piece = board.get_piece_at((new_x, new_y))
                        if piece is None or piece.color != self.color:
                            moves.append((new_x, new_y))
        elif self.type in ["士", "士"]:  # Advisor
            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                new_x, new_y = x + dx, y + dy
                if 3 <= new_x <= 5 and (0 <= new_y <= 2 if self.color == BLACK else 7 <= new_y <= 9):
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None or piece.color != self.color:
                        moves.append((new_x, new_y))
        elif self.type in ["帥", "將"]:  # General
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 3 <= new_x <= 5 and (0 <= new_y <= 2 if self.color == BLACK else 7 <= new_y <= 9):
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None or piece.color != self.color:
                        moves.append((new_x, new_y))
            # Check for flying general
            for i in range(1, 10):
                flying_y = y + i if self.color == BLACK else y - i
                if 0 <= flying_y < 10:
                    piece = board.get_piece_at((x, flying_y))
                    if piece and piece.type in ["帥", "將"]:
                        moves.append((x, flying_y))
                        break
                    elif piece:
                        break
        elif self.type in ["炮", "炮"]:  # Cannon
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                jump = False
                for i in range(1, 10):
                    new_x, new_y = x + dx * i, y + dy * i
                    if not (0 <= new_x < 9 and 0 <= new_y < 10):
                        break
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None:
                        if not jump:
                            moves.append((new_x, new_y))
                    elif not jump:
                        jump = True
                    elif jump and piece.color != self.color:
                        moves.append((new_x, new_y))
                        break
                    else:
                        break
        elif self.type in ["兵", "卒"]:  # Soldier
            if self.color == RED:
                if y > 4:  # Not crossed river
                    new_y = y - 1
                    if 0 <= new_y < 10:
                        piece = board.get_piece_at((x, new_y))
                        if piece is None or piece.color != self.color:
                            moves.append((x, new_y))
                else:  # Crossed river
                    for dx, dy in [(0, -1), (-1, 0), (1, 0)]:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < 9 and 0 <= new_y < 10:
                            piece = board.get_piece_at((new_x, new_y))
                            if piece is None or piece.color != self.color:
                                moves.append((new_x, new_y))
            else:  # BLACK
                if y < 5:  # Not crossed river
                    new_y = y + 1
                    if 0 <= new_y < 10:
                        piece = board.get_piece_at((x, new_y))
                        if piece is None or piece.color != self.color:
                            moves.append((x, new_y))
                else:  # Crossed river
                    for dx, dy in [(0, 1), (-1, 0), (1, 0)]:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < 9 and 0 <= new_y < 10:
                            piece = board.get_piece_at((new_x, new_y))
                            if piece is None or piece.color != self.color:
                                moves.append((new_x, new_y))

        return moves

class Board:
    def __init__(self, player_color=RED, vs_AI=True, AI_mode="random"):
        self.pieces = []
        self.setup_pieces()
        self.selected_piece = None
        self.current_player = RED
        self.player_color = player_color
        AI_color = RED if player_color == BLACK else BLACK
        self.AI = AI.RandomEngine(color=AI_color) if vs_AI else None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.is_stalemate = False
        self.last_move = None

    def setup_pieces(self):
        # Red pieces
        self.pieces.extend([
            Piece(RED, "車", (0, 9)), Piece(RED, "馬", (1, 9)),
            Piece(RED, "象", (2, 9)), Piece(RED, "士", (3, 9)),
            Piece(RED, "帥", (4, 9)), Piece(RED, "士", (5, 9)),
            Piece(RED, "象", (6, 9)), Piece(RED, "馬", (7, 9)),
            Piece(RED, "車", (8, 9)), Piece(RED, "炮", (1, 7)),
            Piece(RED, "炮", (7, 7)), Piece(RED, "兵", (0, 6)),
            Piece(RED, "兵", (2, 6)), Piece(RED, "兵", (4, 6)),
            Piece(RED, "兵", (6, 6)), Piece(RED, "兵", (8, 6))
        ])

        # Black pieces
        self.pieces.extend([
            Piece(BLACK, "車", (0, 0)), Piece(BLACK, "馬", (1, 0)),
            Piece(BLACK, "象", (2, 0)), Piece(BLACK, "士", (3, 0)),
            Piece(BLACK, "將", (4, 0)), Piece(BLACK, "士", (5, 0)),
            Piece(BLACK, "象", (6, 0)), Piece(BLACK, "馬", (7, 0)),
            Piece(BLACK, "車", (8, 0)), Piece(BLACK, "炮", (1, 2)),
            Piece(BLACK, "炮", (7, 2)), Piece(BLACK, "卒", (0, 3)),
            Piece(BLACK, "卒", (2, 3)), Piece(BLACK, "卒", (4, 3)),
            Piece(BLACK, "卒", (6, 3)), Piece(BLACK, "卒", (8, 3))
        ])

    def draw(self, screen):
        # Draw board lines
        for x in range(9):
            pygame.draw.line(screen, BLACK,
                             (x * SQUARE_SIZE + BOARD_OFFSET_X, BOARD_OFFSET_Y),
                             (x * SQUARE_SIZE + BOARD_OFFSET_X, 9 * SQUARE_SIZE + BOARD_OFFSET_Y))
        for y in range(10):
            pygame.draw.line(screen, BLACK,
                             (BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y),
                             (8 * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y))

        # Draw river
        text = FONT.render("楚 河            漢 界", True, BLACK)
        screen.blit(text, (SQUARE_SIZE + BOARD_OFFSET_X, 4 * SQUARE_SIZE + BOARD_OFFSET_Y + 15))

        # Draw palace
        for y in [0, 7]:
            pygame.draw.line(screen, BLACK,
                             (3 * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y),
                             (5 * SQUARE_SIZE + BOARD_OFFSET_X, (y + 2) * SQUARE_SIZE + BOARD_OFFSET_Y))
            pygame.draw.line(screen, BLACK,
                             (5 * SQUARE_SIZE + BOARD_OFFSET_X, y * SQUARE_SIZE + BOARD_OFFSET_Y),
                             (3 * SQUARE_SIZE + BOARD_OFFSET_X, (y + 2) * SQUARE_SIZE + BOARD_OFFSET_Y))

        # Draw pieces
        for piece in self.pieces:
            piece.draw(screen)

        # Highlight selected piece and valid moves
        if self.selected_piece:
            x, y = self.get_screen_position(self.selected_piece.position)

            for move in self.valid_moves:
                x, y = self.get_screen_position(move)
                pygame.draw.circle(screen, HIGHLIGHT, (x, y), PIECE_RADIUS // 2)

        # Draw game over message
        if self.game_over:
            font = pygame.font.Font(None, 36)
            if self.is_stalemate:
                text = font.render("Stalemate!", True, BLACK)
            else:
                winner = "Red" if self.winner == RED else "Black"
                text = font.render(f"{winner} wins!", True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] - 30))
            screen.blit(text, text_rect)

        if self.last_move:
            x, y = self.get_screen_position(self.last_move)
            pygame.draw.circle(screen, (0, 255, 255), (x, y), 10)

    def get_piece_at(self, position):
        for piece in self.pieces:
            if piece.position == position:
                return piece
        return None

    def get_board_position(self, mouse_pos):
        x = (mouse_pos[0] - BOARD_OFFSET_X + SQUARE_SIZE // 2) // SQUARE_SIZE
        y = (mouse_pos[1] - BOARD_OFFSET_Y + SQUARE_SIZE // 2) // SQUARE_SIZE
        return max(0, min(x, 8)), max(0, min(y, 9))

    def get_screen_position(self, board_pos):
        return (board_pos[0] * SQUARE_SIZE + BOARD_OFFSET_X,
                board_pos[1] * SQUARE_SIZE + BOARD_OFFSET_Y)
    
    def handle_ai_move(self):
        if self.AI is None or self.game_over:
            return

        if self.current_player != self.AI.color:
            return

        ai_pieces = [p for p in self.pieces if p.color == self.AI.color]
        all_moves = []
        for piece in ai_pieces:
            moves = self.get_valid_moves(piece)
            all_moves.extend([(piece, move) for move in moves])

        if not all_moves:
            self.game_over = True
            self.winner = RED if self.AI.color == BLACK else BLACK
            return

        # Choose a random move from all valid moves
        selected_piece, selected_move = random.choice(all_moves)

        # Make the move
        self.move_piece(selected_piece, selected_move)

        # Switch the current player
        self.current_player = RED if self.current_player == BLACK else BLACK

        # Check for game over conditions
        if self.is_checkmate():
            self.game_over = True
            self.winner = self.AI.side
        elif self.check_stalemate():
            self.game_over = True
            self.is_stalemate = True

    def handle_click(self, pos):
        if self.game_over:
            return

        x, y = self.get_board_position(pos)
        clicked_piece = self.get_piece_at((x, y))

        if self.selected_piece:
            if (x, y) in self.valid_moves:
                self.move_piece(self.selected_piece, (x, y))
                self.selected_piece = None
                self.valid_moves = []
                self.current_player = RED if self.current_player == BLACK else BLACK

                # Check for game over conditions
                if self.is_checkmate():
                    self.game_over = True
                    self.winner = RED if self.current_player == BLACK else BLACK
                elif self.check_stalemate():
                    self.game_over = True
                    self.is_stalemate = True
                
                # Handle AI move if it's AI's turn
                if not self.game_over and self.AI is not None:
                    self.handle_ai_move()
            elif clicked_piece and clicked_piece.color == self.current_player:
                self.selected_piece = clicked_piece
                self.valid_moves = self.get_valid_moves(clicked_piece)
            else:
                self.selected_piece = None
                self.valid_moves = []
        elif clicked_piece and clicked_piece.color == self.current_player:
            self.selected_piece = clicked_piece
            self.valid_moves = self.get_valid_moves(clicked_piece)

    def move_piece(self, piece: Piece, new_position: tuple):
        captured_piece = self.get_piece_at(new_position)
        if captured_piece:
            self.pieces.remove(captured_piece)
        self.last_move = piece.position
        piece.position = new_position

    def get_valid_moves(self, piece):
        # Get all potential moves
        potential_moves = piece.get_valid_moves(self)
        
        # Filter out moves that would result in check
        return [move for move in potential_moves if not self.is_check_after_move(piece, move)]


    def is_check_after_move(self, piece, move):
        original_position = piece.position
        captured_piece = self.get_piece_at(move)

        # Temporarily make the move
        if captured_piece:
            self.pieces.remove(captured_piece)
        piece.position = move

        # Check if the move results in check
        in_check = self.is_in_check(piece.color)

        # Undo the move
        piece.position = original_position
        if captured_piece:
            self.pieces.append(captured_piece)

        return in_check

    def is_in_check(self, color):
        general = next((p for p in self.pieces if p.type in ["帥", "將"] and p.color == color), None)
        if not general:
            return False

        for piece in self.pieces:
            if piece.color != color:
                if general.position in piece.get_valid_moves(self):
                    return True
        return False

    def is_checkmate(self):
        for piece in self.pieces:
            if piece.color == self.current_player:
                if self.get_valid_moves(piece):
                    return False
        return self.is_in_check(self.current_player)

    def check_stalemate(self):
        if self.is_in_check(self.current_player):
            return False
        for piece in self.pieces:
            if piece.color == self.current_player:
                if self.get_valid_moves(piece):
                    return False
        return True

def main():
    board = Board()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.handle_click(event.pos)

        screen.fill(WOOD)
        board.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()