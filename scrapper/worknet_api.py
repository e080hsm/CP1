from decouple import config
import requests
import xmltodict
import time
from pymongo import MongoClient
import json

class worknet_scrapper:
    ADDRESS = config('WORKNET')
    AUTHKEY = config('AUTHKEY')
    def get_address(para:dict):
        '''
        받아온 파라미터에 맞춰 웹 주소를 반환한다.
        para: 파라미터 리스트
        '''
        ADDRESS = f'{worknet_scrapper.ADDRESS}?authKey={worknet_scrapper.AUTHKEY}'
        para_list = [ADDRESS] + [f'{key}={val}' for key, val in para.items() if val != None]
        return '&'.join(para_list)

    def get_json(url:str):
        '''
        워크넷 open API 주소를 requests를 이용해 가져온다.
        url: 워크넷 openAPI 웹 주소
        '''
        response = requests.get(url)

        if response.status_code != 200:
            raise ConnectionRefusedError(f'connection denied: {response.status_code}"')

        #list is xml. change it to dict(json)
        return xmltodict.parse(response.text)

    def __init__(self):
        self.api_list = []
        self.api_detail = []

    def scrap_api_list(self, startPage=1, endPage=1, display=10, occupation=None, inplace=False):
        '''
        워크넷 오픈API에서 리스트 데이터를 받아온다.
        startPage: 검색 시작 페이지.
        endPage: 검색 종료 페이지. startPage~endPage까지 가져온다.
        display:한 페이지에 표시되는 명단 개수. 기본 및 최소 10, 최대 100
        occupation: 직업 코드. 직업코드는 직종코드.xls 참조.
        inplace: 종말점 설정. True면 None 반환.
        '''
        CALL_TP ='L'
        RET_TP='XML'

        for page in range(startPage, endPage + 1):
            list_para={
                'callTp': CALL_TP,
                'returnType':RET_TP,
                'startPage':page,
                'display':display,
                'occupation':occupation
            }

            # make addres for API
            address_list  = worknet_scrapper.get_address(list_para)
            
            try:
                # get list from worknet api
                self.api_list.extend(worknet_scrapper.get_json(address_list)['wantedRoot']['wanted'])
                time.sleep(1)
            except ConnectionRefusedError:
                print('Error is occured in "scrap_api_list"')
        return None if inplace else self
    
    def scrap_api_detail(self, inplace=False):
        '''
        scrap_api_list를 이용해 워크넷에서 받아온 API리스트에서 세부 정보를 추가적으로 찾아낸다.
        inplace: 종말점 설정. True면 None 반환.
        '''
        CALL_TP = 'D'
        RET_TP='XML'
        for wanted in self.api_list:
            detail_para={
                'callTp': CALL_TP,
                'returnType':RET_TP,
                'wantedAuthNo':wanted['wantedAuthNo'],
                'infoSvc':wanted['infoSvc']
            }

            # make addres for API
            address_detail = worknet_scrapper.get_address(detail_para)
            
            try:
                # get the detailed infomation from api
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
        '''
        scrap_api_detail에서 받아온 리스트를 로컬 json 파일로 저장한다.
        file_name: 파일 이름. 반드시 .json 파일이어야 한다.
        '''
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
    