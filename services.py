import csv
import os

import bs4
import requests


#################
###  SCORING  ###
#################


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
def write_results_to_csv(data, race):
    # check to see if results file exists already
    if os.path.isfile(f"data/{race}_results.csv"):
        overwrite = None
        while not overwrite:
            overwrite = input(f"The file {race}_results.csv already exists, do you want to overwrite? [Y/N]: ")
            if overwrite.lower() == 'y':
                with open(f"data/{race}_results.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                    print(
                        f"Results successfully written to data/{race}_results.csv")
            elif overwrite.lower() == 'n':
                print(f"Please rename the results file or choose a different race and run again.")
                raise SystemExit(0)
            elif overwrite.lower() == 'q':
                print(f"Good bye.")
                raise SystemExit(0)
            else:
                print(f"[{overwrite}] is not a valid response.  Please enter Y or N or [Q]uit to continue: ")
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
