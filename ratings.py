"""
PDGA ratings estimator

Asks for tournament ratings inputs for values not included in current
PDGA rating. Then calculates the estimated new ratings

TODO:
    Include function to remove ratings that fall below the standard deviation
"""

from gc import get_referents
from requests_html import HTMLSession

import pandas as pd
import numpy as np
from typing import List


def get_ratings_detail(pdga_num: int):
    details_url = f'https://www.pdga.com/player/{pdga_num}/details'
    s = HTMLSession()
    r = s.get(details_url)
    return r


def get_current_rating(results: str):
    rating_raw = results.html.find('.current-rating', first=True).text
    current_loc_start = rating_raw.find(':')
    current_rating = rating_raw[current_loc_start +1:].strip().split(' ')[0]
    return int(current_rating)


def trans_data(results: str):
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
    df_dates = df_include.copy()
    df_dates['Date'] = df_dates['Date'].str.split('to').str[-1].str.strip()
    df_dates['Date'] = pd.to_datetime(df_dates['Date'], format='%d-%b-%Y')

    # Filter results to ratings that are counted towards current rating
    df_results = df_dates.copy()
    df_results = df_results.loc[df_results['Included'] == True]

    return df_results


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
def manual_ratings():
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
