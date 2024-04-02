import importlib
import sys
import os
import readline
from color import *

def install_package(module_name,head_list):
    import subprocess
    subprocess.check_call(head_list+['install', module_name])
    print(f"{module_name} installed successfully.")
def install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"{module_name} not found. Installing...")
        try:
            install_package(module_name,["pip"])
        except Exception as e:
            print(f"Failed to install {module_name}. Error: {e}")
            print("Trying the other way...")
            try:
                install_package(module_name,["python","-m","pip"])
            except Exception as e:
                print(f"Failed to install {module_name}. Error: {e}")
                print("Seems like you don't have pip!")
            

def print_greetings():
    project  = colorize(bcolors.OKBLUE,"gitbrowser")
    dev_name = colorize(bcolors.OKBLUE,"Hdvpdrm")
    help = colorize(bcolors.OKGREEN,"help")
    print(f"Welcome to the {project}'s fork by {dev_name}!")
    print(f"Print {help} to see available commands.")
def main():
    # Install modules
    required_modules = ['requests', 'random_word', 'webbrowser', "tqdm"]
    for module in required_modules:
        install_module(module)

    import gitfetcher
    import commandline      

    # Define the URL template for fetching repositories
    url_template = "https://api.github.com/search/repositories?q=QUERY&sort=stars&order=desc&per_page=PERPAGE"
    
    # Initialize the Fetcher with the URL template and placeholders
    _fetcher = gitfetcher.Fetcher(url_template, "QUERY", "PERPAGE")
    
    # Initialize the Listener with the Fetcher
    _listener = commandline.Listener(_fetcher)

    os.system('cls' if os.name == 'nt' else 'clear')
    print_greetings()
    
    # Command-line interface loop
    while True:
        try:
            text_input = str(input(".. "))
            _listener.map_input(text_input)
        except KeyboardInterrupt as _:
            print("\nquit...")
            sys.exit(0)
        except EOFError as _:
            sys.exit(0)

if __name__ == '__main__':
    main()
