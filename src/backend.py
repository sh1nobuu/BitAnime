# Dependencies
import requests as req
import shutil
import re
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass(init=True)
class Download:
    name: str
    episode_quality: str
    episode_number: int
    folder: str

    def get_links(self, source=None):
        if source != None:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}" for i in range(1, self.episode_number + 1)
            ]
            episode_links.insert(0, source)
        else:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}" for i in range(1, self.episode_number + 1)
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
                with req.get(episode_link) as res:
                    soup = BeautifulSoup(res.content, "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    def get_download_urls(self, download_link):
        with req.get(download_link) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            link = soup.find("div", {"class": "mirror_link"}).find(
                "div",
                text=re.compile(fr"\b{self.episode_quality}\b"),
                attrs={"class": "dowload"},
            )
            if link == None:
                link = soup.find("div", {"class": "mirror_link"}).find(
                    "div", {"class": "dowload"}
                )
        return [download_link.split("+")[-1], link.a.get("href")]

    def download_episodes(self, url):
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }
        with req.get(url[1], headers=header, stream=True) as res:
            episode_name = f"EP.{url[0]}.mp4"
            file_loc = os.path.join(self.folder, episode_name)
            with open(file_loc, "wb") as file:
                shutil.copyfileobj(res.raw, file, 8192)


class InvalidInputValue(Exception):
    """Raise when custom_episode_number is equal to 0 or custom_episode_number is greater than episode_number"""

    pass
