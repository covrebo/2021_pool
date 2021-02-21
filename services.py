import collections
import csv
import os
from typing import List

import bs4
import requests

Picks = collections.namedtuple('Picks', 'picker, picks')
WeeklyPoints = collections.namedtuple('WeeklyPoints', 'picker, d1, d1_pts, d2, d2_pts, d3, d3_pts, bonus, total_points,')


#################
###  SCORING  ###
#################

# calculate the weekly points for each driver
def weekly_points(race: int, picks: List[Picks], results: List) -> List[WeeklyPoints]:
    results_dict = {}
    for r in results[1:]:
        results_dict[f'{r[2]}'] = {
            f'{results[0][0]}': r[0],
            f'{results[0][1]}': r[1],
            f'{results[0][2]}': r[2],
            f'{results[0][7]}': r[7],
        }

    # TODO: might want to refactor this to a dictionary versus named tuple
    wkly_points = []

    for pick in picks:
        bonus = input(f"Weekly bonus points for {pick.picker}: ")
        wkly_points.append(WeeklyPoints(picker=pick.picker, d1=pick.picks[0], d1_pts=results_dict[f'{pick.picks[0]}']['PTS'], d2=pick.picks[1], d2_pts=results_dict[f'{pick.picks[1]}']['PTS'], d3=pick.picks[2], d3_pts=results_dict[f'{pick.picks[2]}']['PTS'], bonus=bonus, total_points=(int(results_dict[f'{pick.picks[0]}']['PTS']) + int(results_dict[f'{pick.picks[1]}']['PTS']) + int(results_dict[f'{pick.picks[2]}']['PTS']) + int(bonus))))
    # 0, (int(results_dict[f'{pick.picks[0]}']['PTS']) + int(results_dict[f'{pick.picks[1]}']['PTS']) + int(results_dict[f'{pick.picks[2]}']['PTS']), 0)

    wkly_points = sorted(wkly_points, key=lambda x: x.total_points, reverse=True)


    # print(race)
    # print(picks)
    # print(results)
    # print(results_dict)
    # print(wkly_points)
    # for pick in wkly_points:
    #     print(f"{pick.picker} finished with {pick.total_points} points.")
    return wkly_points

#####################
###  WEBSCRAPING  ###
#####################

def pull_site(url):
    raw_site = requests.get(url)
    try:
        raw_site.raise_for_status()
    except:
        print(
            "There was an error trying to retrieve the data from the results page.")
        return None

    return raw_site


def scrape(site):
    data_list = []

    soup = bs4.BeautifulSoup(site.text, 'html.parser')
    # get the table
    table = soup.find_all("tr")
    for row in table[1:]:
        temp = row.find_all("td")
        list = []
        for tag in temp:
            list.append(tag.get_text())
        data_list.append(list)

    return data_list


#############
###  CSV  ###
#############

def import_picks_from_csv(race: str) -> List[Picks]:
    # read weekly pick csv into list of named tuples
    try:
        with open(f"data/{race}_picks.csv", "r") as f:
            reader = csv.DictReader(f)
            picks = []
            for row in reader:
                wk_picks = [int(s) for s in row[
                    "Select three drivers from the list below."].split() if
                            s.isdigit()]
                picks.append(Picks(row["Who is submitting picks?"], wk_picks))
        return picks
    except FileNotFoundError:
        print(f"The file {race}_picks.csv does not exist.  Check the data directory.")


# write the results from a race to a csv file
def write_results_to_csv(data, race):
    # check to see if results file exists already
    if os.path.isfile(f"data/{race}_results.csv"):
        overwrite = None
        while not overwrite:
            overwrite = input(
                f"The file {race}_results.csv already exists, do you want to overwrite? [Y/N]: ")
            if overwrite.lower() == 'y':
                with open(f"data/{race}_results.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                    print(
                        f"Results successfully written to data/{race}_results.csv")
            elif overwrite.lower() == 'n':
                print(
                    f"Please rename the results file or choose a different race and run again.")
                raise SystemExit(0)
            elif overwrite.lower() == 'q':
                print(f"Good bye.")
                raise SystemExit(0)
            else:
                print(
                    f"[{overwrite}] is not a valid response.  Please enter Y or N or [Q]uit to continue: ")
                overwrite = None
    else:
        with open(f"data/{race}_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print(f"Results successfully written to data/{race}_results.csv")


###################
###  DIRECTORY  ###
###################

def create_data_directory():
    print("Checking for data directory...")
    try:
        os.mkdir("data/")
        print("Data directory created.")
    except:
        print("Data directory already exists.")

    return None


#################
###  CONSOLE  ###
#################
def display_header():
    # print the application header to the console
    print()
    print("#" * 30)
    print("###  2021 POOL CALCULATOR  ###")
    print("#" * 30)
    print()

    return None


def get_user_input():
    # get the race number from the user
    race = input("What is the race number [XX]: ")

    # get the results URL from the user
    url = input("What is the results url from ESPN: ")

    return race, url