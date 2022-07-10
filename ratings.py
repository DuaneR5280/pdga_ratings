from requests_html import HTMLSession
from pandas import DataFrame
import pandas as pd
import numpy as np
from typing import List


def get_ratings_detail(pdga_num: int):
    """Get ratings details from PDGA player details page

    Args:
        pdga_num (int): Player PDGA number

    Returns:
        response: HTML page python requests response
    """
    details_url = f'https://www.pdga.com/player/{pdga_num}/details'
    session = HTMLSession()
    response = session.get(details_url)
    return response


def get_current_rating(results: str) -> int:
    """Get player's current rating

    Args:
        results (response): Requests response

    Returns:
        int: Player's current rating
    """
    rating_raw = results.html.find('.current-rating', first=True).text
    current_loc_start = rating_raw.find(':')
    current_rating = rating_raw[current_loc_start +1:].strip().split(' ')[0]
    return int(current_rating)


def convert_dates(df, date_col='Date', format='%d-%b-%Y') -> DataFrame:
    # Format dates to datetime date, remove multi date spans
    df_dates = df.copy()
    df_dates[date_col] = df_dates[date_col].str.split(' to ').str[-1].str.strip()
    df_dates[date_col] = pd.to_datetime(df_dates[date_col], format=format)
    return df_dates


def trans_data(results: str) -> DataFrame:
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


# Get current year tournaments played page
def get_tour_results_page(pdga_num: int):
    details_url = f'https://www.pdga.com/player/{pdga_num}'
    s = HTMLSession()
    r = s.get(details_url)
    return r


def trans_tour_data(results: str) -> DataFrame:
    # WIP
    table = results.html.find('.table-container', first=True)
    table_df = pd.read_html(table.html)
    df = table_df[0]
    df_dates = convert_dates(df.copy(), 'Dates')
    
    return df_dates

def get_ratings_dates() -> DataFrame:
    """Get dates when ratings will be updated

    ### WIP ###

    Returns:
        _type_: _description_
    """
    ratings_updates_url = "https://www.pdga.com/faq/ratings/when-updated"
    s = HTMLSession()
    r = s.get(ratings_updates_url)
    table = r.html.find('table', first=True)
    # HTML table to DataFrame
    table_df = pd.read_html(table.html)
    df = table_df[0]
    # Convert dates
    dates = convert_dates(df, 'Ratings Publication Date', '%B %d, %Y')
    return dates['Ratings Publication Date']


# Standard deviation plus 2.5 pdga threashold
def std_calc(ratings: List):
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


if __name__ == "__main__":
    ratings_detail = get_ratings_detail(input('Enter PDGA Number: '))
    df_results = trans_data(ratings_detail)
    current_rating = get_current_rating(ratings_detail)
    print(f'Current Rating: {current_rating}\n')
    new_ratings = manual_ratings()
    new_rating = combine_ratings(list(df_results["Rating"]), new_ratings, current_rating)
    print(f'\nNew Estimated Rating: {new_rating}')
