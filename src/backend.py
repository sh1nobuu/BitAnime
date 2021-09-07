import requests
import os
import shutil
from bs4 import BeautifulSoup

folder_path = ""


def get_path(folder):
    global folder_path
    folder_path = folder


def get_links(name, episode_number, source=None):
    if source is not None:
        source_ep = f"https://gogoanime.pe/{name}-episode-"
        episode_links = [f"{source_ep}{i}" for i in range(1, int(episode_number) + 1)]
        episode_links.insert(0, source)
    else:
        source_ep = f"https://gogoanime.pe/{name}-episode-"
        episode_links = [f"{source_ep}{i}" for i in range(1, int(episode_number) + 1)]
    return episode_links


def get_download_links(episode_link):
    episode_link_resp = requests.get(episode_link)
    soup = BeautifulSoup(episode_link_resp.content, "html.parser")
    exist = soup.find("h1", {"class": "entry-title"})
    if exist is None:
        # 202
        link = soup.find("li", {"class": "dowloads"})
        return link.a.get("href")
    else:
        # 404
        episode_link = f"{episode_link}-"
        episode_link_resp = requests.get(episode_link)
        soup = BeautifulSoup(episode_link_resp.content, "html.parser")
        exist = soup.find("h1", {"class": "entry-title"})
        if exist is None:
            link = soup.find("li", {"class": "dowloads"})
            return link.a.get("href")
        else:
            pass


def get_download_urls(download_link):
    link = requests.get(download_link)
    soup = BeautifulSoup(link.content, "html.parser")
    link = soup.find_all("div", {"class": "dowload"})
    return link[0].a.get("href")


def download_episodes(url):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }
    url_resp = requests.get(url, headers=header, stream=True)
    episode_name = f"{url.split('-')[-2]}.mp4"
    file_name = os.path.join(folder_path, episode_name)
    with open(file_name, "wb") as file:
        shutil.copyfileobj(url_resp.raw, file)
