import pygame
import sys

# Initialize Pygame
pygame.init()

# Window and cell size
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (118, 62, 45)
LIGHT_BROWN = (238, 214, 175)
HIGHLIGHT = (72, 209, 204)
BUTTON_BORDER_COLOR = (0, 0, 128)
GAME_OVER_COLOR = (255, 0, 0)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шахматы")

# Font for letters and numbers
font = pygame.font.Font(None, 24)

# Load piece and background images
pieces = {
    "white_pawn": pygame.image.load("pieces/white_pawn.png"),
    "black_pawn": pygame.image.load("pieces/black_pawn.png"),
    "white_rook": pygame.image.load("pieces/white_rook.png"),
    "black_rook": pygame.image.load("pieces/black_rook.png"),
    "white_knight": pygame.image.load("pieces/white_knight.png"),
    "black_knight": pygame.image.load("pieces/black_knight.png"),
    "white_bishop": pygame.image.load("pieces/white_bishop.png"),
    "black_bishop": pygame.image.load("pieces/black_bishop.png"),
    "white_queen": pygame.image.load("pieces/white_queen.png"),
    "black_queen": pygame.image.load("pieces/black_queen.png"),
    "white_king": pygame.image.load("pieces/white_king.png"),
    "black_king": pygame.image.load("pieces/black_king.png"),
}
background_image = pygame.image.load("backgrounds/chess_background.jpg")

for key in pieces:
    pieces[key] = pygame.transform.scale(pieces[key], (CELL_SIZE, CELL_SIZE))

# Initial piece positions on the board
initial_board = [
    ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_knight",
     "black_rook"],
    ["black_pawn"] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ["white_pawn"] * 8,
    ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_knight",
     "white_rook"],
]

board = [row[:] for row in initial_board]

selected_piece = None
selected_pos = None
valid_moves = []
player_color = "white"  # Default player color
turn = "white"  # Turn order ("white" or "black")
game_over = False
in_main_menu = True

# Create a stack to store board states
board_history = []

# Track whether kings and rooks have moved
king_moved = {"white": False, "black": False}
rook_moved = {"white": {"left": False, "right": False}, "black": {"left": False, "right": False}}


def draw_board():
    """Draw the chessboard."""
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Highlight possible moves
            if (row, col) in valid_moves:
                pygame.draw.rect(screen, HIGHLIGHT, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 5)

    # Draw letters and numbers on the chessboard
    for i in range(ROWS):
        # Numbers (strings)
        text = font.render(str(ROWS - i), True, RED)
        screen.blit(text, (5, i * CELL_SIZE + 5))
        # Letters (columns)
        text = font.render(chr(ord('A') + i), True, RED)
        screen.blit(text, (i * CELL_SIZE + 5, HEIGHT - 20))


def draw_pieces():
    """Draw pieces on the board."""
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                screen.blit(pieces[piece], (col * CELL_SIZE, row * CELL_SIZE))


def get_cell(pos):
    """Returns the row and column of the clicked cell."""
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row, col


def is_valid_position(row, col):
    """Checks if the position is on the board."""
    return 0 <= row < ROWS and 0 <= col < COLS


def is_in_check(board, color):
    """Checks if the 'color' king is in check."""
    king_pos = None
    enemy_color = "black" if color == "white" else "white"

    # Find the king's position
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == f"{color}_king":
                king_pos = (r, c)
                break
        if king_pos:
            break

    # Check all possible moves of the opponent’s pieces
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] and enemy_color in board[r][c]:
                if king_pos in get_valid_moves(board[r][c], (r, c), board):
                    return True

    return False


def is_checkmate(color):
    """Checks if the 'color' king is in checkmate."""
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] and color in board[r][c]:
                piece = board[r][c]
                for move in get_valid_moves(piece, (r, c), board):
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = piece
                    temp_board[r][c] = None
                    if not is_in_check(temp_board, color):
                        return False
    return True


