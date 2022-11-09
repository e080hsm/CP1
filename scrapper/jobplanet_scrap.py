from decouple import config
from bs4 import BeautifulSoup as bs
import requests

class jobplanet_scrapper:
    ADDRESS = config('JOBPLANET')

    def __init__(self):
        self.api_list = []
        self.api_detail = []

    def scrap_api_list(self, stext:str, Page_No=1, inplace=False):
        TAB_TP ='recruit'
        ADDRESS = jobplanet_scrapper.ADDRESS + '/Search/?'

        list_para={
            'stext': stext,
            'tabType':TAB_TP,
            'Page_No':Page_No
        }

        # get list from worknet api
        address_list = [f'{key}={val}' for key, val in list_para.items()]
        address_list = ADDRESS +'&'.join(address_list)
        response = requests.get(address_list)
        
        if response.status_code != 200:
            raise ConnectionRefusedError(f'connection denied: {response.status_code}"')
        
        soup = bs(response.text, 'html.parser')
        self.api_list = soup.find_all("p", class_='option')

        return None if inplace else self

    def scrap_api_detail(self, inplace=False):
        # CALL_TP = 'D'
        # RET_TP='XML'
        # ADDRESS = f'{worknet_scrapper.ADDRESS}?authKey={worknet_scrapper.AUTHKEY}'
        # for wanted in self.api_list:
        #     detail_para={
        #         'callTp': CALL_TP,
        #         'returnType':RET_TP,
        #         'wantedAuthNo':wanted['wantedAuthNo'],
        #         'infoSvc':wanted['infoSvc']
        #     }

        #     # get the detailed infomation from api
        #     address_detail = [ADDRESS] + [f'{key}={val}' for key, val in detail_para.items()]
        #     address_detail = '&'.join(address_detail)
            
        #     try:
        #         self.api_detail.append(worknet_scrapper.get_json(address_detail))
        #         time.sleep(1)
        #     except ConnectionRefusedError:
        #         print('Error is occured in "scrap_api_detail"')

        return None if inplace else self

    def move_to_nosql(self):
        pass

if __name__ == '__main__':
    work_api = jobplanet_scrapper()
    work_api.scrap_api_list(stext='데이터')#.scrap_api_detail(inplace=True)
    print(work_api.api_list[0])