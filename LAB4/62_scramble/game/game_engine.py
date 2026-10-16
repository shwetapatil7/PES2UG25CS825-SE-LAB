
import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = [
            "PYTHON", "PYGAME", "PLANET", "ROCKET",
            "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"
        ]

        self.secret_word = ""
        self.scrambled_word = ""
        self.tile_letters = []
        self.selected_tile = None

        self.score = 0.0
        self.hints_used = 0
        self.revealed_positions = set()

        self.round_duration = 20  # seconds
        self.round_start_time = pygame.time.get_ticks()
        self.round_over_time = None
        self.game_over_pending = False

        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        center = width // 2

        # Input and buttons
        self.input_box = TextBox(center - 220, 255, 200, 46)
        self.submit_btn = pygame.Rect(center - 5, 255, 100, 46)
        self.hint_btn = pygame.Rect(center + 110, 255, 90, 46)

        # Fonts
        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 34)
        self.font_msg = pygame.font.SysFont(None, 24)
        self.font_btn = pygame.font.SysFont(None, 22)
        self.font_tile = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 20)

        self.next_round()

    def scramble_string(self, word):
        letters = list(word)

        if len(letters) > 1:
            while True:
                random.shuffle(letters)
                shuffled = "".join(letters)

                if shuffled != word:
                    return shuffled

        return word

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)

        self.tile_letters = list(self.scrambled_word)
        self.selected_tile = None

        self.hints_used = 0
        self.revealed_positions = set()

        self.input_box.clear()

        self.round_start_time = pygame.time.get_ticks()
        self.round_over_time = None
        self.game_over_pending = False

    def get_time_left(self):
        elapsed = (
            pygame.time.get_ticks() - self.round_start_time
        ) / 1000

        return max(0, self.round_duration - elapsed)

    def get_current_guess(self):
        # Use typed input when provided.
        typed_guess = self.input_box.text.strip().upper()

        if typed_guess:
            return typed_guess

        # Otherwise, use the order of the letter tiles.
        return "".join(self.tile_letters)

    def submit_guess(self):
        if self.game_over_pending:
            return

        guess = self.get_current_guess()

        if not guess:
            self.feedback_msg = "Type or arrange a word first!"
            self.feedback_color = (240, 170, 50)
            return

        # TASK 1: Compare with the original secret word.
        if guess == self.secret_word:
            # Each hint costs 0.25 points.
            points_earned = max(0, 1.0 - 0.25 * self.hints_used)
            self.score += points_earned

            self.feedback_msg = (
                f"CORRECT! {self.secret_word} | "
                f"+{points_earned:.2f} points"
            )
            self.feedback_color = (80, 230, 110)

            # Start a fresh round.
            self.next_round()

        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.input_box.clear()

    def give_hint(self):
        if self.game_over_pending:
            return

        # Reveal one additional letter in its correct position.
        hidden_positions = [
            i for i in range(len(self.secret_word))
            if i not in self.revealed_positions
        ]

        if not hidden_positions:
            self.feedback_msg = "All letters have been revealed!"
            self.feedback_color = (240, 170, 50)
            return

        position = random.choice(hidden_positions)
        self.revealed_positions.add(position)

        self.hints_used += 1
        self.score = max(0, self.score - 0.25)

        self.feedback_msg = (
            f"Hint revealed! -0.25 points "
            f"({len(self.revealed_positions)}/{len(self.secret_word)})"
        )
        self.feedback_color = (255, 210, 90)

    def handle_tile_click(self, position):
        if self.game_over_pending:
            return

        tile_width = 44
        tile_gap = 8
        total_width = (
            len(self.tile_letters) * tile_width
            + (len(self.tile_letters) - 1) * tile_gap
        )
        start_x = (self.width - total_width) // 2
        tile_y = 155

        for i in range(len(self.tile_letters)):
            rect = pygame.Rect(
                start_x + i * (tile_width + tile_gap),
                tile_y,
                tile_width,
                48
            )

            if rect.collidepoint(position):
                if self.selected_tile is None:
                    self.selected_tile = i
                elif self.selected_tile == i:
                    self.selected_tile = None
                else:
                    # TASK 4: Swap the two selected letter tiles.
                    self.tile_letters[self.selected_tile], \
                        self.tile_letters[i] = (
                            self.tile_letters[i],
                            self.tile_letters[self.selected_tile]
                        )

                    self.selected_tile = None

                return

    def handle_event(self, event):
        if not self.game_over_pending:
            self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

            elif self.hint_btn.collidepoint(event.pos):
                self.give_hint()

            else:
                self.handle_tile_click(event.pos)

    def update(self):
        # TASK 3: End the round when its countdown reaches zero.
        if self.game_over_pending:
            elapsed = pygame.time.get_ticks() - self.round_over_time

            if elapsed >= 1800:
                self.next_round()

            return

        if self.get_time_left() <= 0:
            self.game_over_pending = True
            self.round_over_time = pygame.time.get_ticks()

            self.feedback_msg = (
                f"TIME UP! The correct word was {self.secret_word}"
            )
            self.feedback_color = (255, 100, 100)

            self.input_box.clear()

    def render(self, screen):
        screen.fill((26, 30, 38))

        # Title
        title = self.font_title.render(
            "Word Scramble Arena", True, (245, 245, 245)
        )
        screen.blit(
            title,
            (self.width // 2 - title.get_width() // 2, 20)
        )

        # Score
        score_text = self.font_msg.render(
            f"Score: {self.score:.2f}", True, (255, 220, 80)
        )
        screen.blit(
            score_text,
            (self.width // 2 - score_text.get_width() // 2, 65)
        )

        # TASK 3: Countdown timer and timer bar
        time_left = self.get_time_left()

        timer_text = self.font_small.render(
            f"Time left: {time_left:.1f}s",
            True,
            (245, 245, 245)
        )
        screen.blit(
            timer_text,
            (self.width // 2 - timer_text.get_width() // 2, 91)
        )

        bar_width = min(420, self.width - 40)
        bar_x = (self.width - bar_width) // 2
        bar_y = 116

        pygame.draw.rect(
            screen, (65, 70, 82),
            (bar_x, bar_y, bar_width, 10),
            border_radius=5
        )

        remaining_width = int(
            bar_width * time_left / self.round_duration
        )

        if remaining_width > 0:
            timer_color = (
                (80, 220, 110) if time_left > 7
                else (255, 170, 50) if time_left > 3
                else (255, 70, 70)
            )

            pygame.draw.rect(
                screen, timer_color,
                (bar_x, bar_y, remaining_width, 10),
                border_radius=5
            )

        # TASK 4: Interactive letter tiles
        tile_width = 44
        tile_gap = 8
        total_width = (
            len(self.tile_letters) * tile_width
            + (len(self.tile_letters) - 1) * tile_gap
        )
        start_x = (self.width - total_width) // 2

        for i, letter in enumerate(self.tile_letters):
            rect = pygame.Rect(
                start_x + i * (tile_width + tile_gap),
                155,
                tile_width,
                48
            )

            tile_color = (
                (220, 150, 45)
                if i == self.selected_tile
                else (55, 100, 145)
            )

            pygame.draw.rect(
                screen, tile_color, rect, border_radius=6
            )
            pygame.draw.rect(
                screen, (190, 210, 230),
                rect, width=2, border_radius=6
            )

            letter_surface = self.font_tile.render(
                letter, True, (255, 255, 255)
            )

            screen.blit(
                letter_surface,
                (
                    rect.centerx - letter_surface.get_width() // 2,
                    rect.centery - letter_surface.get_height() // 2
                )
            )

        instruction = self.font_small.render(
            "Click two tiles to swap them, or type your answer below.",
            True,
            (190, 200, 215)
        )
        screen.blit(
            instruction,
            (self.width // 2 - instruction.get_width() // 2, 210)
        )

        # TASK 2: Progressive hint display
        hint_pattern = " ".join(
            letter if i in self.revealed_positions else "_"
            for i, letter in enumerate(self.secret_word)
        )

        hint_surface = self.font_msg.render(
            f"Hint: {hint_pattern}",
            True,
            (255, 210, 90)
        )
        screen.blit(
            hint_surface,
            (self.width // 2 - hint_surface.get_width() // 2, 230)
        )

        # Input box
        self.input_box.render(screen)

        # Submit button
        pygame.draw.rect(
            screen, (50, 150, 85),
            self.submit_btn, border_radius=6
        )
        pygame.draw.rect(
            screen, (220, 220, 220),
            self.submit_btn, width=2, border_radius=6
        )

        submit_text = self.font_btn.render(
            "SUBMIT", True, (255, 255, 255)
        )
        screen.blit(
            submit_text,
            (
                self.submit_btn.centerx - submit_text.get_width() // 2,
                self.submit_btn.centery - submit_text.get_height() // 2
            )
        )

        # Hint button
        pygame.draw.rect(
            screen, (130, 90, 175),
            self.hint_btn, border_radius=6
        )
        pygame.draw.rect(
            screen, (220, 220, 220),
            self.hint_btn, width=2, border_radius=6
        )

        hint_text = self.font_btn.render(
            "HINT (-0.25)", True, (255, 255, 255)
        )
        screen.blit(
            hint_text,
            (
                self.hint_btn.centerx - hint_text.get_width() // 2,
                self.hint_btn.centery - hint_text.get_height() // 2
            )
        )

        # Feedback
        feedback = self.font_msg.render(
            self.feedback_msg, True, self.feedback_color
        )
        screen.blit(
            feedback,
            (
                self.width // 2 - feedback.get_width() // 2,
                325
            )
        )
