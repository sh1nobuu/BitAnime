from backend import *
import json
import io
import os


def loadDownloadHistory():
    if os.path.isfile("./downloadHistory.json") and os.access(
        "./downloadHistory.json", os.R_OK
    ):
        return json.load(open("./downloadHistory.json"))
    else:
        print("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join("./", "downloadHistory.json"), "w") as db_file:
            db_file.write(json.dumps([]))
        return json.load(open("./downloadHistory.json"))


def main():
    dh = loadDownloadHistory()

    config = config_check()
    downloader = gogoanime(
        config,
        1,
        config["CLIQuality"],
        "a",
        1,
        1,
        1,
        config["CLIDownloadLocation"],
    )
    list = downloader.get_show_from_bookmark()
    dl_links = {}
    for ep in list:
        print(
            "{OK}Scraping DL for " + ep["showName"] + " Ep " + str(ep["latestEpisode"])
        )
        dl_links[downloader.get_download_link(ep["downloadURL"])] = (
            ep["showName"],
            ep["latestEpisode"],
        )
    result = downloader.file_downloader(dl_links)
    if len(result.errors) > 0:
        while len(result.errors) > 0:
            print(f"{ERR}{len(result.errors)} links failed retrying.")
            print(f"{OK}Re-Scraping Links")
            dl_links.clear()
            for ep in list:
                dl_links[downloader.get_download_link(ep["downloadURL"])] = (
                    ep["showName"],
                    ep["latestEpisode"],
                )
            result = downloader.file_downloader(dl_links, overwrite_downloads=0)


if __name__ == "__main__":
    main()
