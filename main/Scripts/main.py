import sys
import os
import pygame
import constants as consts

class Window:

    def __init__(self) -> None:
        self.human_player = consts._playerX
        self.ai_player = consts._playerO
        self.players = [self.human_player, self.ai_player]

        self.difficulty_level = 1
        self.difficulty_map = {1: 1, 2: 4, 3: 6}

        pygame.init()
        self.screen = pygame.display.set_mode((consts.WIDTH, consts.HEIGHT))
        self.icon_path = os.path.join("main", "assets", "images", "ttt_icon.jpg")
        self.icon = pygame.image.load(self.icon_path)
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption("Tic Tac Toe Game")
        self.font = pygame.font.SysFont(None, 60)
        self.small_font = pygame.font.SysFont(None, 30)

        self.awaiting_ai = False
        self.ai_move_time = 0
        self.winner = None

        self.reset_game()

    def reset_game(self):
        if self.winner == self.human_player and self.difficulty_level < 3:
            self.difficulty_level += 1

        self.game_state = [[None for _ in range(3)] for _ in range(3)]
        self.players = [self.human_player, self.ai_player]
        self.game_end = False
        self.awaiting_ai = False
        self.ai_move_time = 0
        self.winner = None
        self.create_window()

    def change_difficulty(self) -> None:
        if self.difficulty_level < 3:
            self.difficulty_level += 1 
        elif self.difficulty_level == 3:
            self.difficulty_level = 1

    def create_window(self) -> None:
        self.screen.fill((185, 105, 200))

        for i in range(1, consts.ROWS):
            pygame.draw.line(self.screen, (255, 255, 255), (0, i * consts.CELL_SIZE), (consts.WIDTH, i * consts.CELL_SIZE), 3)

        for j in range(1, consts.COLS):
            pygame.draw.line(self.screen, (255, 255, 255), (j * consts.CELL_SIZE, 0), (j * consts.CELL_SIZE, consts.HEIGHT), 3)

        self.display_difficulty()

    def display_difficulty(self):
        text = self.small_font.render(f"Difficulty: {['Easy','Medium','Hard'][self.difficulty_level-1]}", True, (0, 0, 0))
        self.screen.blit(text, (10, consts.HEIGHT - 30))

    def mainloop(self) -> None:
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_1:
                        self.difficulty_level = 1
                        self.reset_game()
                    elif e.key == pygame.K_2:
                        self.difficulty_level = 2
                        self.reset_game()
                    elif e.key == pygame.K_3:
                        self.difficulty_level = 3
                        self.reset_game()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_end:
                        self.reset_game()
                    else:
                        if self.players[0] == self.human_player:
                            self.play_game()

            if not self.game_end and self.players[0] == self.ai_player and self.awaiting_ai:
                current_time = pygame.time.get_ticks()
                if current_time - self.ai_move_time >= 1500:
                    self.ai_move()
                    self.awaiting_ai = False

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def get_turn(self):
        self.players = self.players[::-1]
        return self.players[0]

    def play_game(self) -> None:
        mouse_position = pygame.mouse.get_pos()
        row = mouse_position[1] // consts.CELL_SIZE
        col = mouse_position[0] // consts.CELL_SIZE

        if 0 <= row < 3 and 0 <= col < 3 and self.game_state[row][col] is None:
            current_turn = self.players[0]
            self.game_state[row][col] = current_turn

            if current_turn == self.human_player:
                self.draw_x(row, col)
            else:
                self.draw_o(row, col)

            if self.check_winner():
                self.winner = current_turn 
                self.draw_game_result(f"{current_turn} wins!")
                self.game_end = True
            elif all(all(cell is not None for cell in row) for row in self.game_state):
                self.draw_game_result("It's a draw!")
                self.game_end = True
            else:
                self.get_turn()
                if self.players[0] == self.ai_player:
                    self.awaiting_ai = True
                    self.ai_move_time = pygame.time.get_ticks()

    def ai_move(self) -> None:
        _, move = self.minimax(self.game_state, self.ai_player, 0, self.difficulty_map[self.difficulty_level])
        print(f"AI evaluated move: {move}")
        if move:
            row, col = move
            self.game_state[row][col] = self.ai_player
            self.draw_o(row, col)

            if self.check_winner():
                self.winner = self.ai_player
                self.draw_game_result(f"{self.ai_player} wins!")
                self.game_end = True
            elif all(all(cell is not None for cell in row) for row in self.game_state):
                self.draw_game_result("It's a draw!")
                self.game_end = True
            else:
                self.get_turn()

    def minimax(self, state, player, depth, max_depth):
        winner = self.check_state_winner(state)
        if winner == self.ai_player:
            return 1, None
        elif winner == self.human_player:
            return -1, None
        elif all(all(cell is not None for cell in row) for row in state):
            return 0, None
        if depth >= max_depth:
            return 0, None

        best_move = None
        if player == self.ai_player:
            max_eval = -float('inf')
            for r in range(3):
                for c in range(3):
                    if state[r][c] is None:
                        state[r][c] = player
                        eval, _ = self.minimax(state, self.human_player, depth + 1, max_depth)
                        state[r][c] = None
                        if eval > max_eval:
                            max_eval = eval
                            best_move = (r, c)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for r in range(3):
                for c in range(3):
                    if state[r][c] is None:
                        state[r][c] = player
                        eval, _ = self.minimax(state, self.ai_player, depth + 1, max_depth)
                        state[r][c] = None
                        if eval < min_eval:
                            min_eval = eval
                            best_move = (r, c)
            return min_eval, best_move

    def check_state_winner(self, state):
        for row in state:
            if row[0] is not None and row[0] == row[1] == row[2]:
                return row[0]
        for col in range(3):
            if state[0][col] is not None and state[0][col] == state[1][col] == state[2][col]:
                return state[0][col]
        if state[0][0] is not None and state[0][0] == state[1][1] == state[2][2]:
            return state[0][0]
        if state[0][2] is not None and state[0][2] == state[1][1] == state[2][0]:
            return state[0][2]
        return None

    def draw_x(self, row, col):
        padding = 30
        x1 = col * consts.CELL_SIZE + padding
        y1 = row * consts.CELL_SIZE + padding
        x2 = (col + 1) * consts.CELL_SIZE - padding
        y2 = (row + 1) * consts.CELL_SIZE - padding
        pygame.draw.line(self.screen, (255, 255, 255), (x1, y1), (x2, y2), 3)
        pygame.draw.line(self.screen, (255, 255, 255), (x1, y2), (x2, y1), 3)

    def draw_o(self, row, col):
        center_x = col * consts.CELL_SIZE + consts.CELL_SIZE // 2
        center_y = row * consts.CELL_SIZE + consts.CELL_SIZE // 2
        radius = consts.CELL_SIZE // 2 - 20
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius, 3)

    def draw_game_result(self, message):
        overlay = pygame.Surface((consts.WIDTH, consts.HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(message, True, (0, 0, 0))
        text_rect = text.get_rect(center=(consts.WIDTH // 2, consts.HEIGHT // 2))
        self.screen.blit(text, text_rect)

        restart_text = self.small_font.render("Click anywhere to restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(consts.WIDTH // 2, consts.HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def check_winner(self):
        return self.check_state_winner(self.game_state) is not None

if __name__ == "__main__":
    window = Window()
    window.mainloop()
    
# The game is almost done, 90% I assume 