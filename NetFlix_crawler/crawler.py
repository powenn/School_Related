"""
runtime error and others error will return -1
ctrl+C will return -2
"""

import os
import time
import requests
import openpyxl
from bs4 import BeautifulSoup

DEBUG = True
CURRENT_DIR = os.path.dirname(__file__)
DATA_FILENAME = "data.txt"
OUTPUT_FILENAME = "output.xlsx"
DATA_PATH = f"{CURRENT_DIR}/{DATA_FILENAME}"
OUTPUT_PATH = f"{CURRENT_DIR}/{OUTPUT_FILENAME}"
BASE_URL = "https://www.netflix.com/tw/title/"


def DebugPrint(message: str):
    if DEBUG:
        print(f"[DEBUG] : {message}")


def getAnswer(text):
    try:
        return input(text)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed, aborting")
        exit(-2)


def DataFileExist() -> bool:
    DebugPrint(f"data file should be locate at {DATA_PATH}")
    if (not os.path.exists(DATA_PATH)) or (not os.path.isfile(DATA_PATH)):
        print(f"{DATA_FILENAME} not int {CURRENT_DIR} or not a file")
        return False
    return True


def OutputFileExist() -> bool:
    DebugPrint(f"output file should be located at {OUTPUT_PATH}")
    if (not os.path.exists(OUTPUT_PATH)) or (not os.path.isfile(OUTPUT_PATH)):
        print(f"{OUTPUT_FILENAME} not in {CURRENT_DIR} or not a file")
        return False
    return True


class Anime:
    id: str
    name: str
    release_year: str
    maturity_number: str
    title_genre: str
    starring: list[str]
    seasons: list[str]
    downloadable_info: str
    detailed_genres: list[str]
    tags: list[str]
    actors: list[str]
    has_multi_seasons: bool

    def __init__(self, id, name, release_year, maturity_number, title_genre, starring, seasons, downloadable_info, detailed_genres, tags, actors, has_multi_seasons):
        self.id = id
        self.name = name
        self.release_year = release_year
        self.maturity_number = maturity_number
        self.title_genre = title_genre
        self.starring = starring
        self.downloadable_info = downloadable_info
        self.detailed_genres = detailed_genres
        self.tags = tags
        self.actors = actors
        self.has_multi_seasons = has_multi_seasons
        self.seasons = seasons

    def printInfo(self):
        print(f"Id : {self.id}\nAnime name : {self.name}\nRelease year : {self.release_year}\nMaturity number : {self.maturity_number}\nTitle genre : {self.title_genre}\nStarring : {self.starring}\nDownloadable info : {self.downloadable_info}\nDetailed genres : {self.detailed_genres}\nTags : {self.tags}\nActors : {self.actors}\nHas multi seasons : {self.has_multi_seasons}\nSeasons : {self.seasons}")


def hasNetworkConnection() -> bool:
    try:
        request = requests.get("https://google.com", timeout=3)
        return request.status_code == requests.codes.ok
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False


def GetStatusAndResponce(url: str) -> tuple:
    r = requests.get(url)
    return (r.status_code, r.text)


def processData() -> list[Anime]:
    data = open(DATA_PATH, "r")
    data_list = list(map(lambda x: x.replace("\n", ""), data.readlines()))
    anime_list = []
    DebugPrint(f"Read data from data.txt\n{data_list}")
    for dl in data_list:
        id, name = dl.split(",")
        full_url = BASE_URL+id
        DebugPrint(f"id : {id} , name : {name} , full url : {full_url}")
        statAndResponce = GetStatusAndResponce(full_url)
        if statAndResponce[0] == requests.codes.ok:
            anime_list.append(processHtml(id, statAndResponce[1]))
        else:
            print("error occurred :( ")
    return anime_list


