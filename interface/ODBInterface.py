from requests import Session, packages
import configparser

class ODBInterface:

    def __init__(self, cfg_file, logger=None):
        
        packages.urllib3.disable_warnings()

        self.logger = logger
        self.cfg = configparser.ConfigParser()
        # logger.debug(f"Parsing config file {cfg_file}")
        self.cfg.read(cfg_file)

        self.api_url = self.cfg['URLS']["api_url"]
        # logger.debug(f"Set OBDInterface base URL to {self.api_url}")
        self.session = self.get_authenticated_session()
        

    def get_authenticated_session(self) -> Session:

        session = Session()
        session.verify = False

        # url_login = self.cfg["URLS"]["login_url"]
        # credentials = {
        #     "email" : self.cfg["CREDENTIALS"]["email"],
        #     "password" : self.cfg["CREDENTIALS"]["password"]
        # }

        # login_result = session.post(url=url_login, params=credentials, verify=False)
        # if login_result.status_code == 401:
        #     raise ConnectionRefusedError(f"Login unsuccesful: {login_result.json()['comment']}")
        # elif login_result.status_code != 200:
        #     raise ConnectionError(f"Unknown connection error while trying to log in")
        
        # cookies = login_result.json()
        cookies = {
            "ODB-API-KEY" : self.cfg["CREDENTIALS"]["APIKEY"],
            "ODB-API-UID" : self.cfg["CREDENTIALS"]["APIUID"]
        }
        # print(cookies)
        session.cookies.update(cookies)

        return session

    def get_OB_from_id(self, id):
        url = f"{self.api_url}/obsBlocks"
        res = self.session.get(url, params={"ob_id" : id})
        if res.status_code == 200:
            data = res.json()
            return data
        else:
            print("What should I do here?")
    
    def get_script(self, instrument, script_name, script_version):
        url = f"{self.api_url}/instrumentPackages/{instrument.upper()}/scripts"
        res = self.session.get(url)
        print(res.json())
        if res.status_code == 200:
            for script in res.json():
                if script["metadata"]["name"] == script_name and \
                    script["metadata"]["version"] == script_version:

                    return script["script"]

    def close_session(self):
        self.session.close()

    # def get_semids(self):
    #     url = f"{self.api_url}/observers/semesterIDs"
    #     res = self.session.get(url)
    #     if res.status_code == 200:
    #         data = res.json()
    #         return data
    #     else:
    #         print("What should I do here?")

    # def get_OBs_from_semIDs(self, semIDs):
    #     url = f"{self.api_url}/search/ob"
    #     for semID in semIDs:
    #         res = self.session.get(url, params = {
    #             "sem_id" : semID
    #         })
