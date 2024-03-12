import logging
import requests

class MagiqInterface():

    def __init__(self, cfg):
        server = cfg['MAGIQSERVER']['server']
        port = cfg['MAGIQSERVER']['port']
        self.urlbase = f'http://{server}:{port}'

    @staticmethod
    def create_magiq_ui_name(name, idx):
        postfix = f'-{idx}'
        rem = 16 - len(name) - len(postfix)
        if rem < 0: 
            uname = name[0:rem] + postfix + ' '
        else:
            uname = (name + postfix).ljust(17)
        return uname

    def convert_target_to_targetlist_row(self, target, acquisition, idx):
        tparams = target.get('parameters')
        aparams = acquisition.get('parameters', False)

        name = tparams.get('target_info_name') 
        uname = self.create_magiq_ui_name(name, idx)
        ra = tparams['target_coord_ra'].replace(':', ' ') + " "
        dec = tparams['target_coord_dec'].replace(':', ' ') + " "
        epoch = str(tparams['target_coord_epoch']) + " "
        rowStr = uname + ra + dec + epoch
        mags = tparams.get('target_magnitude', False)
        if mags: # only add the first magnitude
            magnitude = str(mags[0]['target_info_mag']) + " "
            band = mags[0].get('target_info_band', "").lower()
            rowStr += f'{band}mag=' + magnitude

        if aparams:
            raOffset = aparams.get('tcs_coord_raoff', False)
            decOffset = aparams.get('tcs_coord_decoff', False)
            wrap = aparams.get('rot_cfg_wrap', False)
            wrap = 'shortest' if wrap=='auto' else wrap 
            rotMode = aparams.get('rot_cfg_mode', False)
            rotMode = 'vertical' if rotMode=='vertical_angle' else rotMode 
            rotPA = aparams.get('rot_cfg_pa', False)

            rowStr += 'raOffset=' + str(raOffset) + ' ' if isinstance(raOffset, bool) and raOffset else ""
            rowStr += 'decOffset=' + str(decOffset) + ' ' if isinstance(decOffset, bool) and decOffset else ""
            rowStr += 'rotmode=' + str(rotMode).lower() + ' ' if isinstance(rotMode, bool) and rotMode else ""
            rowStr += 'wrap=' + str(wrap) + ' ' if isinstance(wrap, bool) and wrap else ""
            rowStr += 'target=' + uname + ' ' if uname else ""
            rowStr += 'rotdest=' + str(rotPA) + ' ' if isinstance(rotPA, bool) and rotPA else ""
        rowStr = rowStr.rstrip(' ')
        return rowStr

    def convert_obs_to_targetlist(self, obs, logger):

        targetListStr = ""
        for idx, ob in enumerate(obs):
            target = ob.get('target', False)
            acquisition = ob.get('acquisition', False)
            if not target or not acquisition:
                logger.debug('ob has either no target or acquisition. not going to add')
                continue
            try:
                row = self.convert_target_to_targetlist_row(target, acquisition, idx) 
                targetListStr += row + '\n'
            except Exception as err:
                name = target.get('parameters').get('target_info_name') 
                logger.warning(f'Error converting target {name} to targetlist row: {err}. Not going to add')
                continue
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
        parameters = target.get('parameters')
        name = parameters.get('target_info_name', '')
        uname = self.create_magiq_ui_name(name, idx)
        uname = uname.rstrip(' ')
        url = f'{url}target={uname}'
        logger.info(f'Selecting target {url}')
        response = requests.get(url)
        return response