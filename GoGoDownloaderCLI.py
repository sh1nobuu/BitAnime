import json
import io
import os
import re
from backend import *


def renameFile(filename: str):
    """_summary_

    Args:
        filename (str): _description_

    Returns:
        _type_: _description_
    """
    newFileName = "".join(re.split("\(|\)|\[|\]", filename)[::2])
    try:
        os.rename(filename, newFileName)
        return True
    except OSError as err:
        return err


def loadDownloadHistory():
    """Loads the downloadHistory.json, creates it if it doesn't exist

    Returns:
        object: download history list
    """
    if os.path.isfile("./downloadHistory.json") and os.access(
        "./downloadHistory.json", os.R_OK
    ):
        return json.load(open("./downloadHistory.json"))
    else:
        with io.open(os.path.join("./", "downloadHistory.json"), "w") as db_file:
            db_file.write(json.dumps([]))
        return json.load(open("./downloadHistory.json"))


def writeShowToDownloadHistory(showName: str, downloadHistory: list):
    """Writes the showName and latestEpisode to the downloadHistory.json file

    Args:
        showName (str): _description_
        downloadHistory (list): _description_

    Returns:
        _type_: _description_
    """
    downloadHistory.append(showName)
    with io.open(os.path.join("./", "downloadHistory.json"), "w") as db_file:
        db_file.write(json.dumps(downloadHistory))
    return json.load(open("./downloadHistory.json"))


def readDownloadHistory(fileNameObject: object, downloadHistory: list):
    """Reads the downloadHistory.json and checks if the fileName is present

    Args:
        fileNameObject (str): _description_
        downloadHistory (list): _description_

    Returns:
        _type_: _description_
    """
    dhFileName = (
        fileNameObject["showName"] + " - " + str(fileNameObject["latestEpisode"])
    )
    if dhFileName not in downloadHistory:
        writeShowToDownloadHistory(dhFileName, downloadHistory)
        return False
    else:
        return True


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
        if readDownloadHistory(ep, dh):
            showName = ep["showName"] + " - " + str(ep["latestEpisode"])
            print(f"{IN}{showName} already downloaded")
        else:
            print(
                f"{IN}Scraping DL for "
                + ep["showName"]
                + " Ep "
                + str(ep["latestEpisode"])
            )
            dl_links[downloader.get_download_link(ep["downloadURL"])] = (
                ep["showName"],
                ep["latestEpisode"],
            )
    result = downloader.file_downloader(dl_links)
    if config["CleanUpFileName"]:
        for file in result.data:
            renameFile(file)
    if len(result.errors) > 0:
        while len(result.errors) > 0:
            print(f"{ERR}{len(result.errors)} links failed retrying.")
            print(f"{IN}Re-Scraping Links")
            dl_links.clear()
            for ep in list:
                dl_links[downloader.get_download_link(ep["downloadURL"])] = (
                    ep["showName"],
                    ep["latestEpisode"],
                )
            result = downloader.file_downloader(dl_links, overwrite_downloads=0)
            if config["CleanUpFileName"]:
                for file in result.data:
                    renameFile(file)


if __name__ == "__main__":
    main()
