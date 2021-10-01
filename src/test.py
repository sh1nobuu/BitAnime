# Dependencies
import requests as req
import shutil
import re
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from colorama import Fore


class Status:
    url = "https://goload.one/download?id=MTcxNjIz&typesub=Gogoanime-SUB&title=Sonny+Boy+Episode+12"
    streamsb = "StreamSB"
    gogo = "SDP"

    def check_status(self):
        with req.get(self.url) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            print(self.streamsb)
            self.streamsb = soup.find_all("div", {"class": "mirror_link"})[1].find(
                "div",
                text=re.compile(fr"\b{self.streamsb}\b"),
                attrs={"class": "dowload"},
            )
            print(self.streamsb)
            print(self.gogo)
            self.gogo = soup.find("div", {"class": "mirror_link"}).find(
                "div",
                text=re.compile(fr"\b{self.gogo}\b"),
                attrs={"class": "dowload"},
            )
            print(self.gogo)
        self.print_server_status()

    def print_server_status(self):
        streamsb_status = (
            f"[{Fore.RED}-{Fore.RESET}] 1. StreamSB ({Fore.RED}Unavailable{Fore.RESET})"
            if self.streamsb is None
            else f"[{Fore.GREEN}+{Fore.RESET}] 1. StreamSB ({Fore.GREEN}Available{Fore.RESET})"
        )
        gogo_status = (
            f"[{Fore.RED}-{Fore.RESET}] 2. Gogo Sever ({Fore.RED}Unavailable{Fore.RESET})"
            if self.gogo is None
            else f"[{Fore.GREEN}+{Fore.RESET}] 2. Gogo Server ({Fore.GREEN}Available{Fore.RESET})"
        )
        print(f"[{Fore.GREEN}+{Fore.RESET}] Available Servers")
        print(streamsb_status)
        print(gogo_status)


Status().check_status()
