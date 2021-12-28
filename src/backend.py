# Standard modules

import re
import os
import shutil
import asyncio
from dataclasses import dataclass

# External modules

import requests as req
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from colorama import Fore


@dataclass
class Download:
    name: str
    episode_quality: str
    folder: str
    episode_start: int
    episode_end: int
    server_number: int
    loop: object

    def get_links(self, source: str = None) -> list[str]:
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

    async def get_download_links(self, episode_links: list) -> list[str]:
        server = ServerList(self.server_number).return_server()
        server = server(None, None)
        async with ClientSession(loop=self.loop) as session:
            tasks = [
                server.get_download_links(session, episode_link)
                for episode_link in episode_links
            ]
            download_links = await asyncio.gather(*tasks)
        return download_links

    async def get_download_urls(self, download_links: list) -> list[list[str, str]]:
        server = ServerList(self.server_number).return_server()
        server = server(self.loop, self.episode_quality)
        async with ClientSession(loop=self.loop) as session:
            tasks = [
                server.get_download_urls(session, download_link)
                for download_link in download_links
            ]
            download_urls = await asyncio.gather(*tasks)
        return download_urls

    def download_episodes(self, download_url: str) -> None:
        print(download_url)
        header = {
            "Host": "gogo-cdn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://gogoplay1.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Te": "trailers",
            "Connection": "close",
        }
        with req.get(download_url[1], headers=header, stream=True) as response:
            data = response.raw
            ep_name = f"EP.{download_url[0]}.mp4"
            file_loc = os.path.join(self.folder, ep_name)
            with open(file_loc, "wb") as file:
                shutil.copyfileobj(data, file)


