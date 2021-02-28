import collections
import csv
import os
from typing import List, Dict

import bs4
import requests

Picks = collections.namedtuple('Picks', 'picker, picks')
WeeklyPoints = collections.namedtuple('WeeklyPoints',
                                      'picker, d1, d1_pts, d2, d2_pts, d3, d3_pts, bonus, total_points,')
WeeklyStandings = collections.namedtuple('WeeklyStandings',
                                         'picker, race_points, total_points,')


#################
###  SCORING  ###
#################

# calculate the weekly points for each driver
def weekly_points(race: int, picks: List[Picks], results: List) -> List[
    WeeklyPoints]:
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
        wkly_points.append(WeeklyPoints(picker=pick.picker, d1=pick.picks[0],
                                        d1_pts=
                                        results_dict[f'{pick.picks[0]}'][
                                            'PTS'], d2=pick.picks[1], d2_pts=
                                        results_dict[f'{pick.picks[1]}'][
                                            'PTS'], d3=pick.picks[2], d3_pts=
                                        results_dict[f'{pick.picks[2]}'][
                                            'PTS'], bonus=bonus, total_points=(
                    int(results_dict[f'{pick.picks[0]}']['PTS']) + int(
                results_dict[f'{pick.picks[1]}']['PTS']) + int(
                results_dict[f'{pick.picks[2]}']['PTS']) + int(bonus))))
    print()

    wkly_points = sorted(wkly_points, key=lambda x: x.total_points,
                         reverse=True)

    return wkly_points


def calculate_standings(prev_standings: List[List],
                        wkly_points: List[WeeklyPoints]) -> Dict:
    # TODO: handle ties
    prev_standings_dict = {}
    wkly_standings = {}
    if prev_standings:
        for row in prev_standings[1:]:
            prev_standings_dict[f"{row[0]}"]: row[-1]
        for row in prev_standings[1:]:
            tp = [pick.total_points for pick in wkly_points if
                  pick.picker == row[0]]
            wp = [pick.total_points for pick in wkly_points if
                  pick.picker == row[0]]
            wkly_standings[f"{row[0]}"] = [
                ('picker', f"{row[0]}"),
                ('weekly_points', int(wp[0])),
                ('total_points', int(row[-1]) + int(tp[0]))
            ]
        return wkly_standings
    else:
        for pick in wkly_points:
            wkly_standings[pick.picker] = [
                ('picker', pick.picker),
                ('weekly_points', pick.total_points),
                ('total_points', pick.total_points)
            ]
        return wkly_standings

