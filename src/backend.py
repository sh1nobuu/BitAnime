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
        # 200
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
            return None


def get_download_urls(download_link):
    link = requests.get(download_link[1])
    soup = BeautifulSoup(link.content, "html.parser")
    link = soup.find("div", {"class": "mirror_link"}).find_all(
        "div", {"class": "dowload"}
    )
    try:
        if len(link) > 5:
            return [
                download_link[1].split("+")[-1],
                link[int(download_link[0]) + 1].a.get("href"),
            ]
        else:
            return [
                download_link[1].split("+")[-1],
                link[int(download_link[0])].a.get("href"),
            ]
    except IndexError:
        return [download_link[1].split("+")[-1], link[0].a.get("href")]


def download_episodes(url):
    if "cdn" in url[1]:
        header = {
            "Host": "gogo-cdn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://streamani.io/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Te": "trailers",
            "Connection": "close",
        }
        url_resp = requests.get(url[1], headers=header, stream=True)
        episode_name = f"{url[0]}.mp4"
        file_name = os.path.join(folder_path, episode_name)
        with open(file_name, "wb") as file:
            shutil.copyfileobj(url_resp.raw, file)
    else:
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }
        url_resp = requests.get(url, headers=header, stream=True)
        episode_name = f"{url[0]}.mp4"
        file_name = os.path.join(folder_path, episode_name)
        with open(file_name, "wb") as file:
            shutil.copyfileobj(url_resp.raw, file)
        # url_resp = requests.get(url, headers=header, stream=True)
    # try:
    #     episode_name = f"{url.split('/')[-1].split('-')[-2]}.mp4"
    # except IndexError:
    #     episode_name = f"{url_resp.url.split('/')[-1].split('.')[-3]}.mp4"
    # file_name = os.path.join(folder_path, episode_name)
    # with open(file_name, "wb") as file:
    #     shutil.copyfileobj(url_resp.raw, file)
