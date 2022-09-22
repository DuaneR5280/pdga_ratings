# PDGA player rating update estimator
from requests_html import HTMLSession
from pandas import DataFrame
import pandas as pd
import numpy as np
from typing import List
from datetime import date, timedelta


# def get_ratings_detail(pdga_num: int):
#     """Get ratings details from PDGA player details page

#     Args:
#         pdga_num (int): Player PDGA number

#     Returns:
#         response: HTML page python requests response
#     """
#     details_url = f'https://www.pdga.com/player/{pdga_num}/details'
#     session = HTMLSession()
#     response = session.get(details_url)
#     return response


# def get_player_stats(pdga_num: int):
#     """Get current year tournaments played page

#     Args:
#         pdga_num (int): PDGA number

#     Returns:
#         response: requests response
#     """
#     details_url = f'https://www.pdga.com/player/{pdga_num}'
#     s = HTMLSession()
#     r = s.get(details_url)
#     return r


# def get_single_tournament(t_url: str):
#     s = HTMLSession()
#     r = s.get(t_url)
#     return r


# def get_current_rating(results) -> int:
#     """Get player's current rating from get_player_stats()

#     Args:
#         results (response): Requests response

#     Returns:
#         int: Player's current rating
#     """
#     rating_raw = results.html.find('.current-rating', first=True).text
#     current_loc_start = rating_raw.find(':')
#     current_rating = rating_raw[current_loc_start +1:].strip().split(' ')[0]
#     return int(current_rating)


# def convert_dates(df, date_col='Date', format='%d-%b-%Y') -> DataFrame:
#     """Convert Dates in DataFrame Date column (str) to Datetime.Date
    
#     Format dates to datetime date, remove multi date spans

#     Example:
#         '3-Sep to 4-Sep-2022' to 2022-09-04

#     Args:
#         df (DataFrame): Dates(str) in table from PDGA web pages
#         date_col (str, optional): Date Column of DataFrame. Defaults to 'Date'.
#         format (str, optional): Existing date string format = Day-Month-Year. Defaults to '%d-%b-%Y'.

#     Returns:
#         DataFrame: Tournament data with proper formated Datetime.Date in Date column    
#     """
#     df_dates = df.copy()
#     df_dates[date_col] = df_dates[date_col].str.split(' to ').str[-1].str.strip()
#     df_dates[date_col] = pd.to_datetime(df_dates[date_col], format=format)
#     return df_dates


def trans_data(results) -> DataFrame:
    """Transform Data from Ratings Detail page

    Only includes data that has been evalutated and is included in the
    current player ratings. Ratings drop off after 1 year.

    Args:
        results (str): Requests response

    Returns:
        DataFrame: Tournament table
    """
    table = results.html.find('table', first=True)

    # HTML table to DataFrame
    table_df = pd.read_html(table.html)
    df = table_df[0]

    # Convert Yes/No to Bool
    df_eval = df.copy()
    df_eval['Evaluated'] = df_eval['Evaluated'].map({'Yes': True, 'No': False})

    df_include = df_eval.copy()
    df_include['Included'] = df_include['Included'].map({'Yes': True, 'No': False})

    # Format dates to datetime date, remove multi date spans
    df_dates = convert_dates(df_include.copy())

    # Filter results to ratings that are counted towards current rating
    df_results = df_dates.copy()
    df_results = df_results.loc[df_results['Included'] == True]

    return df_results


def trans_stats(results) -> DataFrame:
    """Transform player stats pdga page to DataFrame

    WIP - not needed RN, better to get a list of tournament names
        to compare to the ratings detail tournament column list of links.
        Then follow the link to get the rating data for that tournament
        to add to the df_results.

    Args:
        results (str): Requests response

    Returns:
        DataFrame: Tournament table
    """

    table = results.html.find('.table-container')
    table_df = [pd.read_html(t.html)[0] for t in table]
    df = pd.concat(table_df, axis=0, ignore_index=True)
    df_dates = convert_dates(df.copy(), 'Dates')
    return df_dates


def tournaments_list(df_dates: DataFrame) -> List:
    # generate a list of tournament names not included in df_results
    # doesn't work well because we need the hyperlink to the tournament
    # to get the results
    # Here for reference
    tournaments_not_included = list(df_dates[~df_dates.Tournament.isin(df_results['Tournament'])]['Tournament'])
    return tournaments_not_included