def get_valid_moves(piece, pos, board=None):
    if board is None:
        board = globals()['board']

    row, col = pos
    moves = []

    if "pawn" in piece:
        direction = -1 if "white" in piece else 1
        # Regular pawn move
        if is_valid_position(row + direction, col) and board[row + direction][col] is None:
            moves.append((row + direction, col))
        # First move: two steps
        if (row == 6 and "white" in piece) or (row == 1 and "black" in piece):
            if is_valid_position(row + 2 * direction, col) and board[row + direction][col] is None and \
                    board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        # Diagonal capture
        for dx in [-1, 1]:
            if is_valid_position(row + direction, col + dx):
                if board[row + direction][col + dx] and ("white" in piece) != (
                        "white" in board[row + direction][col + dx]):
                    moves.append((row + direction, col + dx))

    elif "rook" in piece or "queen" in piece:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dr, col + dc
            while is_valid_position(r, c):
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c] and ("white" in piece) != ("white" in board[r][c]):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

    if "bishop" in piece or "queen" in piece:
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row + dr, col + dc
            while is_valid_position(r, c):
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c] and ("white" in piece) != ("white" in board[r][c]):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

    if "knight" in piece:
        for dr, dc in [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]:
            r, c = row + dr, col + dc
            if is_valid_position(r, c):
                if board[r][c] is None or ("white" in piece) != ("white" in board[r][c]):
                    moves.append((r, c))

    if "king" in piece:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            r, c = row + dr, col + dc
            if is_valid_position(r, c):
                if board[r][c] is None or ("white" in piece) != ("white" in board[r][c]):
                    moves.append((r, c))

        # Castling check
        if not king_moved[piece.split('_')[0]]:
            # Queenside castling
            if not rook_moved[piece.split('_')[0]]["left"] and board[row][0] == piece.split('_')[0] + "_rook":
                if all(board[row][i] is None for i in range(1, 4)):
                    moves.append((row, col - 2))
            # Kingside castling
            if not rook_moved[piece.split('_')[0]]["right"] and board[row][7] == piece.split('_')[0] + "_rook":
                if all(board[row][i] is None for i in range(5, 7)):
                    moves.append((row, col + 2))

    return moves


