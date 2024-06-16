import sys
import pygame
import requests

# Initialize Pygame
pygame.init()

GRID_GENERATOR_URL = "https://sudoku-api.vercel.app/api/dosuku"

# Screen dimensions and grid configuration
GRID_SIZE = 9
CELL_SIZE = 60
WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = WIDTH
LINE_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)
NUM_COLOR = (0, 0, 255)
FIXED_NUM_COLOR = (0, 0, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20
SUCCESS_COLOR = (0, 255, 0)
HIGHLIGHT_COLOR = (173, 216, 230)
PADDING = 20
BUTTON_PADDING = 10


def obtain_grid():
    response = requests.get(GRID_GENERATOR_URL)
    if (
        response.status_code == 200
        and response.json()["newboard"]["message"] == "All Ok"
    ):
        print("Successfully obtained grid")
        return response.json()["newboard"]["grids"]
    else:
        print("Failed to obtain grid")
        return None


def parse_grids(grids):
    empty_grid = grids[0].get("value")
    solution_grid = grids[0].get("solution")
    difficulty = grids[0].get("difficulty")
    return empty_grid, solution_grid, difficulty


def draw_buttons():
    button_texts = ["Solve", "Reset", "Regenerate"]
    button_rects = []

    for i, text in enumerate(button_texts):
        x = WIDTH + BUTTON_SPACING + 10
        y = i * (BUTTON_HEIGHT + BUTTON_SPACING) + BUTTON_SPACING
        rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        button_rects.append(rect)
        pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=10)
        button_text = font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = button_text.get_rect(center=rect.center)
        screen.blit(button_text, (text_rect.x, text_rect.y))

    return button_rects


def draw_difficulty():
    difficulty_text = font.render(f"{difficulty.capitalize()}", True, LINE_COLOR)
    text_rect = difficulty_text.get_rect(
        center=(
            WIDTH + BUTTON_SPACING + BUTTON_WIDTH // 2,
            HEIGHT - BUTTON_SPACING - 20,
        )
    )
    screen.blit(difficulty_text, text_rect)


def reset_grid():
    global grid, original_grid
    grid = [row[:] for row in original_grid]


def is_grid_solved():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] != solution_grid[row][col]:
                return False
    return True


grids = obtain_grid()
original_grid, solution_grid, difficulty = parse_grids(grids)
grid = [row[:] for row in original_grid]

# Set up the display
screen = pygame.display.set_mode(
    (WIDTH + BUTTON_WIDTH + 3 * BUTTON_SPACING, HEIGHT + 2 * PADDING)
)
pygame.display.set_caption("Pydoku Game")
font = pygame.font.Font(None, 40)
clock = pygame.time.Clock()


def draw_grid(solved=False):
    screen.fill(BG_COLOR)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                col * CELL_SIZE + PADDING,
                row * CELL_SIZE + PADDING,
                CELL_SIZE,
                CELL_SIZE,
            )
            if selected == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

            num = grid[row][col]
            if num != 0:
                color = (
                    SUCCESS_COLOR
                    if solved
                    else (
                        FIXED_NUM_COLOR if original_grid[row][col] != 0 else NUM_COLOR
                    )
                )
                text = font.render(str(num), True, color)
                screen.blit(
                    text,
                    (
                        col * CELL_SIZE + CELL_SIZE // 4 + PADDING,
                        row * CELL_SIZE + CELL_SIZE // 4 + PADDING,
                    ),
                )

    for i in range(0, GRID_SIZE + 1, 3):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (i * CELL_SIZE + PADDING, PADDING),
            (i * CELL_SIZE + PADDING, HEIGHT + PADDING),
            3,
        )
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (PADDING, i * CELL_SIZE + PADDING),
            (WIDTH + PADDING, i * CELL_SIZE + PADDING),
            3,
        )


def is_valid_move(grid, row, col, num):
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False
    return True


def solve_sudoku(grid):
    empty = find_empty_location(grid)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num
            if solve_sudoku(grid):
                return True
            grid[row][col] = 0
    return False


def find_empty_location(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return (row, col)
    return None


def main():
    global grid, original_grid, difficulty, selected
    selected = None
    button_rects = draw_buttons()

    while True:
        solved = is_grid_solved()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < WIDTH + PADDING and y < HEIGHT + PADDING:
                    selected = (y // CELL_SIZE, x // CELL_SIZE)
                else:
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            if i == 0:  # Solve button
                                solve_sudoku(grid)
                            elif i == 1:  # Reset button
                                reset_grid()
                            elif i == 2:  # Regenerate button
                                grids = obtain_grid()
                                original_grid, solution_grid, difficulty = parse_grids(
                                    grids
                                )
                                grid = [row[:] for row in original_grid]
                                selected = None

            if event.type == pygame.KEYDOWN and selected and not solved:
                row, col = selected
                if original_grid[row][col] == 0:
                    if event.key == pygame.K_1:
                        grid[row][col] = 1
                    if event.key == pygame.K_2:
                        grid[row][col] = 2
                    if event.key == pygame.K_3:
                        grid[row][col] = 3
                    if event.key == pygame.K_4:
                        grid[row][col] = 4
                    if event.key == pygame.K_5:
                        grid[row][col] = 5
                    if event.key == pygame.K_6:
                        grid[row][col] = 6
                    if event.key == pygame.K_7:
                        grid[row][col] = 7
                    if event.key == pygame.K_8:
                        grid[row][col] = 8
                    if event.key == pygame.K_9:
                        grid[row][col] = 9
                    if event.key == pygame.K_BACKSPACE:
                        grid[row][col] = 0
                    if event.key == pygame.K_RETURN:
                        solve_sudoku(grid)

        draw_grid(solved)
        button_rects = draw_buttons()
        draw_difficulty()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
