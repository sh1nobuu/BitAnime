import re
import requests
import json
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from colorama import Fore
from parfive import Downloader
from threading import Semaphore
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
)


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
        logging.info("Config.json loaded")
        with open("./config.json", "r") as f:
            CONFIG = json.load(f)
        if not "GoGoAnime_Username" in CONFIG or len(CONFIG["GoGoAnime_Username"]) == 0:
            logging.error("GoGoAnime_Username not set in config.json")
            print("GoGoAnime_Username not set in config.json")
            exit(0)
        else:
            if (
                not "GoGoAnime_Password" in CONFIG
                or len(CONFIG["GoGoAnime_Password"]) == 0
            ):
                logging.error("GoGoAnime_Password not set in config.json")
                print("GoGoAnime_Password not set in config.json")
                exit(0)
            else:
                logging.info(
                    "Config loaded and "
                    + CONFIG["GoGoAnime_Username"]
                    + " username found"
                )
                return CONFIG
    else:
        logging.error("config.json not found")
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
class gogoanime:
    config: object
    name: str
    episode_quality: str
    folder: str
    all_episodes: int
    episode_start: int
    episode_end: int
    title: str
    printed: bool = False

    def get_gogoanime_auth_cookie(self):
        session = requests.session()
        page = session.get(
            f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/login.html"
        )
        soup = BeautifulSoup(page.content, "html.parser")
        meta_path = soup.select('meta[name="csrf-token"]')
        csrf_token = meta_path[0].attrs["content"]

        url = f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/login.html"
        payload = f"email={self.config['GoGoAnime_Username']}&password={self.config['GoGoAnime_Password']}&_csrf={csrf_token}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "authority": "gogo-cdn.com",
            "referer": f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/",
            "content-type": "application/x-www-form-urlencoded",
        }
        session.headers = headers

        r = session.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            return session.cookies.get_dict().get("auth")
        else:
            print("ldldl")

    def user_logged_in_check(
        self,
    ):
        page = requests.get(
            f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/one-piece-episode-1",
            cookies=dict(auth=gogoanime.get_gogoanime_auth_cookie(self)),
        )
        soup = BeautifulSoup(page.content, "html.parser")
        loginCheck = soup(text=re.compile("Logout"))
        if len(loginCheck) == 0:
            raise Exception(
                "User is not logged in, make sure account has been activated"
            )

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
            cookies=dict(auth=gogoanime.get_gogoanime_auth_cookie(self)),
        )
        quality_arr = ["1080", "720", "640", "480"]
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            for link in soup.find_all(
                "a", href=True, string=re.compile(self.episode_quality)
            ):
                return link["href"]
            else:
                ep_num = url.rsplit("-", 1)[1]
                print(
                    f"{self.episode_quality} not found for ep{ep_num} checking for next best"
                )
                for q in quality_arr:
                    for link in soup.find_all("a", href=True, string=re.compile(q)):
                        print(f"{q} found.")
                        return link["href"]
        except:
            print("No matching download found")

    def file_downloader(self, file_list: dict, overwrite_downloads: bool = None):
        """[summary]

        Args:
            file_list (dict): [description]
            overwrite_downloads (bool, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        if overwrite_downloads is None:
            overwrite = self.config["OverwriteDownloads"]
        else:
            overwrite = overwrite_downloads
        dl = Downloader(
            max_conn=max_concurrent_downloads(self.config["MaxConcurrentDownloads"]),
            overwrite=overwrite,
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
            if link is not None:
                dl.enqueue_file(
                    link,
                    path=f"./{self.title}",
                )

        files = dl.download()
        return files

    def get_show_from_bookmark(self):
        print(f"{IN}Loading shows from bookmarks")
        bookmarkList = []
        a = dict(auth=gogoanime.get_gogoanime_auth_cookie(self))
        resp = requests.get(
            f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/user/bookmark",
            cookies=a,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("div", attrs={"class": "article_bookmark"})
        splitTableLines = table.text.split("Remove")
        for rows in splitTableLines:
            fullRow = " ".join(rows.split())
            if "Anime name" in fullRow:
                fullRow = fullRow.replace("Anime name Latest", "")
                splitRow = fullRow.split("Latest")
            elif fullRow == "Status":
                break
            else:
                fullRow = fullRow.replace("Status ", "")
                splitRow = fullRow.split("Latest")
            animeName = splitRow[0].strip().encode("ascii", "ignore").decode()
            animeName = re.sub("[^A-Za-z0-9 ]+", "", animeName)
            animeDownloadName = animeName.replace(" ", "-").lower()
            episodeNum = splitRow[-1].split()[-1]
            bookmarkList.append(
                {
                    "showName": animeName,
                    "latestEpisode": int(episodeNum),
                    "downloadURL": f"https://gogoanime.{self.config['CurrentGoGoAnimeDomain']}/{animeDownloadName}-episode-{str(episodeNum)}",
                }
            )
        with open("bookmarkList.json", "w") as f:
            json.dump(bookmarkList, f)
        return bookmarkList


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
