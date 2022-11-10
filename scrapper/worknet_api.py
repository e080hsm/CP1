from decouple import config
import requests
import xmltodict
import time
from pymongo import MongoClient
import json

class worknet_scrapper:
    ADDRESS = config('WORKNET')
    AUTHKEY = config('AUTHKEY')
    def get_address(base_url:str, para:dict):
        para_list = [base_url] + [f'{key}={val}' for key, val in para.items()]
        return '&'.join(para_list)

    def get_json(url:str):
        response = requests.get(url)

        if response.status_code != 200:
            raise ConnectionRefusedError(f'connection denied: {response.status_code}"')

        #list is xml. change it to dict(json)
        return xmltodict.parse(response.text)

    def __init__(self):
        self.api_list = []
        self.api_detail = []

    def scrap_api_list(self, startPage=1, endPage=1, display=10, occupation='', inplace=False):
        CALL_TP ='L'
        RET_TP='XML'
        ADDRESS = f'{worknet_scrapper.ADDRESS}?authKey={worknet_scrapper.AUTHKEY}'

        for page in range(startPage, endPage + 1):
            list_para={
                'callTp': CALL_TP,
                'returnType':RET_TP,
                'startPage':page,
                'display':display,
                'occupation':occupation
            }

            # get list from worknet api
            address_list  = worknet_scrapper.get_address(ADDRESS, list_para)
            
            try:
                self.api_list.extend(worknet_scrapper.get_json(address_list)['wantedRoot']['wanted'])
                time.sleep(1)
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
            address_detail = worknet_scrapper.get_address(ADDRESS, detail_para)
            
            try:
                self.api_detail.append(worknet_scrapper.get_json(address_detail))
                time.sleep(1)
            except ConnectionRefusedError:
                print('Error is occured in "scrap_api_detail"')

        return None if inplace else self

    def move_to_nosql(self, collection:MongoClient):
        DATABASE_NAME = 'cp1'
        COLLECTION_NAME = 'worknet'
        collection[DATABASE_NAME][COLLECTION_NAME].insert_many(self.api_detail)
    
    def to_json(self, file_name:str):
        with open(file_name, 'w') as f:
            json.dump(self.api_detail, f, indent=2)

if __name__ == '__main__':
    # HOST = config('HOST')
    # USER = config('USER')
    # PASSWORD = config('PASSWORD')
    # DATABASE_NAME = 'cp1'
    # COLLECTION_NAME = 'worknet'
    # MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/?retryWrites=true&w=majority"
    # collection = MongoClient(MONGO_URI)
    # collection[DATABASE_NAME][COLLECTION_NAME].drop()
    work_api = worknet_scrapper()
    work_api.scrap_api_list(occupation= 134102).scrap_api_detail().to_json('worknet.json')
    