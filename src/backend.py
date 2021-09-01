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


def get_download_links(episode_links):
    download_links = []
    for episode_link in episode_links:
        episode_link_resp = requests.get(episode_link)
        soup = BeautifulSoup(episode_link_resp.content, "html.parser")
        links = soup.find("li", {"class": "dowloads"})
        for link in links:
            link = link.get("href")
            download_links.append(link)
    return download_links


def get_download_urls(download_links, bool):
    download_urls = []
    for link in download_links:
        link = requests.get(link)
        soup = BeautifulSoup(link.content, "html.parser")
        download_link = soup.find_all("div", {"class": "dowload"})
        download_urls.append(download_link[0].a.get("href"))
        if bool:
            conv_download_urls = {
                episode_title: url for episode_title, url in enumerate(download_urls)
            }
        else:
            conv_download_urls = {
                episode_title + 1: url
                for episode_title, url in enumerate(download_urls)
            }
        conv_download_urls = sorted(set(conv_download_urls.items()))
    return conv_download_urls


def download_episodes(url):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }
    url_resp = requests.get(url[1], headers=header, stream=True)
    file_name = os.path.join(folder_path, f"{url[0]}.mp4")
    with open(file_name, "wb") as file:
        shutil.copyfileobj(url_resp.raw, file)
