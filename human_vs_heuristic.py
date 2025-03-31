import pygame
import os
import random

# Set up the game window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
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
    ["SE", "SH", "SD", "SD", "SCT", "SCT", "SH", "SC"],
    ["SR", "SR", "SR", "SR", "SR", "SR", "SR", "SR"],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    ["GR", "GR", "GR", "GR", "GR", "GR", "GR", "GR"],
    ["GE", "GH", "GD", "GD", "GCT", "GCT", "GH", "GC"]
]

PIECE_IMAGES = {
    'GE': 'gold_elephant.png',
    'GC': 'gold_camel.png',
    'GH': 'gold_horse.png',
    'GD': 'gold_dog.png',
    'GCT': 'gold_cat.png',
    'GR': 'gold_rabbit.png',
    'SE': 'silver_elephant.png',
    'SC': 'silver_camel.png',
    'SH': 'silver_horse.png',
    'SD': 'silver_dog.png',
    'SCT': 'silver_cat.png',
    'SR': 'silver_rabbit.png'
}


# Piece strengths (higher number = stronger piece)
piece_strength = {
    "GE": 5, "GC": 4, "GH": 3, "GD": 2, "GCT": 1, "GR": 0,
    "SE": 5, "SC": 4, "SH": 3, "SD": 2, "SCT": 1, "SR": 0,
    " ": -1  # Empty space
}
def load_images():
    images = {}
    for piece, filename in PIECE_IMAGES.items():
        path = os.path.join(os.getcwd(), filename) #gets the path to the proper image
        images[piece] = pygame.image.load(path)
        images[piece] = pygame.transform.scale(images[piece], (CELL_SIZE - 10, CELL_SIZE - 10)) #scale
    return images

# Start the game
pygame.init()
piece_images = load_images()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Arimaa")

# Game variables
selected = None  # What's clicked: None, (row, col), or ((r1, c1), (r2, c2))
whose_turn = "Gold"  # Whose turn it is
move_count = 0  # How many moves made this turn
game_finished = False  # Is the game over?

# Draw the game board
def draw_board():
    # Loop through each square
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Set color: light or dark checkerboard pattern
            if (row + col) % 2 == 0:
                color = LIGHT_COLOR
            else:
                color = DARK_COLOR
            
            # Traps get a special color
            if (row, col) in TRAPS:
                color = TRAP_COLOR

            # Highlight selected squares if game isn't over
            if selected and not game_finished:
                # Single piece selected
                if type(selected) == tuple and len(selected) == 2 and type(selected[0]) == int:
                    if (row, col) == selected:
                        color = HIGHLIGHT_COLOR
                # Two pieces selected for push/pull
                elif type(selected) == tuple and len(selected) == 2 and type(selected[0]) == tuple:
                    if (row, col) == selected[0] or (row, col) == selected[1]:
                        color = HIGHLIGHT_COLOR
            
            # Draw the square
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            # Draw the piece (just text for simplicity)
            piece = board[row][col]
            if piece in piece_images:
                img_rect = piece_images[piece].get_rect(center=(col * CELL_SIZE + CELL_SIZE / 2, row * CELL_SIZE + CELL_SIZE / 2))
                screen.blit(piece_images[piece], img_rect)
    # Show win message if game is over
    if game_finished:
        font = pygame.font.Font(None, 48)
        win_message = f"{whose_turn} Wins!"
        text = font.render(win_message, True, (255, 255, 255))
        text_pos = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        pygame.draw.rect(screen, (0, 0, 0), text_pos.inflate(20, 20))  # Black background
        screen.blit(text, text_pos)

