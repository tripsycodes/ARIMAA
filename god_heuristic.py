import pygame
import os
import random
import math
from copy import deepcopy
import time

# Set up the game window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 640  # Extra height for displaying turn info
BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE  # Each square is 75 pixels

# Colors for the board
LIGHT_COLOR = (240, 217, 181)  # Beige
DARK_COLOR = (181, 136, 99)    # Brown
TRAP_COLOR = (255, 180, 60)    # Amber
HIGHLIGHT_COLOR = (200, 200, 100)  # Yellow

# Trap squares where pieces can be captured
TRAPS = [(2, 2), (2, 5), (5, 2), (5, 5)]

# Starting board (8x8 grid)
board = [
    ["SE", "SH", "ST", "SC", "SE", "SC", "SH", "SD"],
    ["SR", "SR", "SR", "SR", "SR", "SR", "SR", "SR"],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    ["GR", "GR", "GR", "GR", "GR", "GR", "GR", "GR"],
    ["GD", "GH", "GT", "GE", "GE", "GC", "GH", "GD"]
]

PIECE_IMAGES = {
    'GE': 'gold_elephant.png',
    'GC': 'gold_camel.png',
    'GT': 'gold_cat.png',
    'GH': 'gold_horse.png',
    'GD': 'gold_dog.png',
    'GR': 'gold_rabbit.png',
    'SE': 'silver_elephant.png',
    'SC': 'silver_camel.png',
    'ST': 'silver_cat.png',
    'SH': 'silver_horse.png',
    'SD': 'silver_dog.png',
    'SR': 'silver_rabbit.png'
}

# Piece strengths (higher number = stronger piece)
# Piece strengths (higher number = stronger piece)
piece_strength = {
    "GE": 5, "GC": 4, "GH": 3, "GD": 2, "GT": 1, "GR": 0,
    "SE": 5, "SC": 4, "SH": 3, "SD": 2, "ST": 1, "SR": 0,
    " ": -1  # Empty space
}

# Game variables
whose_turn = "Gold"  # Gold goes first
move_count = 0  # How many moves made this turn
game_finished = False  # Is the game over?
move_history = []  # Store previous board states to detect loops
max_history_length = 10  # Keep the last 10 board states for loop detection

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Arimaa: Minimax vs Heuristic")

