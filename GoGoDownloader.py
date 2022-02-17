import requests
import ctypes
import os
from backend import gogoanime, CustomMessage, config_check
from bs4 import BeautifulSoup
from colorama import Fore

OK = f"{Fore.RESET}[{Fore.GREEN}+{Fore.RESET}] "
ERR = f"{Fore.RESET}[{Fore.RED}-{Fore.RESET}] "
IN = f"{Fore.RESET}[{Fore.LIGHTBLUE_EX}>{Fore.RESET}] "
try:
    ctypes.windll.kernel32.SetConsoleTitleW("GoGo Downloader")
except AttributeError:
    pass


def gogodownloader(config):
    CURRENT_DOMAIN = config["CurrentGoGoAnimeDomain"]
    os.system("cls")
    while True:
        print(
            f""" {Fore.LIGHTBLUE_EX}

             ______      ______                                      
            / ____/___  / ____/___                                   
           / / __/ __ \/ / __/ __ \                                  
          / /_/ / /_/ / /_/ / /_/ /                                  
          \__________/\____/\____/      __                __         
             / __ \____ _      ______  / /___  ____ _____/ /__  _____
            / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/
           / /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /    
          /_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     
    
                              {Fore.RED}
                                  By: Karl0ss
                             Forked From: sh1nobuu
                  Github: https://github.com/karl0ss/GoGoDownloader
    """
        )
        while True:
            name = input(f"{IN}Enter anime name > ").lower()
            if "-" in name:
                title = name.replace("-", " ").title().strip()
            else:
                title = name.title().strip()
            source = f"https://gogoanime.{CURRENT_DOMAIN}/category/{name}"
            with requests.get(source) as res:
                if res.status_code == 200:
                    soup = BeautifulSoup(res.content, "html.parser")
                    all_episodes = soup.find("ul", {"id": "episode_page"})
                    all_episodes = int(all_episodes.get_text().split("-")[-1].strip())
                    break
                else:
                    print(f"{ERR}Error 404: Anime not found. Please try again.")
        while True:
            quality = input(
                f"{IN}Enter episode quality (1.SD/360P|2.SD/480P|3.HD/720P|4.FULLHD/1080P) > "
            )
            if quality == "1" or quality == "":
                episode_quality = "360"
                break
            elif quality == "2":
                episode_quality = "480"
                break
            elif quality == "3":
                episode_quality = "720"
                break
            elif quality == "4":
                episode_quality = "1080"
                break
            else:
                print(f"{ERR}Invalid input. Please try again.")
        print(f"{OK}Title: {Fore.LIGHTCYAN_EX}{title}")
        print(f"{OK}Episode/s: {Fore.LIGHTCYAN_EX}{all_episodes}")
        print(f"{OK}Quality: {Fore.LIGHTCYAN_EX}{episode_quality}")
        print(f"{OK}Link: {Fore.LIGHTCYAN_EX}{source}")

        folder = os.path.join(os.getcwd(), title)
        if not os.path.exists(folder):
            os.mkdir(folder)

        choice = "y"

        if all_episodes != 1:
            while True:
                choice = input(
                    f"{IN}Do you want to download all episode? (y/n) > "
                ).lower()
                if choice in ["y", "n"]:
                    break
                else:
                    print(f"{ERR}Invalid input. Please try again.")

        episode_start = None
        episode_end = None

        if choice == "n":
            while True:
                try:
                    episode_start = int(input(f"{IN}Episode start > "))
                    episode_end = int(input(f"{IN}Episode end > "))
                    if episode_start <= 0 or episode_end <= 0:
                        CustomMessage(
                            f"{ERR}episode_start or episode_end cannot be less than or equal to 0"
                        ).print_error()
                    elif episode_start >= all_episodes or episode_end > all_episodes:
                        CustomMessage(
                            f"{ERR}episode_start or episode_end cannot be more than {all_episodes}"
                        ).print_error()
                    elif episode_end <= episode_start:
                        CustomMessage(
                            f"{ERR}episode_end cannot be less than or equal to episode_start"
                        ).print_error()
                    else:
                        break
                except ValueError:
                    print(f"{ERR}Invalid input. Please try again.")

        if episode_start is not None:
            pass
        else:
            episode_start = 1
        if episode_end is not None:
            pass
        else:
            episode_end = all_episodes

        gogo = gogoanime(
            config,
            name,
            episode_quality,
            folder,
            all_episodes,
            episode_start,
            episode_end,
            title,
        )

        source = f"https://gogoanime.{CURRENT_DOMAIN}/{name}"
        with requests.get(source) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            episode_zero = soup.find("h1", {"class": "entry-title"})  # value: 404

        if choice == "n" or episode_zero is not None:
            source = None

        dl_links = []
        episode_links = gogo.get_links(source)
        print(f"{OK}Scraping Links")
        for link in episode_links:
            dl_links.append(gogo.get_download_link(link))

        result = gogo.file_downloader(dl_links)
        if len(result.errors) > 0:
            while len(result.errors) > 0:
                print(f"{ERR}{len(result.errors)} links failed retrying.")
                episode_links = gogo.get_links(source)
                print(f"{OK}Re-Scraping Links")
                dl_links.clear()
                for link in episode_links:
                    dl_links.append(gogo.get_download_link(link))
                result = gogo.file_downloader(dl_links, overwrite_downloads=0)

        use_again = input(f"{IN}Do you want to use the app again? (y|n) > ").lower()
        if use_again == "y":
            os.system("cls")
        else:
            break


if __name__ == "__main__":
    config = config_check()
    gogodownloader(config)