# Check if a piece can't move (frozen by stronger enemy)
def is_frozen(row, col, board):
    piece = board[row][col]
    if piece == " ":
        return False
    
    frozen = False
    has_friend = False
    
    # Check all 4 directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dir_row, dir_col in directions:
        new_row = row + dir_row
        new_col = col + dir_col
        # Make sure we're still on the board
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            nearby_piece = board[new_row][new_col]
            if nearby_piece != " ":
                # Friend nearby (same team)?
                if nearby_piece[0] == piece[0]:
                    has_friend = True
                # Stronger enemy nearby?
                elif piece_strength[piece] < piece_strength[nearby_piece]:
                    frozen = True
    
    # Frozen only if there's a stronger enemy and no friends
    return frozen and not has_friend

# Check if a move is allowed (one step, not frozen)
def can_move(start_row, start_col, end_row, end_col, board = board):
    # Must be on the board and to an empty space
    if not (0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE):
        return False
    if board[end_row][end_col] != " " or is_frozen(start_row, start_col, board):
        return False
    
    piece = board[start_row][start_col]
    row_change = start_row - end_row
    col_change = abs(start_col - end_col)
    
    # Must move exactly one step
    if abs(row_change) + col_change != 1:
        return False
    
    # Rabbits have special rules
    if piece == "GR":  # Gold rabbit: backward or sideways
        return row_change == 1 or col_change == 1
    if piece == "SR":  # Silver rabbit: forward or sideways
        return row_change == -1 or col_change == 1
    return True

# Check if push or pull is allowed
def can_push_or_pull(start_row, start_col, end_row, end_col, board = board):
    if 0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8:
        piece = board[start_row][start_col]
        target = board[end_row][end_col]
    else:
        return False
    
    # Must be next to each other
    if abs(start_row - end_row) + abs(start_col - end_col) != 1:
        return False
    
    # Gold pushing/pulling Silver, or Silver pushing/pulling Gold
    if piece[0] == "G" and target[0] == "S" and piece_strength[piece] > piece_strength[target]:
        return True
    if piece[0] == "S" and target[0] == "G" and piece_strength[piece] > piece_strength[target]:
        return True
    return False

# Push a piece (move both pieces)
def push(start_row, start_col, end_row, end_col, dir_row, dir_col, board = board):
    global move_count
    new_row = end_row + dir_row
    new_col = end_col + dir_col

    # Check if the new spot is on the board and empty
    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
        return False  # Can't push out of bounds
    if is_frozen(start_row, start_col, board) or board[new_row][new_col] != " ":
        return False  # Destination must be empty

    # Ensure the pusher is stronger than the pushed piece
    if piece_strength[board[start_row][start_col]] <= piece_strength[board[end_row][end_col]]:
        return False  

    # Move the pushed piece
    board[new_row][new_col] = board[end_row][end_col]
    # Move the pusher to the pushed piece's old spot
    board[end_row][end_col] = board[start_row][start_col]
    # Empty the pusher's original spot
    board[start_row][start_col] = " "

    move_count += 2
    return True

#Pull a piece (move both pieces)
def pull(start_row, start_col, end_row, end_col, dir_row, dir_col, board = board):
    global move_count
    new_row = start_row + dir_row  # The puller moves in the opposite direction of the pull
    new_col = start_col + dir_col
    
    # Check if the new spot is on the board and empty
    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
        return False
    if is_frozen(start_row, start_col, board) or board[new_row][new_col] != " ":
        return False
    
    if piece_strength[board[start_row][start_col]] <= piece_strength[board[end_row][end_col]]:
        return False

    # Move the pieces
    board[new_row][new_col] = board[start_row][start_col]  # Puller moves
    board[start_row][start_col] = board[end_row][end_col]  # Pulled piece moves
    board[end_row][end_col] = " "  # Old spot is empty

    move_count += 2
    return True


# Check if a piece in a trap should be removed
def check_traps(board = board):
    for trap_row, trap_col in TRAPS:
        piece = board[trap_row][trap_col]
        if piece == " ":
            continue
        
        # Look around the trap
        has_friend = False
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dir_row, dir_col in directions:
            new_row = trap_row + dir_row
            new_col = trap_col + dir_col
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                nearby_piece = board[new_row][new_col]
                if nearby_piece != " " and nearby_piece[0] == piece[0]:
                    has_friend = True
                    print("yay")
                    break
        
        # No friend nearby? Remove the piece
        if not has_friend:
            print("aww")
            board[trap_row][trap_col] = " "