def load_images():
    """Load images for each piece."""
    images = {}
    for piece, filename in PIECE_IMAGES.items():
        try:
            path = os.path.join(os.getcwd(), filename)
            images[piece] = pygame.image.load(path)
            images[piece] = pygame.transform.scale(images[piece], (CELL_SIZE - 10, CELL_SIZE - 10))
            print(f"Loaded image for {piece}: {filename}")
        except Exception as e:
            print(f"Failed to load image for {piece}: {e}")
            # Create a fallback colored square
            img = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
            color = (218, 165, 32) if piece[0] == 'G' else (192, 192, 192)
            pygame.draw.rect(img, color, (0, 0, CELL_SIZE - 10, CELL_SIZE - 10))
            font = pygame.font.SysFont('Arial', 20, bold=True)
            text = font.render(piece, True, (0, 0, 0))
            text_rect = text.get_rect(center=(img.get_width()//2, img.get_height()//2))
            img.blit(text, text_rect)
            images[piece] = img
    return images

# Load piece images
piece_images = load_images()

def draw_board():
    """Draw the board and all pieces on it."""
    global board, piece_images
    
    # Draw the board squares
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Set color: light or dark checkerboard pattern
            if (row + col) % 2 == 0:
                color = LIGHT_COLOR
            else:
                color = DARK_COLOR
            
            # Traps get a special highlight
            if (row, col) in TRAPS:
                color = TRAP_COLOR
                # Make trap squares slightly red-tinted
                # if (row + col) % 2 == 0:
                #     color = (min(255, LIGHT_COLOR[0] + 20), max(0, LIGHT_COLOR[1] - 30), max(0, LIGHT_COLOR[2] - 30))
                # else:
                #     color = (min(255, DARK_COLOR[0] + 20), max(0, DARK_COLOR[1] - 30), max(0, DARK_COLOR[2] - 30))
            
            # Draw the square
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            # if (row, col) in TRAPS:
            #     pygame.draw.circle(screen, TRAP_COLOR, 
            #                       (col * CELL_SIZE + CELL_SIZE // 2, 
            #                        row * CELL_SIZE + CELL_SIZE // 2), 
            #                       8, 2)  # Outlined circle
            
            # Draw the piece if present
            piece = board[row][col]
            if piece != "  " and piece in piece_images:
                img_rect = piece_images[piece].get_rect(
                    center=(col * CELL_SIZE + CELL_SIZE // 2, 
                           row * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(piece_images[piece], img_rect)
    
    # Draw the grid lines
    # grid_color = (50, 50, 50)
    # for i in range(BOARD_SIZE + 1):
    #     # Horizontal lines
    #     pygame.draw.line(screen, grid_color, 
    #                     (0, i * CELL_SIZE), 
    #                     (WINDOW_WIDTH, i * CELL_SIZE), 1)
    #     # Vertical lines
    #     pygame.draw.line(screen, grid_color, 
    #                     (i * CELL_SIZE, 0), 
    #                     (i * CELL_SIZE, BOARD_SIZE * CELL_SIZE), 1)
    
    # Add row and column labels
    font = pygame.font.SysFont('Arial', 14)
    # for i in range(BOARD_SIZE):
    #     # Row labels (numbers)
    #     label = font.render(str(BOARD_SIZE - i), True, (150, 150, 150))
    #     screen.blit(label, (5, i * CELL_SIZE + 5))
        
    #     # Column labels (letters)
    #     label = font.render(chr(65 + i), True, (150, 150, 150))
    #     screen.blit(label, (i * CELL_SIZE + CELL_SIZE - 15, BOARD_SIZE * CELL_SIZE - 20))

    # # Display turn information and controls at bottom
    # font = pygame.font.SysFont('Arial', 18)
    
    # Turn info
    info_text = f"Turn: {whose_turn} ({'Minimax AI' if whose_turn == 'Gold' else 'Heuristic AI'}) - Moves: {move_count}/4"
    info_surface = font.render(info_text, True, (255, 255, 255))
    screen.blit(info_surface, (10, BOARD_SIZE * CELL_SIZE + 10))
    
    # Controls
    controls_text = "Controls: SPACE to advance, R to restart, ESC to quit"
    controls_surface = font.render(controls_text, True, (200, 200, 200))
    screen.blit(controls_surface, (WINDOW_WIDTH - 400, BOARD_SIZE * CELL_SIZE + 10))
    
    # Show win message if game is over
    if game_finished:
        font = pygame.font.Font(None, 48)
        win_message = f"{whose_turn} Wins!"
        text = font.render(win_message, True, (255, 255, 255))
        text_pos = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        pygame.draw.rect(screen, (0, 0, 0), text_pos.inflate(20, 20))  # Black background
        screen.blit(text, text_pos)

def is_frozen(board, row, col):
    """Check if a piece is frozen (surrounded by stronger enemy pieces)."""
    if board[row][col] == "  ":
        return False
        
    piece = board[row][col]
    player_prefix = piece[0]
    strength = piece_strength[piece]
    
    # Check if any adjacent position has a stronger enemy piece
    has_stronger_enemy = False
    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        adj_row, adj_col = row + dr, col + dc
        if 0 <= adj_row < BOARD_SIZE and 0 <= adj_col < BOARD_SIZE:
            adj_piece = board[adj_row][adj_col]
            if adj_piece != "  " and adj_piece[0] != player_prefix:
                if piece_strength[adj_piece] > strength:
                    has_stronger_enemy = True
                    break
    
    if not has_stronger_enemy:
        return False
    
    # Check if any adjacent position has a friendly piece
    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        adj_row, adj_col = row + dr, col + dc
        if 0 <= adj_row < BOARD_SIZE and 0 <= adj_col < BOARD_SIZE:
            adj_piece = board[adj_row][adj_col]
            if adj_piece != "  " and adj_piece[0] == player_prefix:
                return False  # Not frozen, has friendly support
    
    return True  # Frozen: has stronger enemy and no friendly support

def can_move(board, start_row, start_col, end_row, end_col):
    """Check if a piece can legally move from start to end."""
    # Check if coordinates are valid
    if not (0 <= start_row < BOARD_SIZE and 0 <= start_col < BOARD_SIZE):
        return False
    if not (0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE):
        return False
    
    # Check if there's a piece at the start
    piece = board[start_row][start_col]
    if piece == "  ":
        return False
    
    # Check if the destination is empty
    if board[end_row][end_col] != "  ":
        return False
    
    # Check if move is orthogonal (no diagonals)
    if start_row != end_row and start_col != end_col:
        return False
    
    # Check if move is adjacent (no jumps)
    if abs(start_row - end_row) + abs(start_col - end_col) != 1:
        return False
    
    # Check if the piece is frozen
    if is_frozen(board, start_row, start_col):
        return False
    
    # Special rule for rabbits: cannot move backward
    if piece[1] == 'R':
        if piece[0] == 'G' and end_row > start_row:  # Gold rabbits can't move down
            return False
        if piece[0] == 'S' and end_row < start_row:  # Silver rabbits can't move up
            return False
    
    return True

def can_push_pull(board, piece_row, piece_col, target_row, target_col):
    """Check if a piece can push or pull the target piece."""
    # Check if coordinates are valid
    if not (0 <= piece_row < BOARD_SIZE and 0 <= piece_col < BOARD_SIZE):
        return False
    if not (0 <= target_row < BOARD_SIZE and 0 <= target_col < BOARD_SIZE):
        return False
    
    # Check if there's a piece at both positions
    piece = board[piece_row][piece_col]
    target = board[target_row][target_col]
    if piece == "  " or target == "  ":
        return False
    
    # Check if they're different colors
    if piece[0] == target[0]:
        return False
    
    # Check if they're adjacent
    if abs(piece_row - target_row) + abs(piece_col - target_col) != 1:
        return False
    
    # Check if the pushing/pulling piece is stronger
    if piece_strength[piece] <= piece_strength[target]:
        return False
    
    # Check if the piece is frozen
    if is_frozen(board, piece_row, piece_col):
        return False
    
    return True

def check_traps(board):
    """Check all trap squares and remove pieces without adjacent friendly pieces."""
    # Trap locations (row, col)
    traps = [(2, 2), (2, 5), (5, 2), (5, 5)]
    
    # Check each trap
    for trap_row, trap_col in traps:
        # If there's a piece on a trap
        if board[trap_row][trap_col] != "  ":
            piece = board[trap_row][trap_col]
            player_prefix = piece[0]  # 'G' or 'S'
            
            # Check if there's any adjacent friendly piece
            has_friendly_support = False
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_row, adj_col = trap_row + dr, trap_col + dc
                if 0 <= adj_row < BOARD_SIZE and 0 <= adj_col < BOARD_SIZE:
                    adj_piece = board[adj_row][adj_col]
                    if adj_piece != "  " and adj_piece[0] == player_prefix:
                        has_friendly_support = True
                        break
            
            # If no friendly support, the piece is captured
            if not has_friendly_support:
                #print(f"Piece {piece} captured at trap ({trap_row}, {trap_col})")
                board[trap_row][trap_col] = "  "  # Remove the piece
    
    return board

def check_winner(board):
    """Check if the game is won and set the winner."""
    global game_finished, whose_turn
    
    # Check for rabbit elimination
    gr_count = 0
    sr_count = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'GR':
                gr_count += 1
            if board[row][col] == 'SR':
                sr_count += 1
    
    # If all rabbits of one side are eliminated
    if gr_count == 0:
        print("All Gold rabbits eliminated - Silver wins!")
        whose_turn = 'Silver'
        game_finished = True
        return True
    elif sr_count == 0:
        print("All Silver rabbits eliminated - Gold wins!")
        whose_turn = 'Gold'
        game_finished = True
        return True
    
    # Check for rabbit reaching goal row
    for col in range(BOARD_SIZE):
        if board[0][col] == "GR":  # Gold rabbit at top row
            print("Gold rabbit reached the goal row - Gold wins!")
            print(col)
            whose_turn = "Gold"
            game_finished = True
            return True
        if board[7][col] == "SR":  # Silver rabbit at bottom row
            print("Silver rabbit reached the goal row - Silver wins!")
            print(col)
            whose_turn = "Silver"
            game_finished = True
            return True
    
    return False

def heuristic(board, add_noise=False):
    """Evaluate the board position from Gold's perspective."""
    h = 0
    
    # Piece value weights
    piece_values = {
        'SE': 100, 'SC': 50, 'SH': 30, 'SD': 20, 'ST': 15, 'SR': 10,
        'GE': -100, 'GC': -50, 'GH': -30, 'GD': -20, 'GT': 15, 'GR': -10,
        ' ': 0
    }
    
    # Count material
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            h += piece_values.get(piece, 0)
    
    # Rabbit advancement - Silver rabbits want to go down, Gold rabbits want to go up
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == 'SR':
                # Exponential reward for advancement
                h += (row + 1) ** 2
                # Extra bonus for being close to the goal row
                if row == 7:
                    h = float('inf')  # Win condition
                elif row >= 6:  # One step away from winning
                    h += 200
                elif row >= 5:  # Two steps away
                    h += 100
                
            elif piece == 'GR':
                # Penalize Gold rabbit advancement (since this is from Silver's perspective)
                h -= (8 - row) ** 2
                if row == 0:
                    h = -float('inf')  # Loss condition
    
    # Control of center - pieces in the center have more influence
    center_value = [
        [1, 1, 2, 2, 2, 2, 1, 1],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [2, 3, 4, 4, 4, 4, 3, 2],
        [2, 3, 4, 5, 5, 4, 3, 2],
        [2, 3, 4, 5, 5, 4, 3, 2],
        [2, 3, 4, 4, 4, 4, 3, 2],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [1, 1, 2, 2, 2, 2, 1, 1]
    ]
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece.startswith('S'):
                h += center_value[row][col] * 2
            elif piece.startswith('G'):
                h -= center_value[row][col] * 2
    
    # Trap control and piece safety
    for trap_row, trap_col in TRAPS:
        silver_adjacent = 0
        gold_adjacent = 0
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = trap_row + dr, trap_col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                piece = board[r][c]
                if piece.startswith('S'):
                    silver_adjacent += 1
                elif piece.startswith('G'):
                    gold_adjacent += 1
        
        # Reward for controlling trap
        if silver_adjacent > gold_adjacent:
            h += 15 * (silver_adjacent - gold_adjacent)
        elif gold_adjacent > silver_adjacent:
            h -= 15 * (gold_adjacent - silver_adjacent)
        
        # Check pieces in traps
        piece_in_trap = board[trap_row][trap_col]
        if piece_in_trap != " ":
            if piece_in_trap.startswith('S') and silver_adjacent == 0:
                h -= 50  # Severe penalty for unsupported piece in trap
            elif piece_in_trap.startswith('G') and gold_adjacent == 0:
                h += 50  # Reward for enemy piece about to be captured
    
    # File control - reward controlling files (columns)
    for col in range(BOARD_SIZE):
        silver_count = 0
        gold_count = 0
        for row in range(BOARD_SIZE):
            piece = board[row][col]
            if piece.startswith('S'):
                silver_count += 1
            elif piece.startswith('G'):
                gold_count += 1
        
        # Reward for controlling files
        if silver_count > gold_count:
            h += 10 * (silver_count - gold_count)
        elif gold_count > silver_count:
            h -= 10 * (gold_count - silver_count)
    
    # Piece mobility and safety
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece != " ":
                # Count possible moves for this piece
                moves = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c] == " " and not is_frozen(board, row, col):
                            moves += 1
                
                # Reward mobility
                if piece.startswith('S'):
                    h += moves * 2
                else:
                    h -= moves * 2
    
    # Add a small amount of noise to prevent repetitive patterns
    if add_noise:
        h += random.uniform(-20, 20)
    
    return h

def debug_moves(board, player):
    """Debug function to print available moves."""
    moves = generate_moves(board, player)
    print(f"\nMoves available for {player}: {len(moves)}")
    
    if len(moves) > 0:
        print("First 10 moves:")
        count = 0
        for move in moves:
            if move[0] != "pass":
                print(f" - {move}")
                count += 1
                if count >= 10:
                    break
    
    # Check frozen pieces
    print("\nFrozen pieces:")
    frozen_count = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece != " " and piece[0] == player[0]:
                if is_frozen(board, row, col):
                    print(f" - {piece} at ({row}, {col}) is FROZEN")
                    frozen_count += 1
    
    if frozen_count == 0:
        print(" - None")
    
    return moves

def generate_moves(board, current_turn, move_count=0):
    """Generate all possible moves for the current player."""
    moves = []
    
    # Only generate moves if we haven't used all 4 moves
    if move_count < 4:
        # Generate regular moves
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece != " " and piece[0] == current_turn[0]:
                    # Check normal moves
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_row = row + dr
                        new_col = col + dc
                        if can_move(board, row, col, new_row, new_col):
                            moves.append((row, col, new_row, new_col, "move"))
                    
                    # Push/pull moves - require 2 moves so only if < 3 moves used
                    if move_count < 3:
                        # Check for adjacent enemy pieces that can be pushed/pulled
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            adj_row = row + dr
                            adj_col = col + dc
                            if can_push_pull(board, row, col, adj_row, adj_col):
                                # Try push directions
                                for pdr, pdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                    push_row = adj_row + pdr
                                    push_col = adj_col + pdc
                                    if 0 <= push_row < BOARD_SIZE and 0 <= push_col < BOARD_SIZE:
                                        if board[push_row][push_col] == " ":
                                            # Check if push would create a trap capture
                                            temp_board = [row[:] for row in board]
                                            temp_board[push_row][push_col] = temp_board[adj_row][adj_col]
                                            temp_board[adj_row][adj_col] = temp_board[row][col]
                                            temp_board[row][col] = " "
                                            check_traps(temp_board)
                                            
                                            # If push would capture a piece, prioritize it
                                            if temp_board[push_row][push_col] == " ":
                                                moves.append((row, col, adj_row, adj_col, "push", pdr, pdc))
                                            else:
                                                # Add with higher priority
                                                moves.append((row, col, adj_row, adj_col, "push", pdr, pdc))
                                
                                # Try pull directions
                                for pdr, pdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                    # Skip direction toward the enemy piece
                                    if pdr == dr and pdc == dc:
                                        continue
                                    
                                    pull_row = row + pdr
                                    pull_col = col + pdc
                                    if 0 <= pull_row < BOARD_SIZE and 0 <= pull_col < BOARD_SIZE:
                                        if board[pull_row][pull_col] == " ":
                                            # Check if pull would create a trap capture
                                            temp_board = [row[:] for row in board]
                                            temp_board[pull_row][pull_col] = temp_board[row][col]
                                            temp_board[row][col] = temp_board[adj_row][adj_col]
                                            temp_board[adj_row][adj_col] = " "
                                            check_traps(temp_board)
                                            
                                            # If pull would capture a piece, prioritize it
                                            if temp_board[row][col] == " ":
                                                moves.append((row, col, adj_row, adj_col, "pull", pdr, pdc))
                                            else:
                                                # Add with higher priority
                                                moves.append((row, col, adj_row, adj_col, "pull", pdr, pdc))
        
        # Add "pass" move if at least one move was made
        if move_count >= 1:
            moves.append(("pass", None, None, None, None))
    
    # Debug information
    if len(moves) == 0:
        print(f"WARNING: No valid moves generated for {current_turn}")
    
    return moves

def make_move(board, move):
    """Apply a move to the board and return the new board."""
    if move[0] == "pass":
        return [row[:] for row in board]  # Return a copy of the board
    
    # Create a copy of the board to modify
    new_board = [row[:] for row in board]
    
    if move[4] == "move":
        start_row, start_col, end_row, end_col, _ = move
        new_board[end_row][end_col] = new_board[start_row][start_col]
        new_board[start_row][start_col] = " "
    
    elif move[4] == "push":
        start_row, start_col, end_row, end_col, _, dir_row, dir_col = move
        push_row, push_col = end_row + dir_row, end_col + dir_col
        
        # Move the opponent's piece first
        new_board[push_row][push_col] = new_board[end_row][end_col]
        # Then move our piece to opponent's previous spot
        new_board[end_row][end_col] = new_board[start_row][start_col]
        # Empty our original position
        new_board[start_row][start_col] = " "
    
    elif move[4] == "pull":
        start_row, start_col, end_row, end_col, _, dir_row, dir_col = move
        pull_row, pull_col = start_row + dir_row, start_col + dir_col
        
        # Move our piece first
        new_board[pull_row][pull_col] = new_board[start_row][start_col]
        # Then move opponent's piece to our original spot
        new_board[start_row][start_col] = new_board[end_row][end_col]
        # Empty opponent's original position
        new_board[end_row][end_col] = " "
    
    # Check traps after any move
    check_traps(new_board)
    
    return new_board

def board_to_string(board):
    """Convert a board to a string representation for loop detection."""
    return "".join("".join(row) for row in board)

def is_loop_detected(board_history):
    """Check if the current board state has appeared multiple times."""
    if len(board_history) < 6:
        return False
    
    # Get the last board state
    last_state = board_history[-1]
    
    # Count occurrences of this board state in history
    occurrences = sum(1 for state in board_history if state == last_state)
    
    # If this board state has appeared 3+ times, it's a loop
    return occurrences >= 3

def add_to_history(board):
    """Add the current board state to history."""
    global move_history
    board_str = board_to_string(board)
    move_history.append(board_str)
    # Keep only the last max_history_length states
    if len(move_history) > max_history_length:
        move_history.pop(0)

def handle_ai_turn():
    """Handle the AI's turn (up to 4 moves)."""
    global whose_turn, move_count, game_finished, board, move_history
    
    # Print debug info
    print(f"\n{whose_turn}'s turn (move {move_count}/4):")
    debug_moves(board, whose_turn)
    
    # Check if game is already finished
    if check_winner(board):
        return
    
    # Track board states to detect loops
    board_str = board_to_string(board)
    if board_str not in move_history:
        move_history.append(board_str)
        if len(move_history) > max_history_length:
            move_history.pop(0)
    
    # Check for loops in game
    if is_loop_detected(move_history):
        print("Loop detected! Introducing randomness in move selection.")
        # Reset history to break the loop
        move_history = []
    
    # Get the AI's move (Gold = Minimax, Silver = Heuristic)
    if whose_turn == "Gold":
        best_move = get_best_move(board, "Gold")
    else:
        best_move = find_best_move_heuristic(board)
    
    # If no valid move or pass, end turn
    if best_move is None or best_move[0] == "pass":
        print(f"{whose_turn} passes their turn")
        move_count = 4  # Force end of turn
    else:
        # Apply the move
        print(f"{whose_turn} makes move: {best_move}")
        board = make_move(board, best_move)
        move_count += 1
        
        # Check if game is over after the move
        if check_winner(board):
            return
    
    # Check if turn is over (all 4 moves used)
    if move_count >= 4:
        move_count = 0
        whose_turn = "Silver" if whose_turn == "Gold" else "Gold"
        
        # Check if game is over
        check_winner(board)

def minimax(board, depth, alpha, beta, maximizing_player, current_turn):
    """Minimax algorithm with alpha-beta pruning."""
    # Base case: depth limit reached or terminal node
    if depth == 0 or check_winner(board):
        return heuristic(board, add_noise=(depth == 0)), None
    
    # Generate all possible moves
    moves = generate_moves(board, current_turn)
    
    # No valid moves
    if not moves:
        return heuristic(board), None
    
    # Shuffle moves for more variety when scores are equal
    random.shuffle(moves)                                                                          ################## Anchor
    
    if maximizing_player == current_turn:  # (maximizing)                                           ############## Anchor
        max_eval = float('-inf')
        best_move = None
        
        for move in moves:
            # Make the move
            new_board = make_move(board, move)
            
            # Recursively evaluate
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, "Gold")
            
            # Update best move if this is better
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            # Alpha-beta pruning
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        return max_eval, best_move
    
    else:  # Gold's turn (minimizing)
        min_eval = float('inf')
        best_move = None
        
        for move in moves:
            # Make the move
            new_board = make_move(board, move)
            
            # Recursively evaluate
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, "Silver")
            
            # Update best move if this is better
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            # Alpha-beta pruning
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
        return min_eval, best_move

def get_best_move(board, current_turn):
    """Find the best move using minimax with alpha-beta pruning."""
    # Get all available moves
    moves = generate_moves(board, current_turn)
    
    # If no valid moves or only pass, return None or pass
    if len(moves) <= 1:
        return None if len(moves) == 0 else moves[0]
    
    # Filter out pass move unless it's the only option
    non_pass_moves = [m for m in moves if m[0] != "pass"]
    if len(non_pass_moves) == 0:
        return moves[0]  # Only pass move available
    
    # If loop is detected, choose a random move
    if is_loop_detected([board_to_string(board)]):
        print("Loop detected in minimax - choosing random move")
        return random.choice(non_pass_moves)
    
    # Adjust search depth based on game complexity
    piece_count = sum(1 for row in board for piece in row if piece != " ")
    depth = 2
    
    # Deeper search for endgame positions with fewer pieces
    if piece_count < 10:
        depth = 3
    
    start_time = time.time()
    score, best_move = minimax(board, depth, float('-inf'), float('inf'), current_turn == "Silver", current_turn)
    end_time = time.time()
    
    print(f"Minimax search (depth {depth}) took {end_time - start_time:.2f} seconds, score: {score}")
    
    # If minimax fails to find a move or returns pass, pick a random non-pass move
    if best_move is None or best_move[0] == "pass":
        if len(non_pass_moves) > 0:
            print("Minimax defaulting to random non-pass move")
            best_move = random.choice(non_pass_moves)
    
    return best_move

def find_best_move_heuristic(board):
    """Find the best move using a simple heuristic evaluation."""
    # Get all available moves
    moves = generate_moves(board, "Silver")
    
    # If no valid moves, return None
    if len(moves) <= 1:  # Only pass or no moves
        return None if len(moves) == 0 else moves[0]
    
    # Filter out pass move unless it's the only option
    non_pass_moves = [m for m in moves if m[0] != "pass"]
    if len(non_pass_moves) == 0:
        return moves[0]  # Only pass move available
    
    # If loop is detected, choose a random move
    if is_loop_detected([board_to_string(board)]):
        print("Loop detected in heuristic - choosing random move")
        return random.choice(non_pass_moves)
    
    # Group moves by score for random selection among equal scores
    move_scores = {}
    
    # Evaluate each move
    for move in non_pass_moves:
        # Make the move
        new_board = make_move(board, move)
        
        # Evaluate position with some noise for variety
        score = heuristic(new_board, add_noise=True)
        
        # Store by score
        if score not in move_scores:
            move_scores[score] = []
        move_scores[score].append(move)
    
    # Find the best score (highest for Silver)
    best_score = max(move_scores.keys())
    
    # Choose randomly from the moves with the best score
    best_move = random.choice(move_scores[best_score])
    print(f"Heuristic selected move with score {best_score}")
    
    return best_move

def main():
    """Main game loop."""
    global whose_turn, move_count, game_finished, board, move_history
    
    # For debugging: print initial state
    print("\n=== Starting Arimaa AI vs AI game ===")
    print("Gold = Minimax AI, Silver = Heuristic AI")
    
    running = True
    clock = pygame.time.Clock()
    
    # Initialize turn counter for display
    turn_counter = 1
    
    # Add a delay between turns for better visualization
    turn_delay = 1000  # 1 second delay between turns
    
    # Flag to control when to process the next turn
    next_turn_ready = True
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Spacebar to advance turns quickly
                elif event.key == pygame.K_SPACE and not game_finished:
                    next_turn_ready = True
                # R key to restart the game
                elif event.key == pygame.K_r:
                    # Reset game state
                    board = [
                        ["SE", "SH", "ST", "SC", "SE", "SC", "SH", "SD"],
                        ["SR", "SR", "SR", "SR", "SR", "SR", "SR", "SR"],
                        [" ", " ", " ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " ", " ", " "],
                        ["GR", "GR", "GR", "GR", "GR", "GR", "GR", "GR"],
                        ["GD", "GH", "GT", "GE", "GE", "GC", "GH", "GD"]
                    ]
                    whose_turn = "Gold"
                    move_count = 0
                    game_finished = False
                    turn_counter = 1
                    move_history = []
                    next_turn_ready = True
                    print("\n=== Game restarted ===")
        
        # Clear screen and draw board
        screen.fill((0, 0, 0))
        draw_board()
        
        # AI gameplay
        if not game_finished and next_turn_ready:
            next_turn_ready = False  # Mark turn as in progress
            
            # Track whose turn it was
            current_turn = whose_turn
            
            # Let the AI play its turn
            handle_ai_turn()
            
            # If the turn changed, increment counter
            if whose_turn != current_turn:
                turn_counter += 1
                # Add delay between turns for better visualization
                pygame.time.delay(turn_delay)
            
            # Mark next turn as ready
            next_turn_ready = True
            
            # If we've been playing for a long time with no winner (200+ turns), declare a draw
            if turn_counter > 200:
                print("Game ended in a draw after 200 turns")
                game_finished = True
        
        # Game over display
        if game_finished:
            # Draw a centered game over message
            font = pygame.font.SysFont('Arial', 36)
            if turn_counter > 200:
                message = "Game ended in a draw!"
            else:
                message = f"{whose_turn} wins!"
            
            text = font.render(message, True, (255, 255, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
            
            # Draw a background for the text
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(30)
    
    # Clean up
    pygame.quit()
    print("\n=== Game ended ===")
    if game_finished:
        if turn_counter > 200:
            print("Game ended in a draw")
        else:
            print(f"Winner: {whose_turn}")
    else:
        print("Game closed without finishing")

# Start the game
if __name__ == "__main__":
    main()