# update the win summary
def update_win_summary(race: int, picks: List[Picks], new_standings: List, weekly_points: List[WeeklyPoints]) -> List:
    # TODO: handle ties
    win_summary = []
    # TODO: move to csv section and make more generic
    # check for an existing win summary csv
    if os.path.isfile(f"data/{int(race)-1}_wins.csv"):
        # read previous wins into memory
        with open(f'data/{int(race) - 1}_wins.csv', "r") as f:
            reader = csv.reader(f)
            for row in reader:
                win_summary.append(row)
        # update win summary list
        for winner in win_summary[1:]:
            if winner[0] == weekly_points[0][0]:
                win_count = int(winner[1])
                win_count += 1
                winner[1] = win_count
        # write new win summary to csv
        with open(f"data/{race}_wins.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(win_summary)

    else:
        with open(f"data/{race}_wins.csv", "w") as f:
            # create header row for win summary list
            header = ["picker", "wins"]
            win_summary.append(header)
            # create empty list of winners
            for p in picks:
                row = [p.picker, 0]
                win_summary.append(row)
            # update the list with the first pool winner
            for picker in win_summary[1:]:
                if picker[0] == new_standings[0][0]:
                    picker[1] += 1
            # write results to csv
            writer = csv.writer(f)
            writer.writerows(win_summary)

    # remove the header
    win_summary.pop(0)
    win_summary = sorted(win_summary, key=lambda x: int(x[1]), reverse=True)

    return win_summary

#####################
###  WEBSCRAPING  ###
#####################

def pull_site(url):
    # TODO: check is there is a results file so you don't make request every time

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
    picks_dict = {}
    # check for previous picks
    if os.path.isfile(f"data/{int(race) - 1}_picks_final.csv"):
        try:
            # read previous picks into dictionary
            with open(f"data/{int(race) - 1}_picks_final.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    picks_dict[f"{row[0]}"] = [row[1], row[2], row[3]]
        except:
            print("ERROR SERVICES:179")
        # read the new picks into a list
        try:
            with open(f"data/{race}_picks.csv", "r") as f:
                reader = csv.DictReader(f)
                picks_list = []
                for row in reader:
                    wk_picks = [int(s) for s in row[
                        "Select three drivers from the list below."].split() if
                                s.isdigit()]
                    picks_list.append(Picks(row["Who is submitting picks?"], wk_picks))
        except:
            print("ERROR SERVICES:191")
        # create the new list of picks
        for pick in picks_list:
            if pick.picker in picks_dict.keys():
                picks_dict[f"{pick.picker}"]= [pick.picks[0], pick.picks[1], pick.picks[2]]
        # write the new list of picks to a file:
        try:
            with open(f"data/{race}_picks_final.csv", "w") as f:
                writer = csv.writer(f)
                for key, value in picks_dict.items():
                    row = [key, value[0], value[1], value[2]]
                    writer.writerow(row)
        except:
            print("ERROR SERVICES:203")
        # TODO: refactor to return a dict
        # convert to correct return value
        picks = []
        for key, value in picks_dict.items():
            picks.append(Picks(key, value))
        return picks

    # if there are no previous picks
    else:
        # read picks into a list
        try:
            with open(f"data/{race}_picks.csv", "r") as f:
                reader = csv.DictReader(f)
                picks_list = []
                for row in reader:
                    wk_picks = [int(s) for s in row[
                        "Select three drivers from the list below."].split() if
                                s.isdigit()]
                    picks_list.append(
                        Picks(row["Who is submitting picks?"], wk_picks))
        except:
            print("ERROR SERVICES:225")
        # create the new list of picks
        for pick in picks_list:
            picks_dict[f"{pick.picker}"]= [pick.picks[0], pick.picks[1],
                                               pick.picks[2]]
        # write the new list of picks to a file:
        try:
            with open(f"data/{race}_picks_final.csv", "w") as f:
                writer = csv.writer(f)
                for key, value in picks_dict.items():
                    row = [key, value[0], value[1], value[2]]
                    writer.writerow(row)
        except:
            print("ERROR SERVICES:238")
        # TODO: refactor to return a dict
        # convert to correct return value
        picks = []
        for key, value in picks_dict.items():
            picks.append(Picks(key, value))
        return picks


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


def import_previous_standings(race: str) -> List[List]:
    standings = []
    try:
        with open(f"data/{int(race) - 1}_standings.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                standings.append(row)
        return standings
    except:
        return None


def write_standings_to_csv(race: str, prev_standings: List[List],
                           standings: Dict) -> List:
    new_standings = []
    if prev_standings:
        headers = prev_standings[0]
        # DEBUG print(f"headers before: {prev_standings[0]}")
        headers.append(f'R{race} Points')
        headers.append(f'R{race} Total Points')
        new_standings.append(headers)
        # DEBUG print(f"headers after: {headers}")
        try:
            with open(f"data/{race}_standings.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in prev_standings[1:]:
                    # DEBUG print(f"row before: {row}")
                    row.append(standings[f"{row[0]}"][1][1])
                    row.append(standings[f"{row[0]}"][2][1])
                    new_standings.append(row)
                    # DEBUG print(f"row after: {row}")
                    writer.writerow(row)
        except:
            print(f"There was an error trying to save the weekly standings.")
    else:
        try:
            with open(f"data/{race}_standings.csv", "w") as f:
                writer = csv.writer(f)
                headers = ["picker", "R1 Points", "R1 Total Points"]
                new_standings.append(headers)
                writer.writerow(headers)
                for key, value in standings.items():
                    # DEBUG print(f"row before: {key}, {value}")
                    row = [f"{key}", f"{value[1][1]}", f"{value[2][1]}"]
                    new_standings.append(row)
                    # DEBUG print(f"{row}")
                    writer.writerow(row)
        except:
            print(f"There was an error trying to save the weekly standings.")

    return new_standings


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
    print("###         v2021.0        ###")
    print("#" * 30)
    print()

    return None


def get_user_input():
    # TODO: implement input validation
    # get the race number from the user
    race = input("What is the race number [XX]: ")

    # get the results URL from the user
    url = input("What is the results url from ESPN: ")

    # prompt the user for picks only or full results
    picks_only = input("Do you want to get [P]icks or [R]esults: ")

    return race, url, picks_only


def display_standings(new_standings: List):
    # remove the row with the headers
    new_standings.pop(0)
    # sort the standings
    sorted_standings = sorted(new_standings, key=lambda x: x[-1], reverse=True)
    print()
    print("###################")
    print("###  STANDINGS  ###")
    print("###################")
    print()
    for rank, list in enumerate(sorted_standings):
        print(f"#{rank + 1}: {list[0]} with {list[-1]} points.")
    return None