# Check if someone won (rabbit reached the other side)
def check_winner(board = board):
    global game_finished, whose_turn
    gr_count = 0
    sr_count = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'GR':
                gr_count += 1
            if board[row][col] == 'SR':
                sr_count += 1
    if gr_count == 0:
        whose_turn = 'Silver'
        game_finished = True
        return True
    
    elif sr_count == 0:
        whose_turn = 'Gold'
        game_finished = True
        return True

    # Gold wins if a rabbit reaches row 0
    for col in range(BOARD_SIZE):
        if board[0][col] == "GR":
            whose_turn = "Gold"
            game_finished = True
            return True
    # Silver wins if a rabbit reaches row 7
    for col in range(BOARD_SIZE):
        if board[7][col] == "SR":
            whose_turn = "Silver"
            game_finished = True
            return True
    return False




def handle_push_pull(start, end, click, board = board):
    sr, sc = start
    er, ec = end
    r, c = click
    success = False
    if((abs(sr-r) + abs(sc-c) < abs(er-r) + abs(ec-c)) and (abs(sr-r)+abs(sc-c)==1)):
        dr = r - sr
        dc = c - sc

        success = pull(sr,sc,er,ec,dr,dc)
    elif((abs(sr-r) + abs(sc-c) > abs(er-r) + abs(ec-c)) and (abs(er-r)+abs(ec-c)==1)):
        dr = r - er
        dc = c - ec
        
        success = push(sr,sc,er,ec,dr,dc)
    return success

def heuristic(board):
    
    h = 0
    
    # each piece type has a value
    piece_values = {
        'SE': 100, 'SC': 50, 'SH': 30, 'SD': 20, 'SCT': 10, 'SR': 10,
        'GE': -100, 'GC': -50, 'GH': -30, 'GD': -20, 'GCT': -10, 'GR': -10,
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
                # Exponential reward for advancement (7^2=49, 6^2=36, 5^2=25, etc.)
                h += (row + 1) ** 2
                # Extra bonus for being close to the goal row
                if row == 7:
                    h = float('inf')
                elif row >= 6:  # One step away from winning
                    h += 200
                elif row >= 5:  # Two steps away
                    h += 100
                
            elif piece == 'GR':
                # Penalize Gold rabbit advancement
                h -= (8 - row) ** 2
                if row == 0:
                    h = -float('inf')
    
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
    
    # Trap control - reward controlling squares adjacent to traps
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
        
        # Reward for trap control (more friendly pieces than enemy pieces)
        if silver_adjacent > gold_adjacent:
            h += 15 * (silver_adjacent - gold_adjacent)
        elif gold_adjacent > silver_adjacent:
            h -= 15 * (gold_adjacent - silver_adjacent)
        
        # Extra penalty for having a piece in a trap with no friendly support
        piece_in_trap = board[trap_row][trap_col]
        if piece_in_trap.startswith('S') and silver_adjacent == 0:
            h -= 50  # Severe penalty for unsupported piece in trap
        elif piece_in_trap.startswith('G') and gold_adjacent == 0:
            h += 50  # Reward for enemy piece about to be captured
    
    # Piece mobility - reward having more available moves
    silver_mobility = 0
    gold_mobility = 0
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == " ":
                continue
                
            # Count possible moves for this piece
            moves = 0
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == " ":
                    # Check rabbit movement restrictions
                    if piece == "SR" and dr == 1:  # Silver rabbit can't move backward
                        continue
                    if piece == "GR" and dr == -1:  # Gold rabbit can't move backward
                        continue
                    
                    # Check if piece is frozen
                    if not is_frozen(row, col, board):
                        moves += 1
            
            # Add to team's mobility score
            if piece.startswith('S'):
                silver_mobility += moves
            elif piece.startswith('G'):
                gold_mobility += moves
    
    # Reward having more mobility than opponent
    h += (silver_mobility - gold_mobility) * 2
    
    # Elephant positioning - reward Silver elephant for being in useful positions
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'SE':
                # Reward elephant for being near center
                center_dist = abs(row - 3.5) + abs(col - 3.5)
                h += (7 - center_dist) * 3
                
                # Reward elephant for being near enemy pieces (to push/pull them)
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        r, c = row + dr, col + dc
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                            if board[r][c].startswith('G'):
                                h += 5 / (abs(dr) + abs(dc) + 1)  # Closer is better
            
            # Penalize Gold elephant for being in useful positions
            elif board[row][col] == 'GE':
                center_dist = abs(row - 3.5) + abs(col - 3.5)
                h -= (7 - center_dist) * 3
    
    # Formation and structure - reward pieces for supporting each other
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece.startswith('S'):
                # Count friendly neighbors
                friends = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c].startswith('S'):
                            friends += 1
                
                # Reward for having friendly pieces nearby (better formation)
                h += friends * 2
            
            elif piece.startswith('G'):
                # Count friendly neighbors for Gold
                friends = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c].startswith('G'):
                            friends += 1
                
                # Penalize Gold for having good formation
                h -= friends * 2
    
    return h

