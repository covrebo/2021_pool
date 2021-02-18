import services

# TODO: check to be sure the data directory exists
# TODO: print the header in the console
# TODO: prompt the user for the race number
# TODO: prompt the user for the results URL from ESPN
# TODO: scrape ESPN results table and write results to CSV
# TODO: import the picks for the week
# TODO: import the weekly picks and convert to named tuple
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

    # retrieve the race results
    raw_site = services.pull_site(url)

    # validate the data was pulled from the site
    if not raw_site:
        raise SystemExit(0)

    # process the site data to a list
    results = services.scrape(raw_site)

    # write the results to a csv file
    services.write_results_to_csv(results, race)

if __name__ == '__main__':
    main()