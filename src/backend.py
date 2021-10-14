# Dependencies
import requests as req
import shutil
import re
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from colorama import Fore
from random import choice
import time


@dataclass(init=True)
class Download:
    name: str
    episode_quality: str
    folder: str
    all_episodes: int
    episode_start: int
    episode_end: int
    printed: bool = False

    def get_links(self, source=None):
        if source is not None:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
            episode_links.insert(0, source)
        else:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
        return episode_links

    def get_download_links(self, episode_link):
        with req.get(episode_link) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            exist = soup.find("h1", {"class": "entry-title"})
            if exist is None:
                # Episode link == 200
                episode_link = soup.find("li", {"class": "dowloads"})
                return episode_link.a.get("href")
            else:
                # Episode link == 404
                episode_link = f"{episode_link}-"
                with req.get(episode_link) as find:
                    soup = BeautifulSoup(find.content, "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    def get_download_urls(self, download_link):
        episode_quality = self.episode_quality
        if episode_quality == "FullHDP":
            episode_quality = "1080P"
        elif episode_quality == "HDP":
            episode_quality = "720P"
        elif episode_quality == "SDP":
            episode_quality = "360P"
        else:
            episode_quality = "1080P"
        with req.get(download_link) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            link = soup.find("div", {"class": "dowload"}, text=re.compile(episode_quality))
            if link is None:
                episode_quality = "720P"
                link = soup.find("div", {"class": "dowload"}, text=re.compile(episode_quality))
                if link is None:
                    episode_quality = "360P"
                    link = soup.find("div", {"class": "dowload"}, text=re.compile(episode_quality))
                    CustomMessage('None', self.episode_quality).qual_not_found()
                    self.episode_quality = link.text.split()[1][1:]
                    CustomMessage('None', self.episode_quality).use_default_qual()
                    self.printed = True
        return [
            download_link.split("+")[-1],
            link.a.get("href"),
        ]

    def random_headers(self):
        desktop_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.47",
                         'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36']
        return {'User-Agent': choice(desktop_agents), "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://goload.one/",
            "Connection": "keep-alive"}

    def download_episodes(self, url):
        client = req.session()
        with client.get(url[1], headers=self.random_headers(), stream=True, timeout=10) as workingurl:
            time.sleep(1)
            episode_name = "EP." + url[0] + ".mp4"
            file_loc = os.path.join(self.folder, episode_name)
            with open(file_loc, "w+b") as file:
                shutil.copyfileobj(workingurl.raw, file)


@dataclass(init=True)
class CustomMessage(Exception):
    """Custom message that will accept message as a parameter and it will print it on the console."""

    message: str = None
    episode_quality: str = None

    def print_error(self):
        print(self.message)

    def qual_not_found(self):
        print(
            f"{Fore.RESET}[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} quality not found."
        )

    def use_default_qual(self):
        print(
            f"{Fore.RESET}[{Fore.GREEN}+{Fore.RESET}] Using {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} as a default quality."
        )
