import time

import pygame

# Define the size of the overlay window
WIDTH, HEIGHT = 400, 100

# Initialize Pygame and set the window size
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Define the font for the overlay window
font = pygame.font.SysFont('calibri', 30)

# Define the initial position of the overlay window
x, y = 0, 0


# Define the function to show the overlay window
def show_overlay(button):
    # Create the text to display in the overlay window
    text = font.render(f"Button {button} clicked!", True, (255, 255, 255))
    # Clear the window
    window.fill((0, 0, 0))
    # Draw the text in the center of the window
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)
    # Show the window
    pygame.display.update()
    # Wait for 3 seconds
    time.sleep(3)
    # Move the overlay window up with animation
    for i in range(HEIGHT):
        # Clear the window
        window.fill((0, 0, 0))
        # Draw the text at the new position
        text_rect.move_ip(0, -1)
        window.blit(text, text_rect)
        # Show the window
        pygame.display.update()
        # Wait a short time to create the animation effect
        time.sleep(0.01)


# Define the function to check for mouse clicks
def check_click():
    previous_text = None
    while True:
        for event in pygame.event.get():
            # Check if the event is a mouse button click
            if event.type == pygame.MOUSEBUTTONUP:
                # Get the mouse position relative to the Pygame window
                pos = pygame.mouse.get_pos()
                if pos[0] >= x and pos[0] <= x + WIDTH and pos[1] >= y and pos[1] <= y + HEIGHT:
                    # Get the button that was clicked
                    button = event.button
                    if previous_text is not None:
                        # Move the previous message up with animation
                        for i in range(HEIGHT):
                            # Clear the window
                            window.fill((0, 0, 0))
                            # Draw the previous text at the new position
                            text_rect = previous_text.get_rect(center=(WIDTH // 2, (HEIGHT // 2) - i))
                            window.blit(previous_text, text_rect)
                            # Show the window
                            pygame.display.update()
                            # Wait a short time to create the animation effect
                            time.sleep(0.01)
                    # Show the current message
                    show_overlay(button)
                    previous_text = font.render(f"Button {button} clicked!", True, (255, 255, 255))


# Start the program
check_click()