def convert_links(links: List) -> List:
    """Convert Links List(set) to List(str)

    Convert a list of single sets to a list of strings from a request
    response of absolute links.

    Removes the # from the end of the link for comparison of another
    list of links that does not contain that information but is otherwise
    the same.

    Removes duplicates from the list as well.

    Args:
        links (List(set)): Requests response absolute_links results 

    Returns:
        List(str): Links with # removed
    """
    convert_set = [', '.join(l.absolute_links) for l in links]  # convert single set to list
    dedup = list(set(convert_set))  # de-duplicate
    clean_links = []
    for link in dedup:
        if "#" in link:
            hash_loc = link.find('#')
            clean_links.append(link[:hash_loc])
        else:
            clean_links.append(link)
    return clean_links


def tournament_links(results) -> List:
    """Get a list of tournament names and links from a requests response

    Works with Player Stats & Ratings Detail PDGA page.

    Args:
        results (str): Requests response from PDGA web page

    Returns:
        List: Flattened links response object
    """
    data = results.html.find('td.tournament')
    links = [i.find('a') for i in data]
    flat_links = [item for sublist in links for item in sublist]
    return convert_links(flat_links)


def compare_tournaments(list1, list2) -> List:
    """Compare list of tournaments from player stats page (list1) with ratings detail page (list2)

    Args:
        list1 (str): Tournament list from Player Stats page (https://www.pdga.com/player/51790)
        list2 (str): Tournament list from Player Details page (https://www.pdga.com/player/51790/details)

    Returns:
        List (str): Tournaments not included in current ratings as listed on the Player Details page
    """
    return [t for t in list1 if t not in list2]


def get_single_tour_ratings(response, pdga_num: int) -> List:
    """Get single tournament ratings for player

    Finds all tables on page and then filters table that
    contains players PDGA number.

    Converts that to a DataFrame, creates column filter for round
    ratings for players PDGA number.
    
    Converts any floats to an int and returns them in a list.

    Args:
        response (Requests Response): scraped page data
        pdga_num (int): Player PDGA number

    Returns:
        List: Tournament round ratings
    """
    tables = response.html.find('.table-container')
    table = [t for t in tables if str(pdga_num) in t.text][0]
    df = pd.read_html(table.html)[0]
    filter_col = [col for col in df if col.startswith('Unnamed')]
    round_ratings = list(df[df["PDGA#"] == pdga_num][filter_col].values[0])
    round_ratings = [int(r) for r in round_ratings]
    return round_ratings


#### Calculations ####
def std_calc(ratings: List):
    # Standard deviation plus 2.5 pdga threashold
    return np.std(ratings) * 2.5


def dbl_weight_calc(ratings: List):
    return int(np.floor(len(ratings) * 0.25))


def double_scores(ratings: List):
    dbl_w = int(dbl_weight_calc(ratings))
    return sum(ratings[:dbl_w])


def total_score(ratings: List):
    # Need to account for new ratings below standard deviation
    # Check double_scores are calc correctly
    double_total = double_scores(ratings)
    ratings_total = sum(ratings) + double_total
    num_tournaments = len(ratings) + dbl_weight_calc(ratings)
    total = ratings_total / num_tournaments
    return int(np.ceil(total))


# Manually input new ratings to calculate
# Modify to pull from tournaments not submitted to pdga
def manual_ratings() -> List:
    new_ratings = []

    while True:
        rating_input = input('Add tournament rating [enter to finish]: ')
        if rating_input:
            new_ratings.append(int(rating_input))
        else:
            break
    return new_ratings


def combine_ratings(existing_results: List, new_ratings: List, current_rating: int):
    combined_ratings = new_ratings + existing_results
    std_deviation = std_calc(combined_ratings)
    exclude_value = current_rating - std_deviation

    # remove ratings that fall below devation value
    final_ratings = []
    for rating in combined_ratings:
        if rating <= exclude_value or (current_rating - rating) >= 100:
            print(f'Rating removed {rating}')
            pass
        else:
            final_ratings.append(rating)
    return (total_score(final_ratings))


def ratings_pub_date(current_month = date(date.today().year, date.today().month, 1)):
    """PDGA Ratings Publication Date - https://www.pdga.com/faq/ratings/when-updated

    Args:
        current_month (date, optional): date (year, month, day). Defaults to date(date.today().year, date.today().month, 1).

    Returns:
        date: second Tuesday of given month
    """
    offset = 7 - ((current_month.weekday() - 1) % 7)
    if offset != 7:
        offset += 7
    second_tues = current_month + timedelta(days=offset)
    return second_tues



if __name__ == "__main__":
    ratings_detail = get_ratings_detail(input('Enter PDGA Number: '))
    df_results = trans_data(ratings_detail)
    current_rating = get_current_rating(ratings_detail)
    print(f'Current Rating: {current_rating}\n')
    new_ratings = manual_ratings()
    new_rating = combine_ratings(list(df_results["Rating"]), new_ratings, current_rating)
    print(f'\nNew Estimated Rating: {new_rating}')