def find_best_move(current_board):
    best_move = None
    best_h = heuristic(current_board)
    global move_count
    
    # Keep track of ANY valid move as a fallback
    fallback_move = None
    
    # Create a deep copy of the board for simulation
    board_copy = [row[:] for row in current_board]
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board_copy[row][col]
            if piece.startswith("S"):
                # Check regular moves
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_row = row + dr
                    adj_col = col + dc
                    
                    if can_move(row, col, adj_row, adj_col, board_copy):
                        # Save the first valid move as a fallback
                        if fallback_move is None:
                            fallback_move = (row, col, adj_row, adj_col, "move")
                        
                        # Test the move
                        test_board = [r[:] for r in board_copy]
                        test_board[adj_row][adj_col] = piece
                        test_board[row][col] = ' '
                        
                        # Simulate trap effects
                        for trap_row, trap_col in TRAPS:
                            trap_piece = test_board[trap_row][trap_col]
                            if trap_piece == " ":
                                continue
                            
                            has_friend = False
                            for tdr, tdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                tr, tc = trap_row + tdr, trap_col + tdc
                                if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE:
                                    if test_board[tr][tc] != " " and test_board[tr][tc][0] == trap_piece[0]:
                                        has_friend = True
                                        break
                            
                            if not has_friend:
                                test_board[trap_row][trap_col] = " "
                        
                        h = heuristic(test_board)
                        if h > best_h:
                            best_h = h
                            best_move = (row, col, adj_row, adj_col, "move")
                
                # Check push/pull moves
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_row = row + dr
                    adj_col = col + dc
                    
                    if move_count < 3 and can_push_or_pull(row, col, adj_row, adj_col, board_copy):
                        # Try all possible push directions
                        for pdr, pdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            push_row = adj_row + pdr
                            push_col = adj_col + pdc
                            
                            if 0 <= push_row < BOARD_SIZE and 0 <= push_col < BOARD_SIZE and board_copy[push_row][push_col] == " ":
                                # Simulate push
                                test_board = [r[:] for r in board_copy]
                                test_board[push_row][push_col] = test_board[adj_row][adj_col]  # Move pushed piece
                                test_board[adj_row][adj_col] = test_board[row][col]  # Move pusher
                                test_board[row][col] = " "  # Empty original spot
                                
                                # Simulate trap effects
                                for trap_row, trap_col in TRAPS:
                                    trap_piece = test_board[trap_row][trap_col]
                                    if trap_piece == " ":
                                        continue
                                    
                                    has_friend = False
                                    for tdr, tdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                        tr, tc = trap_row + tdr, trap_col + tdc
                                        if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE:
                                            if test_board[tr][tc] != " " and test_board[tr][tc][0] == trap_piece[0]:
                                                has_friend = True
                                                break
                                    
                                    if not has_friend:
                                        test_board[trap_row][trap_col] = " "
                                
                                h = heuristic(test_board)
                                if h > best_h:
                                    best_h = h
                                    best_move = (row, col, adj_row, adj_col, "push", pdr, pdc)
                        
                        # Try all possible pull directions
                        for pdr, pdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            pull_row = row + pdr
                            pull_col = col + pdc
                            
                            if 0 <= pull_row < BOARD_SIZE and 0 <= pull_col < BOARD_SIZE and board_copy[pull_row][pull_col] == " ":
                                # Simulate pull
                                test_board = [r[:] for r in board_copy]
                                test_board[pull_row][pull_col] = test_board[row][col]  # Move puller
                                test_board[row][col] = test_board[adj_row][adj_col]  # Move pulled piece
                                test_board[adj_row][adj_col] = " "  # Empty pulled piece's spot
                                
                                # Simulate trap effects
                                for trap_row, trap_col in TRAPS:
                                    trap_piece = test_board[trap_row][trap_col]
                                    if trap_piece == " ":
                                        continue
                                    
                                    has_friend = False
                                    for tdr, tdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                        tr, tc = trap_row + tdr, trap_col + tdc
                                        if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE:
                                            if test_board[tr][tc] != " " and test_board[tr][tc][0] == trap_piece[0]:
                                                has_friend = True
                                                break
                                    
                                    if not has_friend:
                                        test_board[trap_row][trap_col] = " "
                                
                                h = heuristic(test_board)
                                if h > best_h:
                                    best_h = h
                                    best_move = (row, col, adj_row, adj_col, "pull", pdr, pdc)
    
    # If we found a better move, return it
    if best_move is not None:
        return best_move
    
    # Otherwise, return any valid move
    if fallback_move:
        return fallback_move
    
    # If no move is possible (very unlikely), return None
    return None

