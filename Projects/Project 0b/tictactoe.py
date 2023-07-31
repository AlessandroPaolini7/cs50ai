"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Count the number of X's and O's on the board
    x_count = 0
    o_count = 0
    for row in board:
        for col in row:
            if col == X:
                x_count += 1
            elif col == O:
                o_count += 1
    # If there are more X's than O's, then it's O's turn
    if x_count > o_count:
        return O
    # If there are more O's than X's, then it's X's turn
    elif o_count > x_count:
        return X
    # If there are the same number of X's and O's, then it's X's turn
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            # If the current cell is empty, then it's a possible action
            if board[i][j] == EMPTY:
                possible_actions.add((i,j))
    # Return the set of possible actions
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # If the action is not in the set of possible actions, raise an exception
    if action not in actions(board):
        raise Exception("Invalid action")
    # If the action is in the set of possible actions, then make the move
    else:
        current_player = player(board)
        # Get the row and column of the action
        row = action[0]
        col = action[1]
        # Make a deep copy of the board
        new_board = copy.deepcopy(board)
        # Make the move
        new_board[row][col] = current_player
        # Return the new board
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check the rows
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]
    # Check the columns
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    # Check the diagonals
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    # If there is no winner, return None
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    # If there are no more possible actions, then the game is over
    if len(actions(board)) == 0:
        return True
    # If there is no winner and there are still possible actions, then the game is not over
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
            return 1
    if winner(board) == O:
            return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    # If the game is over, return None
    if terminal(board):
        return None
    
    # If it's X's turn, then maximize the score
    if player(board) == X:
        # Set the initial score to -infinity
        score = -math.inf
        # Set the initial action to None
        best_action = None
        # For each possible action
        for action in actions(board):
            # Get the minimum score of the resulting board
            min_score = min_value(result(board,action))
            # If the minimum score is greater than the current score
            if min_score > score:
                # Update the score
                score = min_score
                # Update the best action
                best_action = action
        # Return the best action
        return best_action
    
    # If it's O's turn, then minimize the score
    if player(board) == O:
        # Set the initial score to infinity
        score = math.inf
        # Set the initial action to None
        best_action = None
        # For each possible action
        for action in actions(board):
            # Get the maximum score of the resulting board
            max_score = max_value(result(board,action))
            # If the maximum score is less than the current score
            if max_score < score:
                # Update the score
                score = max_score
                # Update the best action
                best_action = action
        # Return the best action
        return best_action
    
def max_value(board):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v