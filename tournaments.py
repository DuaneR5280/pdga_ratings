
class Tournament:
    def __init__(self) -> None:
        

def get_single_tournament(t_url: str):
    s = HTMLSession()
    r = s.get(t_url)
    return r