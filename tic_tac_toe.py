"""Improved Tic-Tac-Toe Game with Scoreboard and Better UI"""

import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


# Represents a player (symbol + display color)
class player(NamedTuple):
    label: str
    color: str


# Represents a move on the board
class Move(NamedTuple):
    row: int
    column: int
    label: str = ""


BOARD_SIZE = 3

# Default players
DEFAULT_PLAYERS = (
    player(label="X", color="#00ADB5"),
    player(label="O", color="#FF5722")
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        # Cycle is used to alternate players automatically
        self._players = cycle(players)
        self._board_size = board_size
        self.current_player = next(self._players)

        # Game state variables
        self.winner_combo = []
        self._has_winner = False
        self.winning_combos = []

        # Score tracking
        self.scores = {"X": 0, "O": 0, "Draw": 0}

        self._setup_board()

    def _setup_board(self):
        """Initialize an empty board and compute all winning combinations"""
        self._current_moves = [
            [Move(row, column) for column in range(self._board_size)]
            for row in range(self._board_size)
        ]
        self.winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        """Generate all possible winning patterns (rows, columns, diagonals)"""
        rows = [
            [(move.row, move.column) for move in row]
            for row in self._current_moves
        ]

        # Transpose rows to get columns
        columns = [list(column) for column in zip(*rows)]

        # Diagonal combinations
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [column[j] for j, column in enumerate(reversed(columns))]

        return rows + columns + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        """Check if a move is valid (cell is empty and no winner yet)"""
        return (
            not self._has_winner and
            self._current_moves[move.row][move.column].label == ""
        )

    def process_move(self, move):
        """Place the move on the board and check for a winner"""
        self._current_moves[move.row][move.column] = move

        # Check each possible winning combination
        for combo in self.winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )

            # A win occurs when all labels are same and not empty
            if len(results) == 1 and "" not in results:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        """Return True if the game has a winner"""
        return self._has_winner

    def is_tied(self):
        """Check if the board is full and no winner exists"""
        return not self._has_winner and all(
            move.label for row in self._current_moves for move in row
        )

    def toggle_player(self):
        """Switch to the next player"""
        self.current_player = next(self._players)

    def reset_game(self):
        """Reset board state for a new game (scores remain unchanged)"""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)

        self._has_winner = False
        self.winner_combo = []

        # Reset starting player
        self.current_player = next(self._players)


class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()

        self.title("Tic-Tac-Toe")
        self.geometry("400x500")
        self.configure(bg="#222831")

        # Stores button → (row, col) mapping
        self._cells = {}
        self._game = game

        self._create_menu()
        self._create_scoreboard()
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        """Create menu with reset and exit options"""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_command(label="Exit", command=quit)

        menu_bar.add_cascade(label="Menu", menu=file_menu)

    def _create_scoreboard(self):
        """Create scoreboard display"""
        self.score_label = tk.Label(
            self,
            text="X: 0 | O: 0 | Draw: 0",
            font=font.Font(size=14, weight="bold"),
            bg="#222831",
            fg="white"
        )
        self.score_label.pack(pady=5)

    def update_scoreboard(self):
        """Update scoreboard values on screen"""
        s = self._game.scores
        self.score_label.config(
            text=f"X: {s['X']} | O: {s['O']} | Draw: {s['Draw']}"
        )

    def _update_button(self, btn):
        """Display current player's symbol on clicked button"""
        btn.config(
            text=self._game.current_player.label,
            fg=self._game.current_player.color
        )

    def _update_display(self, msg, color="white"):
        """Update the status message at the top"""
        self.display.config(text=msg, fg=color)

    def _highlight_cells(self):
        """Highlight the winning combination cells"""
        for btn, pos in self._cells.items():
            if pos in self._game.winner_combo:
                btn.config(bg="#FFD369")

    def play(self, event):
        """Handle user click event on a cell"""
        btn = event.widget
        row, col = self._cells[btn]

        move = Move(row, col, self._game.current_player.label)

        if self._game.is_valid_move(move):
            self._update_button(btn)
            self._game.process_move(move)

            if self._game.has_winner():
                self._highlight_cells()

                # Update score for winner
                self._game.scores[self._game.current_player.label] += 1
                self.update_scoreboard()

                self._update_display(
                    f"Player {self._game.current_player.label} wins",
                    self._game.current_player.color
                )

            elif self._game.is_tied():
                # Update draw score
                self._game.scores["Draw"] += 1
                self.update_scoreboard()

                self._update_display("Game is tied", "red")

            else:
                # Continue game
                self._game.toggle_player()
                self._update_display(
                    f"{self._game.current_player.label}'s turn"
                )

    def _create_board_display(self):
        """Create the top status label"""
        frame = tk.Frame(self, bg="#222831")
        frame.pack()

        self.display = tk.Label(
            frame,
            text="X's Turn",
            font=font.Font(size=20, weight="bold"),
            bg="#222831",
            fg="white"
        )
        self.display.pack(pady=10)

    def _create_board_grid(self):
        """Create the 3x3 button grid"""
        frame = tk.Frame(self, bg="#222831")
        frame.pack()

        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    frame,
                    text="",
                    font=font.Font(size=30, weight="bold"),
                    width=4,
                    height=2,
                    bg="#393E46",
                    fg="white",
                    relief="flat"
                )

                # Add hover effect
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#393E46"))

                # Bind click event
                btn.bind("<Button-1>", self.play)

                btn.grid(row=row, column=col, padx=5, pady=5)

                self._cells[btn] = (row, col)

    def reset_board(self):
        """Reset UI and game state for a new round"""
        self._game.reset_game()
        self._update_display("X's Turn")

        for btn in self._cells:
            btn.config(text="", bg="#393E46")


def main():
    """Application entry point"""
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()


if __name__ == "__main__":
    main()