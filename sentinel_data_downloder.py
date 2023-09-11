from sentinelsat import SentinelAPI
import yaml
import os
from collections import OrderedDict
from core.control_code import ControlCode

'''
[지진]
    - 진원지 위도, 경도와 발생시간을 입력받아서 해당 지역의 위성영상을 검색
'''

class downloader:
    def __init__(self, params) -> None:
        (self.connectionDic, self.login_id, self.login_pw, self.download_path, self.log) = params
        self.queue = []
        
        
    def run(self) -> None:
        from core.earthquake_db import earthquake_DB
        self.db = earthquake_DB(self.connectionDic)
        
        check_list = (ControlCode.Download_Ready, ControlCode.Download_After_Ready)
        
        for check_code in check_list:
            eq_item_list = self.db.get_eq_item_from_db(check_code)
            
            if(len(eq_item_list) == 0):
                self.log.write_log(f'No need to download {check_code}')
                continue
            
            for item in eq_item_list:
                self.do_download((item, check_code))
                pass
        
        self.download_start()
    
    def do_download(self, params):
        (eq_id, area, end_date, is_descending), check_code = params
        self.log.write_log(f'Download start {eq_id} ({check_code})')
        from datetime import datetime, timedelta
        api = SentinelAPI(self.login_id, self.login_pw)
        
        if check_code == ControlCode.Download_Ready:
            start_date = end_date + timedelta(days=-15)
        elif check_code == ControlCode.Download_After_Ready:
            start_date = end_date
            end_date = datetime.now()
            
        is_descending = is_descending != b'\x00'
        orbit_direction = 'Descending' if is_descending else 'Ascending'
        
        
        # 이미 다운 받은 데이터가 있을 경우엔 DB에 저장된 orbit_direction을 확인하여 다운로드해야 함
        # 중복 으로 query를 날리면 안됨
        products = api.query(area, date=(start_date.strftime("%Y%m%d"), end_date), 
                             platformname='Sentinel-1', producttype=('SLC'), raw='IW', orbitdirection=orbit_direction, limit=1)
        
        if len(products) == 0 and is_descending is not True and check_code == ControlCode.Download_Ready:
            products = api.query(area, date=(start_date.strftime("%Y%m%d"), end_date), 
                             platformname='Sentinel-1', producttype=('SLC'), raw='IW', orbitdirection='Descending', limit=1)
            if len(products) > 0:
                self.db.change_descending(eq_id)
        
        online_products = OrderedDict()
        for item in products:
            if api.is_online(item):
                api.check_files(ids = list({item}), directory=self.download_path, delete=True)
                online_products.update({item: products[item]})
        try:
            if check_code == ControlCode.Download_Ready and len(online_products) == 0:
                self.db.update_contorl_code(eq_id, ControlCode.Data_Not_Found)
                self.log.write_log(f'SAR Data not found {eq_id}({area})', level='error')
                return
            
            if check_code == ControlCode.Download_After_Ready and len(online_products) == 0:
                self.log.write_log(f'SAR Data does not upload yet {eq_id}')
                return
            
            self.db.update_contorl_code(eq_id, ControlCode(check_code.value+1))
            self.queue.append((eq_id, online_products))
            # api.download_all(online_products, directory_path=os.path.join(self.download_path, eq_id))
            # self.db.update_contorl_code(eq_id, ControlCode(check_code.value+4))
        except Exception as e:
            self.db.update_contorl_code(eq_id, ControlCode.InternalEngineException)
            self.log.write_log(f'Download error {eq_id} {e}', level='error')
        
        pass
    
    def download_start(self):
        
        download_products = OrderedDict()
        api = SentinelAPI(self.login_id, self.login_pw)
        
        # queue를 돌면서 하나의 product로 합친다. (한번에 다운 받기 위함)
        for index in range(len(self.queue)):
            eq_id, products = self.queue.pop(0)
            for item in products:
                if api.is_online(item):
                    api.check_files(ids = list({item}), directory=self.download_path, delete=True)
                    download_products.update({item: products[item]})
        pass
    
        api.download_all(download_products, directory_path=self.download_path)
        
        pass
    
    def download_complete(self):
        pass



pass