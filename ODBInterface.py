import requests
import configparser

class OBDInterface:

    def __init__(self, cfg_file):

        self.cfg = configparser.ConfigParser()
        self.cfg.read(cfg_file)
        self.session = self.get_authenticated_session()

    def get_authenticated_session(self) -> requests.Session:

        session = requests.Session()

        url_login = self.cfg["URLS"]["login_url"]
        credentials = {
            "email" : self.cfg["CREDENTIALS"]["email"],
            "password" : self.cfg["CREDENTIALS"]["password"]
        }

        login_result = session.post(url=url_login, params=credentials, verify=False)
        if login_result.status_code != 200:
            print("Scream!")
            return
        
        cookies = login_result.json()
        session.cookies.update(cookies)

        return session

    def get_semids(self):
        url = f"{self.url}/observers/semesterIDs"
        res = self.session.get(url)
        if res.status_code == 200:
            data = res.json()
            return data
        else:
            print("What should I do here?")


    def get_OBs_from_semIDs(self, semIDs):
        url = f"{self.url}/search/ob"
        for semID in semIDs:
            res = self.session.get(url, params = {
                "sem_id" : semID
            })
