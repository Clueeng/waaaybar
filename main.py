#!/usr/bin/env python3

# YOU MAY NOT REDISTRIBUTE THIS WITHOUT CREDIT

from pathlib import Path
import sys, tty, termios, os, subprocess, shutil, requests

def wait_any_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdin.read(1)  # read one character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def detect_package_manager():
    managers = {
        "pacman": "pacman",
        "dnf": "dnf",
        "yum": "yum",
        "apt": "apt",
        "zypper": "zypper",
        "apk": "apk",
        "emerge": "emerge"
    }
    for name, cmd in managers.items():
        if shutil.which(cmd):
            return name
    return None

def execute(command):
    subprocess.run(command, check=True)

author = {
    "name": "Flaily",
    "github": "https://github.com/Clueeng"
}

app_name = 'waaaybar'
config_folder = os.path.expanduser('~/.config/waaaybar')

def is_waybar_installed():
    return shutil.which("waybar") is not None

def install_waybar():
    print("\nAttempting to install Waybar...")

    pkg_mgr = detect_package_manager()
    if not pkg_mgr:
        print("No supported package manager detected.")
        return False

    try:
        subprocess.run(["sudo", pkg_mgr, "install", "-y", "waybar"], check=True)
        print("Waybar installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Waybar installation failed.")
        return False


def is_first_time():
    # To determine if it is the first time the user
    # runs this, we'll simply check if the config folder exists already or not
    if not is_waybar_installed():
        print(f'It seems you do not have waybar installed')
        print(f'Do you want to install it? (y/n)')
        installation = input('')
        while installation not in ['y', 'n']:
            print('Choose \'y\' for yes, \'n\' for no')
            installation = input('')
        if installation == 'y':
            if not install_waybar():
                print('Installation aborted')
                exit(1)
        else:
            # The user does not have waybar
            exit(1)
    
    config = Path(f'{config_folder}')
    if config.is_dir():
        return False
    
    # Create a default waybar config

    config.mkdir(parents=True, exist_ok=True)
    return True

def get_available_themes():
    themes = Path(f'{config_folder}/themes')
    if not themes.is_dir():
        themes.mkdir(parents=True, exist_ok=True)
    
    return [f.name for f in themes.iterdir() if f.is_dir()]


def download_file(url, dest_path):
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded {url} to {dest_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False
    
def apply_theme(name):
    source = Path(os.path.expanduser(f'~/.config/{app_name}/themes/{name}'))
    destination = Path(os.path.expanduser('~/.config/waybar'))

    if not source.exists() or not source.is_dir():
        print(f"Theme '{name}' does not exist.")
        return False

    try:
        # Remove current waybar config folder before copying
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        print(f"Theme '{name}' applied successfully.")
        return True
    except Exception as e:
        print(f"Failed to apply theme '{name}': {e}")
        return False

def install_theme(css_url, config_url, name):
    theme_dir = Path(os.path.expanduser(f'~/.config/{app_name}/themes/{name}'))
    theme_dir.mkdir(parents=True, exist_ok=False)  # fail if exists

    css_path = theme_dir / 'style.css'
    config_path = theme_dir / 'config'

    success_css = download_file(css_url, css_path)
    success_config = download_file(config_url, config_path)

    return success_css and success_config

def copy_waybar_to(name):
    source = Path(os.path.expanduser('~/.config/waybar'))
    destination = Path(os.path.expanduser(f'~/.config/{app_name}/themes/{name}'))

    if not source.exists() or not source.is_dir():
        print("Current Waybar config folder does not exist.")
        return False

    if destination.exists():
        print(f"The theme '{name}' already exists at {destination}")
        return False

    try:
        shutil.copytree(source, destination)
        print(f"Copied current Waybar config to theme '{name}'.")
        return True
    except Exception as e:
        print(f"Failed to copy config: {e}")
        return False

def main():
    if is_first_time():
        # Tutorial
        print(f'Welcome to {app_name}!')
        print(f'Our goal is to make switching between waybar configs easy')
        print(f'Press any key...')
        wait_any_key()

    # Print once
    execute(['clear'])
    print(f'This tool is maintained by {author["name"]} at {author["github"]}')
    print(f'What do you want to do ?\n')

    # Then normal run
    choices = [
        "1) List all themes",
        "2) Install a theme",
        "3) Choose a theme",
        "4) Backup current theme"
    ]
    
    while True:
        # Clear here
        execute(['clear'])

        for c in choices:
            print(c)
        
        choice = input("Choose an option: ")

        if choice == '1':
            for theme in get_available_themes():
                print(theme)
            
            print(f'Press any key to continue...')
            wait_any_key()
        if choice == '2':
            # TODO : install from a URL to here
            css = input(f'Link to the style.css: ')
            config = input(f'Link to the config: ')
            name = input('Name of the theme: ')
            # Move that to our config

            while name in get_available_themes():
                print(f"Theme '{name}' already exists.")
                name = input('Name of the theme: ')
            
            if install_theme(css, config, name):
                print("Theme installed successfully.")
            else:
                print("Failed to install theme.")
            wait_any_key()

        if choice == '3':
            themes = get_available_themes()
            if not themes:
                print("No themes available.")
                wait_any_key()
                continue

            print("Available themes:")
            for idx, theme in enumerate(themes, 1):
                print(f"{idx}) {theme}")

            selected = input("Select a theme by number: ").strip()
            if not selected.isdigit() or int(selected) not in range(1, len(themes)+1):
                print("Invalid selection.")
                wait_any_key()
                continue

            theme_name = themes[int(selected)-1]
            if apply_theme(theme_name):
                import time

                subprocess.run(['pkill', 'waybar'])
                time.sleep(0.3)
                subprocess.Popen(['waybar'], 
                               start_new_session=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                time.sleep(2)
                execute(['clear'])
                print("Theme applied!")
                print('Reloaded waybar')
                time.sleep(1)
            else:
                print("Failed to apply theme.")
                wait_any_key()

        if choice == '4':
            execute(['clear'])
            print(f'This action will copy the contents of your current config over to {app_name}\'s config folder')
            action = input('Are you sure you want to continue ? (y/n)')
            while not action in ['y', 'n']:
                print('Invalid choice...')
                action = input('Are you sure you want to continue ? (y/n)')

            if action == 'y':
                print('Great')
            if action == 'n':
                continue

            name = input('Enter the name of your theme: ')
            while name in get_available_themes():
                print(f'{name} already exists')
                name = input('Enter the name of your theme: ')    
            copy_waybar_to(name)

if __name__ == "__main__":
    main()