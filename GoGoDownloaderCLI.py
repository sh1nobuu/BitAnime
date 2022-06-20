from backend import *
import argparse
import os
import requests
from bs4 import BeautifulSoup


def get_archives(archive_file):

    if os.path.isfile(archive_file):
        with open(archive_file, "r") as f:
            return f.read().split()

    else:
        return []


def find_episodes(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    all_episodes = soup.find("ul", {"id": "episode_page"})
    all_episodes = int(all_episodes.get_text().split("-")[-1].strip())
    return all_episodes


def main():
    placeholder = "DUMMY"
    config = config_check()
    parser = argparse.ArgumentParser()
    parser.add_argument("url", metavar="url", type=str)
    parser.add_argument("--archive", metavar="Archive File", type=str)
    parser.add_argument(
        "--quality",
        metavar="download quality",
        choices={"360", "480", "720", "1080"},
        nargs="?",
        const="1080",
        default="1080",
        type=str,
    )
    args = parser.parse_args()

    name = args.url.split("/")[-1]
    title = name.replace("-", " ").title().strip()
    all_episodes = find_episodes(args.url)

    archives = get_archives(args.archive)
    downloader = gogoanime(
        config, name, args.quality, placeholder, all_episodes, 1, all_episodes, title
    )

    episode_links = [link for link in downloader.get_links() if link not in archives]
    dl_links = {}
    for ep in episode_links:
        ep_num = ep.split("-")[-1]
        dl_links[downloader.get_download_link(ep)] = (title, ep_num)
    results = downloader.file_downloader(dl_links)
    failed = []
    with open(args.archive, "a+") as f:
        for ep in episode_links:
            ep_num = ep.split("-")[-1]
            if os.path.join(title, f"{title} Episode {ep_num}.mp4") in results:
                f.write(f"{ep}\n")
            else:
                failed.append(ep)

    with open("logs.txt", "w+") as f:
        for failure in failed:
            f.write(f"{failed} failed to download\n")


if __name__ == "__main__":
    main()
