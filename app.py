import sys
import services

def main():
    # check if the data directory exists, and create it if it doesn't
    services.create_data_directory()

    # print the application header
    services.display_header()

    # get the race number and results url from the user
    race, url, picks_only = services.get_user_input()

    if picks_only.lower() == "p":
        # import picks for the week
        picks = services.import_picks_from_csv(race)

        # TODO: move to services
        # print the picks for the week
        print()
        print("######################")
        print("###  WEEKLY PICKS  ###")
        print("######################")
        print()
        for p in picks:
            print(
                f"{p.picker} has the {p.picks[0]}, {p.picks[1]}, and {p.picks[2]}")
        print()

        sys.exit()

    # import picks for the week
    picks = services.import_picks_from_csv(race)

    # TODO: move to services
    # print the picks for the week
    print()
    print("######################")
    print("###  WEEKLY PICKS  ###")
    print("######################")
    print()
    for p in picks:
        print(f"{p.picker} has the {p.picks[0]}, {p.picks[1]}, and {p.picks[2]}")
    print()

    # retrieve the race results
    raw_site = services.pull_site(url)

    # validate the data was pulled from the site
    if not raw_site:
        raise SystemExit(0)

    # process the site data to a list
    results = services.scrape(raw_site)

    # calculate weekly points
    weekly_points = services.weekly_points(race, picks, results)

    # TODO: move to services
    print()
    print("########################")
    print("###  WEEKLY RESULTS  ###")
    print("########################")
    print()
    for rank, picker in enumerate(weekly_points):
        print(f"#{rank + 1}: {picker.picker} with {picker.total_points}")
    print()

    # write the results to a csv file
    services.write_results_to_csv(results, race)

    # import previous standings
    prev_standings = services.import_previous_standings(race)
    # DEBUG print(prev_standings)

    # update standings
    standings = services.calculate_standings(prev_standings, weekly_points)
    # DEBUG print(standings)

    # write the standings to a csv
    new_standings = services.write_standings_to_csv(race, prev_standings, standings)

    # print the standings to the console
    services.display_standings(new_standings)

    # weekly wins
    win_summary = services.update_win_summary(race, picks, new_standings, weekly_points)

    # TODO: move to services
    # print wins summary
    print()
    print("######################")
    print("###  WINS SUMMARY  ###")
    print("######################")
    print()
    for rank, picker in enumerate(win_summary):
        print(f"#{rank + 1}: {picker[0]} with {picker[1]} wins.")
    print()

    # TODO: Convert to db
    # TODO: Migrate console prints to services
    # TODO: Write tests

if __name__ == '__main__':
    main()

#################
###  ROADMAP  ###
#################
#
# 2021.0
# Initial release
# √ choose the players check to be sure the data directory exists
# √ print the header in the console
# √ prompt the user for the race number
# √ prompt the user for the results URL from ESPN
# √ scrape ESPN results table and write results to CSV
# √ import the picks for the week
# √ import the weekly picks and convert to named tuple
# √ import the standings and convert to named tuples
# √ calculate the weekly points and new standings
# √ write the new standings to csv
#
# 2021.1
# √ Weekly win tracking
# √ Split picks selections from results
# Refactor for better data structures
# Email support for weekly email
#
# 2021.2
# Refactor from csv to database support
#
# 2021.3
# Web app implementation
