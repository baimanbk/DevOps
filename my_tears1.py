import os
import curses
import pyfiglet
import subprocess

NAV_UP = curses.KEY_UP
NAV_DOWN = curses.KEY_DOWN
NAV_NEXT_PAGE = curses.KEY_RIGHT
NAV_PREV_PAGE = curses.KEY_LEFT

def welcome(stdscr):
    ascii_art = pyfiglet.figlet_format("User Management CLI")
    for line in ascii_art.splitlines():
        stdscr.addstr(line + "\n")
    stdscr.refresh()
    stdscr.addstr("\nPress any key to continue...\n")
    stdscr.refresh()
    stdscr.getch()

def list_users():
    users = os.popen("cut -d: -f1 /etc/passwd").read().splitlines()
    user_list = [user for user in users if not user.startswith('_') and len(user) > 2]
    return user_list

def display_users(stdscr, users, page, selected_user, page_size=5):
    total_pages = (len(users) // page_size) + (1 if len(users) % page_size else 0)
    start = (page - 1) * page_size
    end = start + page_size
    current_page_users = users[start:end]
    
    stdscr.clear()
    stdscr.addstr(f"Page {page}/{total_pages}\n", curses.color_pair(1))
    for i, user in enumerate(current_page_users):
        if i == selected_user:
            stdscr.addstr(f"> {user}\n", curses.color_pair(2))
        else:
            stdscr.addstr(f"  {user}\n")
    stdscr.addstr("\nChoose action (n=new user, d=delete user, l=lock user, u=unlock user, q=quit, ←/→=page, ↑/↓=select user): ")
    stdscr.refresh()

    return total_pages, current_page_users

def add_user(stdscr):
    stdscr.addstr("Enter new username: ")
    stdscr.refresh()
    curses.echo()
    username = stdscr.getstr().decode('utf-8')
    try:
        result = subprocess.run(['sudo', 'useradd', username], capture_output=True, text=True)
        if result.returncode == 0:
            stdscr.addstr(f"Successfully added user '{username}'!\n", curses.color_pair(2))
        else:
            stdscr.addstr(f"Error adding user '{username}': {result.stderr}\n", curses.color_pair(3))
    except Exception as e:
        stdscr.addstr(f"Exception occurred: {str(e)}\n", curses.color_pair(3))
    stdscr.refresh()

def delete_user(stdscr, user):
    stdscr.addstr(f"Are you sure you want to delete user '{user}'? (y/n): ")
    stdscr.refresh()
    curses.echo()
    confirm = stdscr.getstr().decode('utf-8').lower()
    if confirm == 'y':
        result = subprocess.run(['sudo', 'userdel', user], capture_output=True, text=True)
        if result.returncode == 0:
            stdscr.addstr(f"Successfully deleted user '{user}'!\n", curses.color_pair(3))
        else:
            stdscr.addstr(f"Error deleting user '{user}': {result.stderr}\n", curses.color_pair(3))
    else:
        stdscr.addstr("Deletion cancelled.\n", curses.color_pair(1))
    stdscr.refresh()

def lock_user(stdscr, user):
    result = subprocess.run(['sudo', 'usermod', '-L', user], capture_output=True, text=True)
    if result.returncode == 0:
        stdscr.addstr(f"User '{user}' locked.\n", curses.color_pair(4))
    else:
        stdscr.addstr(f"Error locking user '{user}': {result.stderr}\n", curses.color_pair(3))
    stdscr.refresh()

def unlock_user(stdscr, user):
    result = subprocess.run(['sudo', 'usermod', '-U', user], capture_output=True, text=True)
    if result.returncode == 0:
        stdscr.addstr(f"User '{user}' unlocked.\n", curses.color_pair(4))
    else:
        stdscr.addstr(f"Error unlocking user '{user}': {result.stderr}\n", curses.color_pair(3))
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

    stdscr.clear()
    welcome(stdscr)

    page = 1
    selected_user = 0
    users = list_users()
    page_size = 5

    while True:
        total_pages, current_page_users = display_users(stdscr, users, page, selected_user, page_size)
        
        action = stdscr.getch()
        
        if action == NAV_UP and selected_user > 0:
            selected_user -= 1
        elif action == NAV_DOWN and selected_user < len(current_page_users) - 1:
            selected_user += 1
        elif action == NAV_NEXT_PAGE and page < total_pages:
            page += 1
            selected_user = 0
        elif action == NAV_PREV_PAGE and page > 1:
            page -= 1
            selected_user = 0
        elif action == ord('n'):
            add_user(stdscr)
            users = list_users()
        elif action == ord('d') and current_page_users:
            delete_user(stdscr, current_page_users[selected_user])
            users = list_users()
        elif action == ord('l') and current_page_users:
            lock_user(stdscr, current_page_users[selected_user])
        elif action == ord('u') and current_page_users:
            unlock_user(stdscr, current_page_users[selected_user])
        elif action == ord('q'):
            break
        else:
            stdscr.addstr("Invalid action. Please try again.\n", curses.color_pair(3))
            stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
