# Standard modules

import ctypes
import os
import asyncio
import concurrent.futures

# External modules

import colorama
from colorama import Fore
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import thread_map
from backend import Download, CustomMessage, ServerStatus

colorama.init(autoreset=True)


class BitAnime:
    OK = f"[{Fore.GREEN}+{Fore.RESET}] "
    ERR = f"[{Fore.RED}-{Fore.RESET}] "
    IN = f"[{Fore.LIGHTBLUE_EX}>{Fore.RESET}] "

    loop = asyncio.get_event_loop()

    def app_banner(self) -> None:
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

    async def check_anime_status(self, name: str) -> int:
        url = f"https://gogoanime.pe/category/{name}"
        async with ClientSession() as session:
            async with session.get(url) as response:
                return response.status

    def input_anime_name(self) -> str:
        while True:
            name = input(f"{self.IN}Enter anime name > ").lower()
            if "-" in name:
                title = name.replace("-", " ").title().strip()
            else:
                title = name.title().strip()

            status = self.loop.run_until_complete(self.check_anime_status(name))

            if status == 200:
                return title, name
            else:
                print(f"{self.ERR}Error 404: Anime not found. Please try again.")

    def choose_server(self, servers_status: int) -> int:
        while True:
            try:
                server = int(input(f"{self.IN}Choose a server > "))

                if servers_status[server - 1] is None:
                    print(
                        f"{self.ERR}Server not available. Please pick a different server."
                    )
                else:
                    return server
            except ValueError:
                print(f"{self.ERR}Invalid input. Please try again.")
            except IndexError:
                print(
                    f"{self.ERR}Server number '{server}' does not exist. Please try again."
                )

    def print_qualities(self, qualities: list, server: int) -> None:
        for number, quality in enumerate(qualities[server - 1], 1):
            print(f"{self.OK}{number}. {quality}")

    def choose_quality(self, server: int) -> str:
        qualities = [
            ["Low quality", "Normal quality", "High quality"],
            ["SDP", "HDP", "FullHDP"],
            ["360P", "480P", "720P", "1080P"],
        ]
        self.print_qualities(qualities, server)
        while True:
            try:
                quality = int(input(f"{self.IN}Enter episode quality > "))
                if quality > len(qualities[server - 1]):
                    print(
                        f"{self.ERR}Quality number {quality} does not exist. Please try again."
                    )
                else:
                    return qualities[server - 1][quality - 1]
            except ValueError:
                print(f"{self.ERR}Invalid input. Please try again.")

    def create_folder(self, title: str) -> str:
        folder = os.path.join(os.getcwd(), title)
        if not os.path.exists(folder):
            os.mkdir(folder)
        return folder

    async def get_number_of_episodes(self, name: str) -> int:
        url = f"https://gogoanime.pe/category/{name}"
        async with ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                all_episodes = soup.find("ul", {"id": "episode_page"})
                all_episodes = int(all_episodes.get_text().split("-")[-1].strip())
        return all_episodes

    def print_anime_info(
        self, server: str, title: str, all_episodes: int, episode_quality: str
    ) -> None:
        print(f"{self.OK}Server: {Fore.LIGHTCYAN_EX}{server}")
        print(f"{self.OK}Title: {Fore.LIGHTCYAN_EX}{title}")
        print(f"{self.OK}Episode/s: {Fore.LIGHTCYAN_EX}{all_episodes}")
        print(f"{self.OK}Quality: {Fore.LIGHTCYAN_EX}{episode_quality}")

    async def check_episode_zero(self, name: str, choice: str) -> str or None:
        url = f"https://gogoanime.pe/{name}"
        async with ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.content.read(), "html.parser")
                episode_zero_status = soup.find("h1", {"class": "entry-title"})
        if choice == "n" or episode_zero_status is not None:
            return None
        else:
            return url

    def dynamic_episode(self, all_episodes: int) -> int:
        while True:
            try:
                episode_start = int(input(f"{self.IN}Episode start > "))
                episode_end = int(input(f"{self.IN}Episode end > "))
                if episode_start <= 0 or episode_end <= 0:
                    CustomMessage(
                        f"{self.ERR}episode_start or episode_end cannot be less than or equal to 0"
                    ).print_error()
                elif episode_start >= all_episodes or episode_end > all_episodes:
                    CustomMessage(
                        f"{self.ERR}episode_start or episode_end cannot be more than {all_episodes}"
                    ).print_error()
                elif episode_end <= episode_start:
                    CustomMessage(
                        f"{self.ERR}episode_end cannot be less than or equal to episode_start"
                    ).print_error()
                else:
                    return episode_start, episode_end
            except ValueError:
                print(f"{self.ERR}Invalid input. Please try again.")

    def download_all_or_not(self, all_episodes: int) -> int and str:
        while True:
            choice = input(
                f"{self.IN}Do you want to download all episode? (y/n) > "
            ).lower()
            if choice == "y":
                return 1, all_episodes, choice
            elif choice == "n":
                episode_start, episode_end = self.dynamic_episode(all_episodes)
                return episode_start, episode_end, choice
            else:
                print(f"{self.ERR}Invalid input. Please try again.")

    def get_download_list(self, episode_links: list, download: object) -> list[str]:
        download_links = self.loop.run_until_complete(
            download.get_download_links(episode_links)
        )
        download_urls = self.loop.run_until_complete(
            download.get_download_urls(download_links)
        )
        return download_urls

    def main(self):
        self.app_banner()
        server_status = self.loop.run_until_complete(ServerStatus().check_status())
        server = self.choose_server(server_status)
        title, name = self.input_anime_name()
        episode_quality = self.choose_quality(server)
        folder = self.create_folder(title)
        all_episodes = self.loop.run_until_complete(self.get_number_of_episodes(name))
        self.print_anime_info(server, title, all_episodes, episode_quality)
        if all_episodes > 1:
            (
                episode_start,
                episode_end,
                choice,
            ) = self.download_all_or_not(all_episodes)
            episode_zero_url = self.loop.run_until_complete(
                self.check_episode_zero(name, choice)
            )
        else:
            episode_start = 1
            episode_end = all_episodes
            episode_zero_url = None
        download = Download(
            name, episode_quality, folder, episode_start, episode_end, server, self.loop
        )
        episode_links = download.get_links(episode_zero_url)
        download_urls = self.get_download_list(episode_links, download)
        print(
            f"{self.OK}Downloading {Fore.LIGHTCYAN_EX}{len(download_urls)}{Fore.RESET} episode/s"
        )
        thread_map(download.download_episodes, download_urls, total=len(download_urls))


if __name__ == "__main__":
    BitAnime().main()
