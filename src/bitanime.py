# Dependencies

import requests
import ctypes
import os
import backend as bd
import colorama
import concurrent.futures
from tqdm.contrib.concurrent import thread_map
from bs4 import BeautifulSoup
from colorama import Fore

colorama.init(autoreset=True)
try:
    ctypes.windll.kernel32.SetConsoleTitleW("BitAnime")
except (AttributeError):
    pass


def bitanime():
    again = True
    while again:
        print(
            f""" {Fore.LIGHTBLUE_EX}
                   ____  _ _      _          _
                  | __ )(_) |_   / \   _ __ (_)_ __ ___   ___
                  |  _ \| | __| / _ \ | '_ \| | '_ ` _ \ / _ \\
                  | |_) | | |_ / ___ \| | | | | | | | | |  __/
                  |____/|_|\__/_/   \_\_| |_|_|_| |_| |_|\___|
                              {Fore.LIGHTYELLOW_EX}
                                  By: sh1nobu
                  Github: https://github.com/sh1nobuu/BitAnime
    """
        )
        """
    Ask user for input and then check if the anime provided exists or if not, loop
    """
        check = True
        while check:
            name = input(f"Enter anime name >> ").lower()
            if "-" in name:
                title = name.replace("-", " ").title().strip()
            else:
                title = name.title().strip()
            source = f"https://gogoanime.pe/category/{name}"
            resp = requests.get(source)
            if resp.status_code == 200:
                print(f"{Fore.LIGHTGREEN_EX}===========================================")
                check = False
            else:
                print(
                    f"{Fore.LIGHTRED_EX}Error 404: Anime not found. Please try again."
                )
                check = True
        """
    Get how many episode/s the anime has
    """
        soup = BeautifulSoup(resp.content, "html.parser")
        episode_number = soup.find("ul", {"id": "episode_page"})
        episode_number = episode_number.get_text().split("-")[-1].strip()
        """
    Print the anime name, episode, and the link of the anime
    """
        print(f"Title: {Fore.LIGHTCYAN_EX}{title}")
        print(f"Episode/s: {Fore.LIGHTCYAN_EX}{episode_number}")
        print(f"Link: {Fore.LIGHTCYAN_EX}{source}")
        print(f"{Fore.LIGHTGREEN_EX}===========================================")
        """
    Create a download folder for the anime
    """
        folder = os.path.join(os.getcwd(), title)
        if not os.path.exists(folder):
            os.mkdir(folder)
        """
    Check if the anime has episode 0 or not
    """
        source = f"https://gogoanime.pe/{name}"
        resp = requests.get(source)
        soup = BeautifulSoup(resp.content, "html.parser")
        episode_zero = soup.find("h1", {"class": "entry-title"})
        if episode_zero is None:
            # Episode 0 does exist
            exec = concurrent.futures.ThreadPoolExecutor()
            episode_links = bd.get_links(name, episode_number)
            download_links = list(exec.map(bd.get_download_links, episode_links))
            filtered_download_links = [download_link for download_link in download_links if download_link]
            download_urls = list(exec.map(bd.get_download_urls, filtered_download_links))
            print(f"Downloading {Fore.LIGHTCYAN_EX}{len(download_urls)} episode/s")
            print(f"{Fore.LIGHTGREEN_EX}===========================================")
            bd.get_path(folder)
            thread_map(
                bd.download_episodes, download_urls, ncols=75, total=len(download_urls)
            )
            try:
                os.startfile(folder)
            except (AttributeError):
                import sys, subprocess

                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, folder])

        else:
            # Episode 0 does not exist
            exec = concurrent.futures.ThreadPoolExecutor()
            episode_links = bd.get_links(name, episode_number)
            download_links = list(exec.map(bd.get_download_links, episode_links))
            filtered_download_links = [download_link for download_link in download_links if download_link]
            download_urls = list(exec.map(bd.get_download_urls, filtered_download_links))
            print(f"Downloading {Fore.LIGHTCYAN_EX}{len(download_urls)} episode/s")
            print(f"{Fore.LIGHTGREEN_EX}===========================================")
            bd.get_path(folder)
            thread_map(
                bd.download_episodes, download_urls, ncols=75, total=len(download_urls)
            )
            try:
                os.startfile(folder)
            except (AttributeError):
                import sys, subprocess

                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, folder])

        use_again = input("Do you want to download other anime? (y|n) >> ").lower()
        if use_again == "y":
            again = True
            os.system("cls")
        else:
            again = False


if __name__ == "__main__":
    bitanime()
