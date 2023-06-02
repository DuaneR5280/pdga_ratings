# TODO:
#   - Update functions to use UDiscRounds model
#   - Add more stats
#       - By Year
#       - Between Dates
#       - By Course
#   - Include sanctioned PDGA rounds
#     - API endpoint example:  https://www.pdga.com/apps/tournament/live-api/live_results_fetch_round.php?TournID=69137&Division=MA40&Round=1
#     - API tournament endpoint: https://www.pdga.com/apps/tournament/live-api/live_results_fetch_event.php?TournID=69137

import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import Counter
from rich import print

from models import UDiscRounds


def csv_data(filename):
    """Open CSV file

    Args:
        filename (Path): UDisc CSV file

    Returns:
        list[dict]: UDisc scores
    """
    with open(filename, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        clean_scorecards = []
        for row in csv_reader:
            fixed_row = {
                k: v.strip() for k, v in row.items() if v != ""
            }  # remove empty hole scores
            clean_scorecards.append(fixed_row)
        scorecards = []
        for item in clean_scorecards:
            hole_scores = {k: int(v) for k, v in item.items() if "Hole" in k}
            non_hole_data = {k: v for k, v in item.items() if "Hole" not in k}
            non_hole_data["hole_scores"] = hole_scores
            non_hole_data["player"] = non_hole_data.pop("PlayerName")
            non_hole_data["course"] = non_hole_data.pop("CourseName")
            non_hole_data["layout"] = non_hole_data.pop("LayoutName")
            non_hole_data["date"] = non_hole_data.pop("Date")
            non_hole_data["total"] = non_hole_data.pop("Total")
            if non_hole_data.get("+/-"):
                non_hole_data["plus_minus"] = int(non_hole_data.pop("+/-"))
            scorecards.append(non_hole_data)
    return scorecards


def udisc_rounds(scorecards: List[Dict]) -> List:
    return [UDiscRounds(**card) for card in scorecards]


def player_list(scorecards: List[Dict]) -> List:
    """Create list of unique players in scorecards

    Args:
        scorecards (List[Dict]): UDisc scorecard data from CSV file

    Returns:
        set: Sorted set of player names
    """
    players = set()
    for i in scorecards:
        players.add(i["player"])
    return sorted(players)


def select_players(players: List) -> Tuple:
    """Create Tuple of players to evaluate against each other from
    players listed in UDisc scorecards

    Args:
        players (List): Players gather from player_list()

    Returns:
        Tuple: string of player names
    """
    for i, player in enumerate(players):
        print(f"{[i]} {player}")
    print("\n")
    player1 = players[int(input("Select player 1 by number: "))].strip()
    print(f"Selected: {player1}\n")
    player2 = players[int(input("Select player 2 by number: "))].strip()
    print(f"\n Selected: {player2}\n")

    return player1, player2


def player_rounds(scorecards: List[Dict], player: str) -> List:
    player_rounds = []
    for score in scorecards:
        if score["player"].strip() in player:
            player_rounds.append(score)
    return player_rounds


def shared_rounds(player1_rounds: List, player2_rounds: List):
    # Not needed
    player1_dates = set()
    player2_dates = set()
    for round in player1_rounds:
        player1_dates.add(round["date"])
    for round in player2_rounds:
        player2_dates.add(round["date"])
    shared_rounds = set()
    for r_date in player1_dates:
        if r_date in player2_dates:
            shared_rounds.add(r_date)
    return shared_rounds


def compare_scores(player1_rounds, player2_rounds):
    scores = []
    for score in player1_rounds:
        for score2 in player2_rounds:
            if score["date"] == score2["date"]:
                data = {
                    "date": score["date"],
                    "course_name": score["course"],
                    score["player"]: score["total"],
                    score2["player"]: score2["total"],
                }
                winner_calc = int(score["total"]) - int(score2["total"])
                if winner_calc < 0:
                    winner = score["player"]
                elif winner_calc > 0:
                    winner = score2["player"]
                else:
                    winner = "tie"
                data["winner"] = winner
                scores.append(data)
    return scores


def compare_years(year):
    """Stats by given year

    Args:
        year (str): year converted to datetime
    """
    pass


def num_wins(scores):
    num_rounds = len(scores)
    winners = [w["winner"] for w in scores]
    win_count = dict(Counter(winners))
    win_count["total"] = num_rounds
    return win_count


def main():
    filename = input("file name (default: scorecards.csv): ")
    if not filename:
        filename = "scorecards.csv"
    udisc_scores = csv_data(filename)
    unique_players = player_list(udisc_scores)
    player1, player2 = select_players(unique_players)
    player1_rounds = player_rounds(udisc_scores, player1)
    player2_rounds = player_rounds(udisc_scores, player2)
    scores = compare_scores(player1_rounds, player2_rounds)
    win_count = num_wins(scores)
    print(win_count)


if __name__ == "__main__":
    main()
    udisc_scores = udisc_rounds(csv_data("scorecards.csv"))