def handle_ai_turn():
    global whose_turn, move_count, game_finished
    
    # AI can make up to 4 moves per turn
    remaining_moves = 4 - move_count
    
    for _ in range(remaining_moves):
        if game_finished:
            break
            
        ai_move = find_best_move(board)
        if ai_move is None:
            print("AI couldn't find a valid move")
            break
        
        if ai_move[4] == "move":
            start_row, start_col, end_row, end_col, _ = ai_move
            piece = board[start_row][start_col]
            print(f"AI moves {piece} from {start_row},{start_col} to {end_row},{end_col}")
            
            # Execute the move
            board[end_row][end_col] = piece
            board[start_row][start_col] = ' '
            move_count += 1
            
        elif ai_move[4] == "push":
            start_row, start_col, end_row, end_col, _, dir_row, dir_col = ai_move
            pusher = board[start_row][start_col]
            pushed = board[end_row][end_col]
            push_to_row, push_to_col = end_row + dir_row, end_col + dir_col
            
            print(f"AI pushes {pushed} at {end_row},{end_col} to {push_to_row},{push_to_col} with {pusher}")
            
            # Execute the push
            board[push_to_row][push_to_col] = pushed
            board[end_row][end_col] = pusher
            board[start_row][start_col] = ' '
            move_count += 2
            
        elif ai_move[4] == "pull":
            start_row, start_col, end_row, end_col, _, dir_row, dir_col = ai_move
            puller = board[start_row][start_col]
            pulled = board[end_row][end_col]
            puller_to_row, puller_to_col = start_row + dir_row, start_col + dir_col
            
            print(f"AI pulls {pulled} from {end_row},{end_col} to {start_row},{start_col} while moving {puller} to {puller_to_row},{puller_to_col}")
            
            # Execute the pull
            board[puller_to_row][puller_to_col] = puller
            board[start_row][start_col] = pulled
            board[end_row][end_col] = ' '
            move_count += 2
        
        # Check if pieces should be removed from traps
        check_traps()
        
        # Check if the game is over
        if check_winner():
            break
        
        # Check if we've used all our moves
        if move_count >= 4:
            break
    
    # End AI turn and give control back to player
    print("AI turn complete")
    whose_turn = "Gold"
    move_count = 0