def draw_text(text, font, color, surface, x, y):
    """Draw text on the screen."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def draw_main_menu():
    """Draw the main menu."""
    screen.blit(background_image, (0, 0))
    font = pygame.font.Font(None, 74)
    draw_text("Chess Game", font, RED, screen, WIDTH // 2, HEIGHT // 3)
    font = pygame.font.Font(None, 50)
    button_text = "Start a Game 1 vs 1"
    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 25, 300, 50)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 3)
    draw_text(button_text, font, RED, screen, WIDTH // 2, HEIGHT // 2)

    # Add color selection buttons
    white_button_text = "Play as White"
    black_button_text = "Play as Black"
    white_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 50)
    black_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 125, 300, 50)
    pygame.draw.rect(screen, WHITE, white_button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, white_button_rect, 3)
    pygame.draw.rect(screen, WHITE, black_button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, black_button_rect, 3)
    draw_text(white_button_text, font, RED, screen, WIDTH // 2, HEIGHT // 2 + 75)
    draw_text(black_button_text, font, RED, screen, WIDTH // 2, HEIGHT // 2 + 150)

    return button_rect, white_button_rect, black_button_rect


def draw_restart_button():
    """Draw the restart button after checkmate."""
    font = pygame.font.Font(None, 50)
    button_text = "Restart"
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 3)
    draw_text(button_text, font, RED, screen, WIDTH // 2, HEIGHT // 2 + 75)
    return button_rect


def draw_back_to_main_menu_button():
    """Draw the "Back to Main Menu" button after checkmate."""
    font = pygame.font.Font(None, 50)
    button_text = "Back to Main Menu"
    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 125, 300, 50)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 3)
    draw_text(button_text, font, RED, screen, WIDTH // 2, HEIGHT // 2 + 150)
    return button_rect


def undo_move():
    """Undo the last move."""
    global board, turn, game_over
    if board_history:
        board = board_history.pop()
        turn = "black" if turn == "white" else "white"
        game_over = False


def restart_game():
    """Restart the game."""
    global board, selected_piece, selected_pos, valid_moves, turn, game_over, board_history, king_moved, rook_moved
    board = [row[:] for row in initial_board]
    selected_piece = None
    selected_pos = None
    valid_moves = []
    turn = "white"
    game_over = False
    board_history = []
    king_moved = {"white": False, "black": False}
    rook_moved = {"white": {"left": False, "right": False}, "black": {"left": False, "right": False}}


def main():
    global selected_piece, selected_pos, valid_moves, turn, king_moved, rook_moved, game_over, in_main_menu, player_color

    font = pygame.font.Font(None, 74)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if in_main_menu:
                button_rect, white_button_rect, black_button_rect = draw_main_menu()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_rect.collidepoint(mouse_pos):
                        in_main_menu = False
                    elif white_button_rect.collidepoint(mouse_pos):
                        player_color = "white"
                        turn = "white"
                        in_main_menu = False
                    elif black_button_rect.collidepoint(mouse_pos):
                        player_color = "black"
                        turn = "white"
                        in_main_menu = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    row, col = get_cell(pygame.mouse.get_pos())
                    print(f"Click at cell: ({row}, {col})")

                    if selected_piece:
                        if (row, col) in valid_moves:
                            # Save the current board state before making a move
                            board_history.append([row[:] for row in board])

                            # If the target cell contains an opponent's piece, capture it
                            if board[row][col] is not None:
                                print(f"{selected_piece} captures {board[row][col]} at ({row}, {col})")

                            # Move the selected piece
                            if "king" in selected_piece and abs(selected_pos[1] - col) == 2:
                                # Castling
                                if col == 2:
                                    # Queenside castling
                                    board[row][3] = board[row][0]
                                    board[row][0] = None
                                elif col == 6:
                                    # Kingside castling
                                    board[row][5] = board[row][7]
                                    board[row][7] = None
                                king_moved[selected_piece.split('_')[0]] = True
                            elif "rook" in selected_piece:
                                if selected_pos[1] == 0:
                                    rook_moved[selected_piece.split('_')[0]]["left"] = True
                                elif selected_pos[1] == 7:
                                    rook_moved[selected_piece.split('_')[0]]["right"] = True
                            elif "king" in selected_piece:
                                king_moved[selected_piece.split('_')[0]] = True

                            board[row][col] = selected_piece
                            board[selected_pos[0]][selected_pos[1]] = None

                            # Deselect the piece
                            selected_piece = None
                            selected_pos = None
                            valid_moves = []

                            # Switch turns
                            turn = "black" if turn == "white" else "white"

                            # Check for checkmate
                            if is_checkmate(turn):
                                print(f"Checkmate! {turn} wins!")
                                game_over = True
                        else:
                            # Cancel selection if the move is invalid
                            selected_piece = None
                            selected_pos = None
                            valid_moves = []
                    else:
                        piece = board[row][col]
                        if piece and turn in piece:  # Ensure correct color is making a move
                            selected_piece = piece
                            selected_pos = (row, col)
                            valid_moves = get_valid_moves(piece, (row, col))

                            # Filter moves so the king doesn't remain in check
                            valid_moves = [
                                move for move in valid_moves
                                if not is_in_check(
                                    [[board[r][c] if (r, c) != (row, col) and (r, c) != move else (
                                        None if (r, c) == (row, col) else piece) for c in range(COLS)] for r in
                                     range(ROWS)],
                                    turn
                                )
                            ]

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Pressing the 'R' key to undo a move
                        undo_move()

                if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_button_rect = draw_restart_button()
                    main_menu_button_rect = draw_back_to_main_menu_button()
                    if restart_button_rect.collidepoint(mouse_pos):
                        restart_game()
                    elif main_menu_button_rect.collidepoint(mouse_pos):
                        in_main_menu = True
                        restart_game()

        if in_main_menu:
            draw_main_menu()
        else:
            draw_board()
            draw_pieces()

            if game_over:
                draw_text("Game Over", font, GAME_OVER_COLOR, screen, WIDTH // 2, HEIGHT // 2)
                draw_restart_button()
                draw_back_to_main_menu_button()

        pygame.display.flip()

if __name__ == "__main__":
    main()