def processHtml(id: str, text: str) -> Anime:
    sp = BeautifulSoup(text, "html.parser")
    name = sp.find("h1", class_="title-title").text.strip()
    release_year = sp.find(
        "span", class_="title-info-metadata-item item-year").text.strip()
    maturity_number = sp.find("span", class_="maturity-number").text.strip()
    title_genre = sp.find(
        "a", class_="title-info-metadata-item item-genre").text.strip()
    starring = sp.find(
        "span", class_="title-data-info-item-list").text.strip().split(",")
    downloadable_info = sp.find(
        "span", class_="more-details-item item-download").text.strip()

    detailed_genres = []
    detailed_genres_sp = sp.findAll(
        "div", class_="more-details-item-container")
    for dg in detailed_genres_sp:
        span_g = dg.findAll("span", class_="more-details-item item-genres")
        for g in span_g:
            detailed_genres.append(g.text.strip().replace("，", ""))

    tags = []
    tags_sp = sp.findAll("div", class_="more-details-item-container")
    for tag in tags_sp:
        span_t = tag.findAll("span", class_="more-details-item item-mood-tag")
        for t in span_t:
            tags.append(t.text.replace("，", ""))

    actors = []
    actors_sp = sp.findAll("div", class_="more-details-cell cell-cast")
    for ac in actors_sp:
        container_a = ac.findAll("div", class_="more-details-item-container")
        for ca in container_a:
            span_a = ca.findAll("span", class_="more-details-item item-cast")
            for a in span_a:
                actors.append(a.text.strip())

    has_multi_seasons = True if sp.find_all(
        "div", class_="select-arrow medium") else False
    if has_multi_seasons:
        seasons = []
        seasons_sp = sp.find(
            "select", class_="ui-select medium").findAll("option")
        for ssp in seasons_sp:
            seasons.append(ssp.text.strip())
    else:
        seasons = [sp.find("div", class_="select-label").text.strip()]

    DebugPrint(
        f"{id,name, release_year, maturity_number, title_genre, starring, seasons, downloadable_info, detailed_genres, tags, actors, has_multi_seasons}")

    return Anime(id, name, release_year, maturity_number, title_genre, starring, seasons, downloadable_info, detailed_genres, tags, actors, has_multi_seasons)


def writeToOutput(anime_list: list[Anime]):
    print(f"Writing to {OUTPUT_PATH} , please wait a moment")
    workbook = openpyxl.Workbook()
    sheet = workbook.worksheets[0]
    title = ["URL", "Id", "Name", "Release year", "Maturity number", "Title genre", "Starring",
             "Season", "Downloadable info", "Detailed genres", "Tags", "Actors", "Has multi seasons"]
    sheet.append(title)
    """
    starring: list[str]
    detailed_genres: list[str]
    tags: list[str]
    actors: list[str]
    seasons: list[str]
    """
    for anime in anime_list:
        for st in anime.starring:
            for dg in anime.detailed_genres:
                for t in anime.tags:
                    for a in anime.actors:
                        for s in anime.seasons:
                            sheet.append([BASE_URL+anime.id, anime.id, anime.name, anime.release_year, anime.maturity_number,
                                          anime.title_genre, st, s, anime.downloadable_info, dg, t, a, anime.has_multi_seasons])
    time.sleep(1)
    print(f"total rows value : {sheet.max_row}")
    workbook.save(OUTPUT_PATH)


if __name__ == "__main__":
    DebugPrint("Here is main")
    DebugPrint(f"Py script running in {CURRENT_DIR}")
    if not DataFileExist():
        exit(-1)
    DebugPrint("Passed data file check")
    if not hasNetworkConnection():
        print("no network connection")
        exit(-1)
    else:
        DebugPrint("has network connection")
    if OutputFileExist():
        ans = getAnswer(
            "Overwrite the output file ?\n( y for overwrite ctrl+c will abprt it and exit the script \nand others responce will attempt you to give a name for new output file name ) : ")
        if ans.lower() == "y" or ans.lower() == "yes":
            print("Output file will be overwrite")
        else:
            new_name = getAnswer("Enter a new name for new output file : ")
            OUTPUT_FILENAME = f"{new_name}.xlsx"
            OUTPUT_PATH = f"{CURRENT_DIR}/{OUTPUT_FILENAME}"
    anime_list = processData()
    if DEBUG:
        for anime in anime_list:
            anime.printInfo()
    writeToOutput(anime_list)