def handle_click(x, y, button, team):
    global selected, whose_turn, move_count, game_finished

    if whose_turn != team or game_finished:
        return

    col = x // CELL_SIZE
    row = y // CELL_SIZE

    if button == 1:  # Left click (Move / Push / Pull)
        if selected is None:
            # Select piece if it belongs to the current team
            if board[row][col] != " " and board[row][col][0] == team[0]:
                selected = (row, col)
        else:
            if isinstance(selected, tuple) and len(selected) == 2 and isinstance(selected[0], int):
                start_row, start_col = selected

                if (row, col) == (start_row, start_col):  # Deselect on re-click
                    selected = None
                elif can_move(start_row, start_col, row, col):  # Normal move
                    board[row][col], board[start_row][start_col] = board[start_row][start_col], " "
                    move_count += 1
                    check_traps()
                    selected = None
                    if check_winner():
                        return
                    if move_count >= 4:
                        whose_turn = "Silver"
                        move_count = 0
                        # AI's turn after player uses all 4 moves
                        handle_ai_turn()
                else:
                    selected = None
            
            elif isinstance(selected, tuple) and len(selected) == 2 and isinstance(selected[0], tuple):
                (start_row, start_col), (end_row, end_col) = selected 

                if (row, col) in [(start_row, start_col), (end_row, end_col)]:  # Deselect on re-click
                    selected = None
                else:
                    dir_row, dir_col = row - end_row, col - end_col
                    if can_push_or_pull(start_row, start_col, end_row, end_col) and move_count < 3:
                        success = handle_push_pull(selected[0], selected[1], (row, col))
                        if success:
                            check_traps()
                            selected = None
                            if check_winner():
                                return
                            if move_count >= 4:
                                whose_turn = "Silver"
                                move_count = 0
                                # AI's turn after player uses all 4 moves
                                handle_ai_turn()
                        else:
                            selected = None
                    else:
                        selected = None

    elif button == 3:  # Right click (Set up push/pull)
        if selected is None:
            if board[row][col] != " " and board[row][col][0] == team[0]:
                selected = (row, col)
        elif isinstance(selected, tuple) and len(selected) == 2 and isinstance(selected[0], int):
            start_row, start_col = selected

            if (row, col) == (start_row, start_col):  # Deselect on re-click
                selected = None
            elif can_push_or_pull(start_row, start_col, row, col):  # Set up push/pull
                selected = ((start_row, start_col), (row, col)) 
            else:
                selected = None

# Pass the turn to the other player
def pass_turn():
    global whose_turn, move_count, game_finished
    if move_count >= 1 and not game_finished:
        whose_turn = "Silver"
        move_count = 0
        selected = None
        # AI's turn after player passes
        handle_ai_turn()

# Main game loop
def main():
    running = True
    while running:
        # Clear the screen
        screen.fill((0, 0, 0))
        draw_board()
        pygame.display.flip()
        
        # Handle events (clicks, key presses)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_finished:
                x, y = event.pos
                button = event.button
                if whose_turn == "Gold":
                    handle_click(x, y, button, "Gold")
                # Silver is now handled by AI, so we don't process clicks for Silver
            elif event.type == pygame.KEYDOWN and not game_finished:
                if event.key == pygame.K_p:  # Press 'P' to pass
                    pass_turn()
        
        # If someone won, wait 2 seconds then quit
        if game_finished:
            pygame.display.flip()
            pygame.time.wait(2000)
            #running = False

    pygame.quit()

# Start the game
if __name__ == "__main__":
    main() # type: ignore