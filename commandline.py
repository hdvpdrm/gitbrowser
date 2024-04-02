import re
import gitfetcher
import subprocess
import json
import os
from color import *

class Listener:
    """
    Command-line listener class that interprets user input and triggers corresponding actions.
    """

    def __init__(self, fetcher):
        """
        Initializes the listener with a Fetcher instance.

        Parameters:
        - fetcher (gitfetcher.Fetcher): The Fetcher instance to interact with GitHub repositories.
        """
        self.fetcher = fetcher
        self.keyword_mapping = {
            'search': self.search,
            'select': self.select,
            'repo': self.repo,
            'options': self.options,
            'exit': self.ext,
            'explore': self.randrepo,
            'help':self.help,
            'clear':self.clear
        }

    def clear(self, command):
        """
        Clear the terminal screen.

        Parameters:
        No parameters.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    def help(self,command):
        if command is not None:
            if command in self.keyword_mapping.keys():
                command_str = colorize(bcolors.OKGREEN,command)
                print(f" command: {command_str}")
                print(self.keyword_mapping[command].__doc__)
            else:
                print(f"{command} doesn't exist!")
            return
        
        for i, pair in enumerate(self.keyword_mapping.items()):
            key, val = pair
            if key != "help":
                command_str = colorize(bcolors.OKGREEN,key)
                i_str = colorize(bcolors.OKBLUE,str(i))
                print(f"command {i_str}: {command_str}")
                print(val.__doc__)
                
    def map_input(self, input_text):
        """
        Maps user input to corresponding functions based on keywords.

        Parameters:
        - input_text (str): User input text.
        """
        match = re.match(r'(\w+)(?:\s+(.*))?', input_text)

        if match:
            keywords, parameters = match.groups()

            # Check if the first word is a valid keyword
            if keywords in self.keyword_mapping:
                # Call the corresponding function with parameters
                self.keyword_mapping[keywords](parameters)
            else:
                print("Invalid keyword")
        else:
            print("Invalid input format")

    def _check_argument(self, arg,command):
        '''
        check is command argument correct.
        '''
        if arg is None:
            command_str = colorize(bcolors.OKGREEN,command)
            help = colorize(bcolors.OKBLUE,f"help {command}")
            print(f"no argument was provided for {command_str}!. Use {help}.")
            return False
        return True
        
    def search(self, query):
        """
        Executes a search for GitHub repositories based on the provided query and displays the list.

        Parameters:
        - query (str): The search query for GitHub repositories.
        """
        if not self._check_argument(query,"search"): return None
        
        self.fetcher.get_repo_list(query).display_repo_list()

    def select(self, key):
        """
        Selects a repository based on the provided numerical key.

        Parameters:
        - key (str): The numerical key of the repository to select.
        """
        if not self._check_argument(key,"select"): return None
        
        if self.fetcher.currentrepolist is not None:
            if key.isnumeric():
                self.fetcher.currentrepolist.currentrepository = gitfetcher.Repository(
                    self.fetcher.currentrepolist.repolist[int(key)])
                print(f"Selected repo {key} : {self.fetcher.currentrepolist.repolist[int(key)]['name']}")
            else:
                print("Please select the repo using its numerical key. select [key]")
        else:
            print("You must search for repos first. search [keywords]")

    def repo(self, optionals):
        """
        Performs various actions related to the selected repository.

        Parameters:
        - optionals (str): Additional options for the selected repository.
        """
        if not self._check_argument(optionals,"repo"): return None
        
        if self.fetcher.currentrepolist is not None:
            if self.fetcher.currentrepolist.currentrepository is not None:
                if optionals == "expand":
                    # Display detailed information about the selected repository
                    self.fetcher.currentrepolist.currentrepository.display_repo()
                elif optionals == "open":
                    # Open the repository in the default web browser
                    self.fetcher.currentrepolist.currentrepository.open_in_browser()
                elif optionals.startswith("details "):
                    # Display specific details about the repository
                    parameter = optionals[len("details "):]
                    try:
                        print(self.fetcher.currentrepolist.currentrepository.data[str(parameter)])
                    except KeyError:
                        print("Invalid parameter")
                elif optionals.startswith("clone "):
                    # Clone the repository into a specified folder
                    parameter = optionals[len("clone "):]
                    if parameter is not None:
                        subprocess.run(f"git clone {self.fetcher.currentrepolist.currentrepository.url} {parameter}")
                    else:
                        print("Specify the folder you want to clone in")
                elif optionals.startswith("clone"):
                    # Clone the repository with optional output folder or use default settings
                    with open("settings.json", 'r') as file:
                        data = json.load(file)
                        if data["outputfolder"] is not None and data["outputfolder"] != "":
                            subprocess.run(f"git clone {self.fetcher.currentrepolist.currentrepository.url} {data['outputfolder']}")
                        else:
                            print("You must either specify the clone path or set a clone folder default. repo clone PATH / options clonefolder PATH")
                else:
                    print("Invalid option")
            else:
                print("You must select a repo first. select [key]")
        else:
            print("You must search repos first. search [keywords]")

    def options(self, optionals):
        """
        Adjusts various options related to the application.

        Parameters:
        - optionals (str): Additional options for configuring the application.
        """
        if not self._check_argument(optionals,"options"): return None
        
        if optionals.startswith("perpage "):
            # Change the default search count per page
            parameter = optionals[len("perpage "):]
            with open("settings.json", 'r') as file:
                data = json.load(file)
                data["perpage"] = parameter
            with open("settings.json", 'w') as file:
                json.dump(data, file, indent=2)
            print(f"Changed the default search count to {parameter}")
        elif optionals.startswith("clonefolder "):
            # Change the default output folder for cloning
            parameter = optionals[len("clonefolder "):]
            with open("settings.json", 'r') as file:
                data = json.load(file)
                data["outputfolder"] = parameter
            with open("settings.json", 'w') as file:
                json.dump(data, file, indent=2)
            print(f"Changed default output folder to {parameter}")
        else:
            print("Invalid option")

    def ext(self, optionals):
        """
        Exits the command-line interface.
        
        Parameters:
        - optionals (str): Unused parameter.
        """
        exit()

    def randrepo(self, count):
        """
        Retrieves a specified number of random repositories and displays their list.

        Parameters:
        - count (str): The number of random repositories to retrieve.
        """
        if not self._check_argument(count,"explore"): return None
        
        try:
            count = int(count)
        except:
            print("Invalid parameter")
            return
        if count > 10:
            count = 10
        if count < 0:
            count = 1
        print(f"Getting {count} random repos for you. Please wait ...")
        self.fetcher.get_random_repos(count).display_repo_list()
