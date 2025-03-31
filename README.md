# ARIMAA
Arimaa is a two-player strategy board game that was designed to be playable with a standard chess set and difficult for computers while still being easy to learn and fun to play for humans. 

#**<ins>Implementation</ins>**:
We have implemented 2 versions:\
(i) Human vs Minimax Algorithm\
(ii) Heuristic vs Minimax Algorithm\
(iii) Human vs Heuristic

#**<ins>Rules</ins>**:
Arimaa is played on an 8×8 board with four trap squares. There are six kinds of pieces, ranging from elephant (strongest) to rabbit (weakest). Stronger pieces can push or pull weaker pieces, and stronger pieces freeze weaker pieces. Pieces can be captured by dislodging them onto a trap square when they have no orthogonally adjacent friendly pieces.

The two players, Gold and Silver, each control sixteen pieces. These are, in order from strongest to weakest: one elephant, one camel, two horses, two dogs, two cats, and eight rabbits. These may be represented by the king, queen, rooks, bishops, knights, and pawns respectively when one plays using a chess set.

#**<ins>Objective</ins>**:
The main object of the game is to move a rabbit of one's own color onto the home rank of the opponent, which is known as a goal. Thus Gold wins by moving a gold rabbit to the eighth rank, and Silver wins by moving a silver rabbit to the first rank. However, because it is difficult to usher a rabbit to the goal line while the board is full of pieces, an intermediate objective is to capture opposing pieces by pushing them into the trap squares.

The game can also be won by capturing all of the opponent's rabbits (elimination) or by depriving the opponent of legal moves (immobilization). Compared to goal, these are uncommon.

#**<ins>Movement</ins>**:
After the pieces are placed on the board, the players alternate turns, starting with Gold. A turn consists of making one to four steps. With each step a piece may move into an unoccupied square one space left, right, forward, or backward, except that rabbits may not step backward. The steps of a turn may be made by a single piece or distributed among several pieces in any order.

A turn must make a net change to the position. Thus one cannot, for example, take one step forward and one step back with the same piece, effectively passing the turn and evading zugzwang. Furthermore, one's turn may not create the same position with the same player to move as has been created twice before. This rule is similar to the situational super ko rule in the game of Go, which prevents endless loops, and is in contrast to chess where endless loops are considered draws. The prohibitions on passing and repetition make Arimaa a drawless game.

#**<ins>Pushing and pulling</ins>**:
The second diagram, from the same game as the initial position above,[10] helps illustrate the remaining rules of movement.

A player may use two consecutive steps of a turn to dislodge an opposing piece with a stronger friendly piece which is adjacent in one of the four cardinal directions. For example, a player's dog may dislodge an opposing rabbit or cat, but not a dog, horse, camel, or elephant. The stronger piece may pull or push the adjacent weaker piece. When pulling, the stronger piece steps into an empty square, and the square it came from is occupied by the weaker piece. The silver elephant on d5 could step to d4 (or c5 or e5) and pull the gold horse from d6 to d5. When pushing, the weaker piece is moved to an adjacent empty square, and the square it came from is occupied by the stronger piece. The gold elephant on d3 could push the silver rabbit on d2 to e2 and then occupy d2. Note that the rabbit on d2 can't be pushed to d1, c2, or d3, because those squares are not empty.

Friendly pieces may not be dislodged. Also, a piece may not push and pull simultaneously. For example, the gold elephant on d3 could not simultaneously push the silver rabbit on d2 to e2 and pull the silver rabbit from c3 to d3. An elephant can never be dislodged, since there is nothing stronger.

#**<ins>Freezing</ins>**:
A piece which is adjacent in any cardinal direction to a stronger opposing piece is frozen, unless it is also adjacent to a friendly piece. Frozen pieces may not be moved by the owner, but may be dislodged by the opponent. A frozen piece can freeze another still weaker piece. The silver rabbit on a7 is frozen, but the one on d2 is able to move because it is adjacent to a silver piece. Similarly the gold rabbit on b7 is frozen, but the gold cat on c1 is not. The dogs on a6 and b6 do not freeze each other because they are of equal strength. An elephant cannot be frozen, since there is nothing stronger, but an elephant can be blockaded.

#**<ins>Capturing</ins>**:
A piece which enters a trap square is captured and removed from the game unless there is a friendly piece orthogonally adjacent. Silver could move to capture the gold horse on d6 by pushing it to c6 with the elephant on d5. A piece on a trap square is captured when all adjacent friendly pieces move away. Thus if the silver rabbit on c4 and the silver horse on c2 move away, voluntarily or by being dislodged, the silver rabbit on c3 will be captured.

Note that a piece may voluntarily step into a trap square, even if it is thereby captured. Also, the second step of a pulling maneuver is completed even if the piece doing the pulling is captured on the first step. For example, Silver could step the silver rabbit from f4 to g4 (so that it will no longer support pieces at f3), and then step the silver horse from f2 to f3, which captures the horse; the horse's move could still pull the gold rabbit from f1 to f2.

#**<ins>Results</ins>**:\
(i)For human vs minimax:\
![image](https://github.com/user-attachments/assets/63bdba0d-e944-4294-b797-bc5f33b0228e)\
![image](https://github.com/user-attachments/assets/ffc72c01-7c30-4059-8c8b-d9dc9f056754)\
![image](https://github.com/user-attachments/assets/dc42e110-ffc3-4270-8205-affdeb55d735)



(ii)For heuristic vs minimax:\
![WhatsApp Image 2025-03-31 at 18 03 45_66612f1a](https://github.com/user-attachments/assets/8d8a0757-b032-4d71-8471-55306e37cc00) \
![Screenshot_2025-03-31_181927 1](https://github.com/user-attachments/assets/97228eab-d552-4faa-bf55-13508547ec96)

