import curses

def init_curses():
    stdscr = curses.initscr()  # Initialize the screen
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Make getch() non-blocking
    curses.noecho()  # Do not display typed characters
    curses.cbreak()  # Disable line buffering
    return stdscr

def cleanup_curses():
    curses.nocbreak()  # Restore line buffering
    curses.echo()  # Re-enable character echo
    curses.endwin()  # End the curses application




stdscr = init_curses()
# Clear the screen
stdscr.clear()

# Hide the cursor
curses.curs_set(0)

# Get the size of the terminal
height, width = stdscr.getmaxyx()

# Display a message in the center of the screen
message = "Welcome to the Curses Application!"
message_y = height // 2
message_x = (width - len(message)) // 2
stdscr.addstr(message_y, message_x, message)

# Display instructions
instructions = "Press 'q' to quit."
instructions_y = message_y + 2
instructions_x = (width - len(instructions)) // 2
stdscr.addstr(instructions_y, instructions_x, instructions)

# Refresh the screen to show the content
stdscr.refresh()

# Main loop to handle user input
while True:
    ch = stdscr.getch()  # Wait for user input
    
    if ch == ord('q'):  # Exit if 'q' is pressed
        break

# Optionally, restore terminal settings and cleanup
stdscr.addstr(instructions_y + 2, instructions_x, "Goodbye!")
stdscr.refresh()
curses.napms(1000)  # Wait for a second to let the user see the "Goodbye!" message


