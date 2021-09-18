import requests as req
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
    while True:
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
        while True:
            name = input(f"[{Fore.GREEN}+{Fore.RESET}] Enter anime name > ").lower()
            if "-" in name:
                title = name.replace("-", " ").title().strip()
            else:
                title = name.title().strip()
            source = f"https://gogoanime.pe/category/{name}"
            with req.get(source) as res:
                if res.status_code == 200:
                    soup = BeautifulSoup(res.content, "html.parser")
                    episode_number = soup.find("ul", {"id": "episode_page"})
                    episode_number = episode_number.get_text().split("-")[-1].strip()
                    break
                else:
                    print(
                        f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTRED_EX}Error 404: Anime not found. Please try again."
                    )
        while True:
            quality = input(
                f"[{Fore.GREEN}+{Fore.RESET}] Enter episode quality (1.SD/360P|2.HD/720P|3.FULLHD/1080P) > "
            )
            if quality == "1" or quality == "":
                episode_quality = "SDP"
                break
            elif quality == "2":
                episode_quality = "HDP"
                break
            elif quality == "3":
                episode_quality = "FullHDP"
                break
            else:
                print(
                    f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTRED_EX}Invalid input. Please try again."
                )
        print(f"[{Fore.GREEN}+{Fore.RESET}] Title: {Fore.LIGHTCYAN_EX}{title}")
        print(
            f"[{Fore.GREEN}+{Fore.RESET}] Episode/s: {Fore.LIGHTCYAN_EX}{episode_number}"
        )
        print(
            f"[{Fore.GREEN}+{Fore.RESET}] Quality: {Fore.LIGHTCYAN_EX}{episode_quality}"
        )
        print(f"[{Fore.GREEN}+{Fore.RESET}] Link: {Fore.LIGHTCYAN_EX}{source}")
        folder = os.path.join(os.getcwd(), title)
        if not os.path.exists(folder):
            os.mkdir(folder)
        while True:
            choice = input(
                f"[{Fore.GREEN}+{Fore.RESET}] Do you want to download all episode? (y/n) > "
            )
            if choice in ["y", "n"]:
                break
            else:
                print(
                    f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTRED_EX}Invalid input. Please try again."
                )
        if choice == "n":
            while True:
                try:
                    custom_episode_number = int(
                        input(
                            f"[{Fore.GREEN}+{Fore.RESET}] How many episode do you want to download? > "
                        )
                    )
                    if custom_episode_number == 0 or custom_episode_number > int(
                        episode_number
                    ):
                        raise bd.InvalidInputValue
                    else:
                        episode_number = custom_episode_number
                        break
                except ValueError:
                    print(
                        f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTRED_EX}Invalid input. Please try again."
                    )
                except bd.InvalidInputValue:
                    print(
                        f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTRED_EX}Custom episode cannot be equal to 0 or custom episode cannot be greater than {episode_number}"
                    )
        download = bd.Download(name, episode_quality, int(episode_number), folder)
        source = f"https://gogoanime.pe/{name}"
        with req.get(source) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            episode_zero = soup.find("h1", {"class": "entry-title"})
        if episode_zero is None:
            # Episode 0 == 200
            with concurrent.futures.ThreadPoolExecutor() as exec:
                episode_links = download.get_links(source)
                download_links = list(
                    exec.map(download.get_download_links, episode_links)
                )
                download_urls = list(
                    exec.map(download.get_download_urls, download_links)
                )
        else:
            # Episode 0 == 404
            with concurrent.futures.ThreadPoolExecutor() as exec:
                episode_links = download.get_links()
                download_links = list(
                    exec.map(download.get_download_links, episode_links)
                )
                download_urls = list(
                    exec.map(download.get_download_urls, download_links)
                )
        print(
            f"[{Fore.GREEN}+{Fore.RESET}] Downloading {Fore.LIGHTCYAN_EX}{len(download_urls)}{Fore.RESET} episode/s"
        )
        thread_map(
            download.download_episodes,
            download_urls,
            ncols=75,
            total=len(download_urls),
        )
        try:
            os.startfile(folder)
        except (AttributeError):
            import sys, subprocess

            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, folder])
        use_again = input(
            f"[{Fore.GREEN}+{Fore.RESET}] Do you want to use the app again? (y|n) > "
        ).lower()
        if use_again == "y":
            os.system("cls")
        else:
            break


if __name__ == "__main__":
    bitanime()
