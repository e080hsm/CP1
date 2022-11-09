from decouple import config
import requests
import xmltodict
import time
import json

class worknet_scrapper:
    ADDRESS = config('WORKNET')
    AUTHKEY = config('AUTHKEY')
    def get_json(url:str):
        response = requests.get(url)

        if response.status_code != 200:
            raise ConnectionRefusedError(f'connection denied: {response.status_code}"')

        #list is xml. change it to dict(json)
        return xmltodict.parse(response.text)

    def __init__(self):
        self.api_list = []
        self.api_detail = []

    def scrap_api_list(self, startPage=1, display=10, occupation='', inplace=False):
        CALL_TP ='L'
        RET_TP='XML'
        ADDRESS = f'{worknet_scrapper.ADDRESS}?authKey={worknet_scrapper.AUTHKEY}'

        list_para={
            'callTp': CALL_TP,
            'returnType':RET_TP,
            'startPage':startPage,
            'display':display,
            'occupation':occupation
        }

        # get list from worknet api
        address_list = [ADDRESS] + [f'{key}={val}' for key, val in list_para.items()]
        address_list = '&'.join(address_list)
        
        try:
            self.api_list = worknet_scrapper.get_json(address_list)['wantedRoot']['wanted']
        except ConnectionRefusedError:
            print('Error is occured in "scrap_api_list"')
        return None if inplace else self
    
    def scrap_api_detail(self, inplace=False):
        CALL_TP = 'D'
        RET_TP='XML'
        ADDRESS = f'{worknet_scrapper.ADDRESS}?authKey={worknet_scrapper.AUTHKEY}'
        for wanted in self.api_list:
            detail_para={
                'callTp': CALL_TP,
                'returnType':RET_TP,
                'wantedAuthNo':wanted['wantedAuthNo'],
                'infoSvc':wanted['infoSvc']
            }

            # get the detailed infomation from api
            address_detail = [ADDRESS] + [f'{key}={val}' for key, val in detail_para.items()]
            address_detail = '&'.join(address_detail)
            
            try:
                self.api_detail.append(worknet_scrapper.get_json(address_detail))
                time.sleep(1)
            except ConnectionRefusedError:
                print('Error is occured in "scrap_api_detail"')

        return None if inplace else self

    def move_to_nosql(self):
        pass

if __name__ == '__main__':
    work_api = worknet_scrapper()
    work_api.scrap_api_list(occupation= 134102).scrap_api_detail(inplace=True)
    print(work_api.api_detail)