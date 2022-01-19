import requests
import json
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from colorama import Fore
from parfive import Downloader
from threading import Semaphore


OK = f"{Fore.RESET}[{Fore.GREEN}+{Fore.RESET}] "
ERR = f"{Fore.RESET}[{Fore.RED}-{Fore.RESET}] "
IN = f"{Fore.RESET}[{Fore.LIGHTBLUE_EX}>{Fore.RESET}] "

global CONFIG

screenlock = Semaphore(value=1)


def config_check():
    """Check for config.json and check required keys are set

    Returns:
        [object]: Config object
    """
    if os.path.exists("./config.json"):
        with open("./config.json", "r") as f:
            CONFIG = json.load(f)
        if not "GoGoAnimeAuthKey" in CONFIG or len(CONFIG["GoGoAnimeAuthKey"]) == 0:
            print("GoGoAnimeAuthKey not set in config.json")
            exit(0)
        else:
            return CONFIG
    else:
        print("config.json file not found")
        exit(0)


def max_concurrent_downloads(max_conn: int):
    """Check max_concurrent_downloads value and restrict to below 6

    Args:
        max_conn (int): Max concurrent downloads to allow

    Returns:
        [int]: Max concurrent downloads allowed
    """
    if max_conn > 6:
        return 6
    else:
        return max_conn


CURRENT_DOMAIN = "film"


@dataclass(init=True)
class Download:
    config: object
    name: str
    episode_quality: str
    folder: str
    all_episodes: int
    episode_start: int
    episode_end: int
    title: str
    printed: bool = False

    def get_links(self, source=None):
        if source is not None:
            source_ep = f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
            episode_links.insert(0, source)
        else:
            source_ep = f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
        return episode_links

    def get_download_link(self, url):

        page = requests.get(
            url,
            cookies=dict(auth=self.config["GoGoAnimeAuthKey"]),
        )

        soup = BeautifulSoup(page.content, "html.parser")

        for link in soup.find_all("a", href=True):
            if self.episode_quality in link.text:
                return link["href"]

    def file_downloader(self, file_list: dict):
        dl = Downloader(
            max_conn=max_concurrent_downloads(self.config["MaxConcurrentDownloads"]),
            overwrite=self.config["OverwriteDownloads"],
            headers=dict(
                [
                    (
                        "User-Agent",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                    ),
                    ("authority", "gogo-cdn.com"),
                    (
                        "referer",
                        f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/",
                    ),
                ]
            ),
        )

        for link in file_list:
            dl.enqueue_file(
                link,
                path=f"./{self.title}",
            )

        files = dl.download()
        return files


@dataclass(init=True)
class CustomMessage(Exception):
    """Custom message that will accept message as a parameter and it will print it on the console."""

    message: str = None
    episode_quality: str = None
    workingepisode: str = None

    def print_error(self):
        screenlock.acquire()
        print(ERR, self.message, end=" ")
        screenlock.release()

    def qual_not_found(self):
        screenlock.acquire()
        print(
            f"{ERR}Episode {self.workingepisode} {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} quality not found."
        )
        screenlock.release()

    def use_default_qual(self):
        screenlock.acquire()
        print(
            f"{OK}Trying {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} quality for Episode {self.workingepisode}."
        )
        screenlock.release()
