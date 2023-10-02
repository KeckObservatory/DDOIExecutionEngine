import logging
import requests

class MagiqInterface():

    def __init__(self, cfg):
        server = cfg['MAGIQSERVER']['server']
        port = cfg['MAGIQSERVER']['port']
        self.urlbase = f'http://{server}:{port}'

    @staticmethod
    def convert_target_to_targetlist_row(target, acquisition, idx):
        tparams = target.get('parameters')
        aparams = acquisition.get('parameters', False)
        postfix = f'-{idx}'
        name = tparams.get('target_info_name') 
        rem = 16 - len(name) - len(postfix)
        if rem < 0: 
            uname = name[0:rem] + postfix + ' '
        else:
            uname = (name + postfix).ljust(17)
        ra = tparams['target_coord_ra'].replace(':', ' ') + " "
        dec = tparams['target_coord_dec'].replace(':', ' ') + " "
        mags = tparams.get('target_info_mag', False)
        magnitude = str(mags[0]['target_info_mag']) + " " if mags else False
        epoch = str(tparams['target_coord_epoch']) + " "
        rowStr = uname + ra + dec + epoch
        if magnitude:
            rotStr += 'vmag=' + magnitude

        if aparams:
            raOffset = aparams.get('tcs_coord_raoff', False)
            decOffset = aparams.get('tcs_coord_decoff', False)
            wrap = aparams.get('rot_cfg_wrap', False)
            rotMode = aparams.get('rot_cfg_mode', False)

            rowStr += 'raOffset=' + str(raOffset) + ' ' if isinstance(raOffset, bool) and raOffset else ""
            rowStr += 'decOffset=' + str(decOffset) + ' ' if isinstance(decOffset, bool) and raOffset else ""
            rowStr += 'rotmode=' + str(rotMode) + ' ' if isinstance(rotMode, bool) and raOffset else ""
            rowStr += 'wrap=' + str(wrap) + ' ' if isinstance(wrap, bool) and raOffset else ""
        return rowStr

    def convert_obs_to_targetlist(self, obs, logger):

        targetListStr = ""
        for idx, ob in enumerate(obs):
            target = ob.get('target', False)
            acquisition = ob.get('acquisition', False)
            if not target or not acquisition:
                logger.debug('ob has either no target or acquisition. not going to add')
                continue
            row = self.convert_target_to_targetlist_row(target, acquisition, idx) 
            targetListStr += row + '\n'
        return targetListStr

    def add_target_list_to_magiq(self, obs, logger):
        url = self.urlbase + '/setTargetlist'
        targetList = self.convert_obs_to_targetlist(obs, logger)
        data = {'targetlist': targetList}
        logger.info(f'Setting target list of {len(obs)} targets via: {url}')
        logger.info(f'setting target list {targetList}')
        response = requests.post(url, data=data)
        logger.info(f'response: status code: {response.status_code}')
        return response

    def check_if_connected_to_magiq_server(self):
        url = self.urlbase + '/status'
        response = requests.get(url)
        if not response.status_code == 200:
            raise Exception("check magiq server")
        return response

    def select_target_in_magiq(self, target, idx, logger):
        url = f'{self.urlbase}/selectTarget?'
        name = target.get('target_info_name', '') + f'-{idx}'
        url = f'{url}targetName={name}'
        logger.info(f'Selecting target {url}')
        response = requests.get(url)
        return response