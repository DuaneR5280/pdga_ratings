# Player details
from requests_html import HTMLSession
from typing import List
from datetime import datetime


class Player:
    def __init__(self, pdga_num):
        # rating, career_events, career_wins, upcoming_events
        self.pdga_num = pdga_num
        self.pdga_page = f"https://www.pdga.com/player/{pdga_num}"
        self.get_pages()
        self.get_rating()
        self.get_career_events()
        self.get_career_wins()
        self.get_upcoming_events()
        self.get_tournaments_played()

    def get_pages(self):
        with HTMLSession() as session:
            self.r_stats = session.get(self.pdga_page)
            self.r_detail = session.get(self.pdga_page + "/details")
            self.r_history = session.get(self.pdga_page + "/history")
            self.r_wins = session.get(self.pdga_page + "/wins")

    def convert_dates(self, dates):
        if "to" in dates:
            d = [_.strip() for _ in dates.split("to")]
            end_date = datetime.strptime(d[1], "%d-%b-%Y").date()
            start_date = datetime.strptime(
                d[0] + f"-{end_date.year}", "%d-%b-%Y"
            ).date()
        elif "," in dates:
            start_date = datetime.strptime(dates, "%a, %b %d, %Y").date()
            end_date = start_date
        else:
            start_date = datetime.strptime(dates, "%d-%b-%Y").date()
            end_date = start_date
        num_days = end_date - start_date
        return {"start": start_date, "end": end_date, "num_days": num_days.days + 1}

    # Stats info
    def get_stats_by_class(self, css_class) -> int:
        css_data = self.r_stats.html.find(f".{css_class}", first=True).text
        loc_start = css_data.find(":")
        data = css_data[loc_start + 1 :].strip().split(" ")[0]
        return int(data)

    def get_rating(self) -> int:
        self.rating = self.get_stats_by_class("current-rating")
        return int(self.rating)

    def get_career_events(self) -> int:
        self.career_events = self.get_stats_by_class("career-events")
        return int(self.career_events)

    def get_career_wins(self) -> int:
        self.career_wins = self.get_stats_by_class("career-wins")
        return int(self.career_wins)

    def get_upcoming_events(self) -> List:
        upcoming_list = self.r_stats.html.find(".upcoming-events li")
        self.upcoming = []
        for event in upcoming_list:
            loc = event.text.find(":")
            e = {
                "dates": self.convert_dates(event.text[:loc].strip()),
                "tournament": event.text[loc + 1 :].strip(),
                "link": list(event.absolute_links)[0],
            }
            self.upcoming.append(e)
        return self.upcoming

    # Tournaments / Ratings Details
    def get_tournaments_played(self) -> List:
        tournament_table = self.r_detail.html.find(".table-container", first=True)
        t_rows = tournament_table.find("tr")
        self.tournaments = []
        for i, row in enumerate(t_rows):
            if i != 0:
                row_data = {
                    "dates": self.convert_dates(row.find(".date", first=True).text),
                    "tournament": row.find(".tournament", first=True).text,
                    "link": list(row.absolute_links)[0],
                    "tier": row.find(".tier", first=True).text,
                    "division": row.find(".division", first=True).text,
                    "round": int(row.find(".round", first=True).text),
                    "score": int(row.find(".score", first=True).text),
                    "rating": int(row.find(".round-rating", first=True).text),
                    "evaluated": row.find("td.evaluated", first=True).text,
                    "included": row.find("td.included", first=True).text,
                }
                self.tournaments.append(row_data)
        return self.tournaments
