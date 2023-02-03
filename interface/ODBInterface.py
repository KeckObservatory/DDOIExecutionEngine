from requests import Session, packages
from requests.exceptions import JSONDecodeError
import configparser

class ODBInterface:

    def __init__(self, cfg_file, logger=None):
        
        packages.urllib3.disable_warnings()

        self.logger = logger

        self.cfg = configparser.ConfigParser()
        self.logger.debug(f"Parsing config file: {cfg_file}")
        self.cfg.read(cfg_file)

        self.api_url = self.cfg['URLS']["api_url"]
        self.logger.debug(f"Set OBDInterface base URL to {self.api_url}")
        self.session = self.get_authenticated_session()
        

    def get_authenticated_session(self) -> Session:

        session = Session()
        session.verify = False

        cookies = {
            "ODB-API-KEY" : self.cfg["CREDENTIALS"]["APIKEY"],
            "ODB-API-UID" : self.cfg["CREDENTIALS"]["APIUID"]
        }

        self.loggger.debug(f"Loading cookies from cfg file")
        session.cookies.update(cookies)

        return session


    def get_OB_from_id(self, id):
        url = f"{self.api_url}/obsBlocks"
        self.logger.debug(f"Getting OB from {url}")
        res = self.session.get(url, params={"ob_id" : id})
        if res.status_code == 200:
            self.logger.info(f"Pulled OB: {id} from DB")
            data = res.json()
            return data
        else:
            self.logger.error(f"Failed to get OB from the ODB! Got status code {res.status_code}")
            try:
                self.logger.error(f"Message: {res.json()}")
            except JSONDecodeError as e:
                self.logger.error(f"No decodable JSON to log")
        
            raise RuntimeError("Failed to recieve an OB from the database!")
    
    def get_script(self, instrument, script_name, script_version):
        url = f"{self.api_url}/instrumentPackages/{instrument.upper()}/scripts"
        self.logger.debug(f"Getting script from {url}")
        res = self.session.get(url)

        if res.status_code == 200:
            for script in res.json():
                if script["metadata"]["name"] == script_name and \
                    script["metadata"]["version"] == script_version:
                    return script["script"]
                
            raise NotImplementedError(f"No script matching {script_name} version {script_version} found in the ODB")
        else:
            self.logger.error(f"Failed to get scripts from the ODB! Got status code {res.status_code}")
            try:
                self.logger.error(f"Message: {res.json()}")
            except JSONDecodeError as e:
                self.logger.error(f"No decodable JSON to log")
        
            raise RuntimeError("Failed to recieve an OB from the database!")

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
