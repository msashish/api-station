from . import session, base_url


class TV:

    def __init__(self, id):
        self.id = id

    def info(self):
        info_url = f"{base_url}tv/{self.id}"
        response = session.get(info_url)
        return response.json()

    @staticmethod
    def top_rated():
        top_rated_url = f"{base_url}tv/top_rated"
        response = session.get(top_rated_url)
        return response.json()
