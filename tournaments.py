# TODO:
#   - API endpoint example:  https://www.pdga.com/apps/tournament/live-api/live_results_fetch_round.php?TournID=69137&Division=MA40&Round=1
#   - API tournament endpoint: https://www.pdga.com/apps/tournament/live-api/live_results_fetch_event.php?TournID=69137

from requests_html import HTMLSession


class TourScraper:
    BASEURL = "https://www.pdga.com/apps/tournament/live-api/"

    def __init__(self, t_url) -> None:
        self.session = HTMLSession()
        self.t_url = t_url
        # self.tournID = tournID
        # self.division = division

    def get_single_tournament(self):
        self.resp = self.session.get(self.t_url)
        return self.resp
