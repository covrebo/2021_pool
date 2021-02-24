import services

# √ choose the players check to be sure the data directory exists
# √ print the header in the console
# √ prompt the user for the race number
# √ prompt the user for the results URL from ESPN
# √ scrape ESPN results table and write results to CSV
# √ import the picks for the week
# √ import the weekly picks and convert to named tuple
# TODO: import the standings and convert to named tuples
# TODO: calculate the weekly points and new standings
# TODO: write the new standing to csv

def main():
    # check if the data directory exists, and create it if it doesn't
    services.create_data_directory()

    # print the application header
    services.display_header()

    # get the race number and results url from the user
    race, url = services.get_user_input()

    # import picks for the week
    picks = services.import_picks_from_csv(race)

    # print the picks for the week
    for p in picks:
        print(f"{p.picker} has the {p.picks[0]}, {p.picks[1]}, and {p.picks[2]}")

    # retrieve the race results
    raw_site = services.pull_site(url)

    # validate the data was pulled from the site
    if not raw_site:
        raise SystemExit(0)

    # process the site data to a list
    results = services.scrape(raw_site)

    # calculate weekly points
    weekly_points = services.weekly_points(race, picks, results)

    print("###  RESULTS  ###")
    for rank, picker in enumerate(weekly_points):
        print(f"#{rank + 1}: {picker.picker} with {picker.total_points}")

    # write the results to a csv file
    services.write_results_to_csv(results, race)

    # import previous standings
    prev_standings = services.import_previous_standings(race)
    print(prev_standings)

    # update standings
    standings = services.calculate_standings(race, prev_standings, weekly_points)
    print(standings)

    # TODO: write the standings to a csv
    services.write_standings_to_csv(race, prev_standings, standings)

if __name__ == '__main__':
    main()