@dataclass
class StreamSBServer:
    loop: object = None
    episode_quality: str = None
    printed: bool = False
    streamsb: str = "StreamSB"

    async def get_download_links(self, session: object, episode_link: str) -> str:
        async with session.get(episode_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            exist = soup.find("h1", {"class": "entry-title"})
            if exist is None:
                # Episode link == 200
                episode_link = soup.find("li", {"class": "dowloads"})
                return episode_link.a.get("href")
            else:
                # Episode link == 404
                episode_link = f"{episode_link}-"
                async with session.get(episode_link) as response:
                    soup = BeautifulSoup(await response.content.read(), "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    async def get_real_download_urls(self, link: str) -> str:
        url = "https://sbplay.one/dl?op=download_orig&id={}&mode={}&hash={}"
        async with ClientSession(loop=self.loop) as session:
            async with session.get(link) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                download_link = soup.find("table").find(
                    "a", text=re.compile(fr"\b{self.episode_quality}\b")
                )
                if download_link is None:
                    download_link = soup.find("table").find_all("a", {"href": "#"})[0]
                    if not self.printed:
                        CustomMessage(None, self.episode_quality).qual_not_found()
                        self.episode_quality = download_link.text
                        CustomMessage(None, self.episode_quality).use_default_qual()
                        self.printed = True
                download_link = download_link.get("onclick").split("download_video")[-1]
                download_link = (
                    download_link.replace("(", "")
                    .replace(")", "")
                    .replace("'", "")
                    .split(",")
                )
                download_link = url.format(
                    download_link[0], download_link[1], download_link[2]
                )
                #!DELETE THIS LATER
                print(download_link)
                async with session.get(download_link) as response:
                    soup = BeautifulSoup(await response.content.read(), "html.parser")
                    direct_link = soup.find("span").find("a").get("href")
        return direct_link

    async def get_download_urls(
        self, session: object, download_link: str
    ) -> list[str, str]:
        async with session.get(download_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            link = soup.find_all("div", {"class": "mirror_link"})[-1].find(
                "div",
                text=re.compile(fr"\b{self.streamsb}\b"),
                attrs={"class": "dowload"},
            )
            real_download_link = await self.get_real_download_urls(link.a.get("href"))
        return [
            download_link.split("+")[-1],
            real_download_link,
        ]


@dataclass
class GogoOneServer:
    loop: object = None
    episode_quality: str = None
    printed: bool = False

    async def get_download_links(self, session: object, episode_link: str) -> str:
        async with session.get(episode_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            exist = soup.find("h1", {"class": "entry-title"})
            if exist is None:
                # Episode link == 200
                episode_link = soup.find("li", {"class": "dowloads"})
                return episode_link.a.get("href")
            else:
                # Episode link == 404
                episode_link = f"{episode_link}-"
                async with session.get(episode_link) as response:
                    soup = BeautifulSoup(await response.content.read(), "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    async def get_download_urls(
        self, session: object, download_link: str
    ) -> list[str, str]:
        async with session.get(download_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            link = soup.find_all("div", {"class": "mirror_link"})[-1].find(
                "div",
                text=re.compile(fr"\b{self.episode_quality}\b"),
                attrs={"class": "dowload"},
            )

        return [
            download_link.split("+")[-1],
            link.a.get("href"),
        ]


@dataclass
class GogoTwoServer:
    loop: object = None
    episode_quality: str = None
    printed: bool = False

    async def get_download_links(self, session: object, episode_link: str) -> str:
        async with session.get(episode_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            exist = soup.find("h1", {"class": "entry-title"})
            if exist is None:
                # Episode link == 200
                episode_link = soup.find("li", {"class": "dowloads"})
                return episode_link.a.get("href")
            else:
                # Episode link == 404
                episode_link = f"{episode_link}-"
                async with session.get(episode_link) as response:
                    soup = BeautifulSoup(await response.content.read(), "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    async def get_download_urls(
        self, session: object, download_link: str
    ) -> list[str, str]:
        async with session.get(download_link) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            link = soup.find_all("div", {"class": "mirror_link"})[0].find(
                "div",
                text=re.compile(fr"\b{self.episode_quality}\b"),
                attrs={"class": "dowload"},
            )
            #!DELETE THIS LATER
            print(link.a.get("href"))

        return [
            download_link.split("+")[-1],
            link.a.get("href"),
        ]


class ServerList:
    def __init__(self, server_number: int):
        self.server_number = server_number
        self.server_list: list = [StreamSBServer, GogoOneServer, GogoTwoServer]
        self.server_qualities: dict = {
            "StreamSB": ["Low quality", "Normal quality", "High quality"],
            "Gogo_One": ["SDP", "HDP", "FullHDP"],
            "Gogo_Two": ["360P", "480P", "720P", "1080P"],
        }

    def return_server(self) -> str:
        return self.server_list[self.server_number - 1]

    def return_server_qualities(self, server: int) -> dict[str]:
        return self.server_qualities[server]


class ServerStatus:
    url = "https://gogoplay1.com/download?id=MTcxNjIz&typesub=Gogoanime-SUB&title=Sonny+Boy+Episode+12"
    streamsb = "StreamSB"
    gogo_one = "SDP"
    gogo_two = "360P"

    async def check_status(self) -> list[str]:
        async with ClientSession() as session:
            async with session.get(self.url) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                self.streamsb = soup.find_all("div", {"class": "mirror_link"})[1].find(
                    "div",
                    text=re.compile(fr"\b{self.streamsb}\b"),
                    attrs={"class": "dowload"},
                )
                self.gogo_one = soup.find_all("div", {"class": "mirror_link"})[0].find(
                    "div",
                    text=re.compile(fr"\b{self.gogo_one}\b"),
                    attrs={"class": "dowload"},
                )
                self.gogo_two = soup.find_all("div", {"class": "mirror_link"})[0].find(
                    "div",
                    text=re.compile(fr"\b{self.gogo_two}\b"),
                    attrs={"class": "dowload"},
                )
        self.print_server_status()
        return [self.streamsb, self.gogo_one, self.gogo_two]

    def print_server_status(self) -> None:
        streamsb_status = (
            f"[{Fore.RED}-{Fore.RESET}] 1. StreamSB ({Fore.RED}Unavailable{Fore.RESET})"
            if self.streamsb is None
            else f"[{Fore.GREEN}+{Fore.RESET}] 1. StreamSB ({Fore.GREEN}Available{Fore.RESET})"
        )
        gogo_status_one = (
            f"[{Fore.RED}-{Fore.RESET}] 2. Gogo Sever 1({Fore.RED}Unavailable{Fore.RESET})"
            if self.gogo_one is None
            else f"[{Fore.GREEN}+{Fore.RESET}] 2. Gogo Server 1({Fore.GREEN}Available{Fore.RESET})"
        )
        gogo_status_two = (
            f"[{Fore.RED}-{Fore.RESET}] 3. Gogo Sever 2({Fore.RED}Unavailable{Fore.RESET})"
            if self.gogo_two is None
            else f"[{Fore.GREEN}+{Fore.RESET}] 3. Gogo Server 2({Fore.GREEN}Available{Fore.RESET})"
        )
        print(f"[{Fore.GREEN}+{Fore.RESET}] Available Servers")
        print(streamsb_status)
        print(gogo_status_one)
        print(gogo_status_two)


@dataclass
class CustomMessage(Exception):
    """Custom message that will accept message as a parameter and it will print it on the console."""

    message: str = None
    episode_quality: str = None

    def print_error(self) -> None:
        print(self.message)

    def qual_not_found(self) -> None:
        print(
            f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} quality not found."
        )

    def use_default_qual(self) -> None:
        print(
            f"[{Fore.GREEN}+{Fore.RESET}] Using {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} as a default quality."
        )
