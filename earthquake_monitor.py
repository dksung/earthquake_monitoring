'''
1. USGS에서 지진 데이터를 가져온다.
2. 가져온 데이터를 DB에 저장한다. (id, title, point, power, time, url)
3. DB에 저장된 데이터를 기반으로 위성영상을 검색한다.
4. 검색된 위성영상을 다운로드 한다.
'''

class eq_monitor:
    def __init__(self) -> None:
        self.load_setting()
    
    def load_setting(self) -> None:
        import yaml, os
        from core.logger import LogHandler
        
        with open('db_info.yaml') as file:
            self.connectionDic = yaml.load(file, Loader=yaml.FullLoader)
            
        with open('setting.yaml') as file:
            self.login_info = yaml.load(file, Loader=yaml.FullLoader)
            
        work_dir = os.path.join(os.path.expanduser('~'), os.path.join(*self.login_info['working_dir']))
        self.login_id = self.login_info['copernicus_id']
        self.login_pw = self.login_info['copernicus_pw']
        self.min_magnitude = self.login_info['min_magnitude']
        
        self.download_path = os.path.join(work_dir, 'data')
        self.log_path = os.path.join(work_dir, 'logs')
        
        if not os.path.isdir(self.download_path):
            os.makedirs(self.download_path)
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        
        self.log = LogHandler(self.log_path)
        
        self.log.write_log('Start monitoring')
    
    def run(self) -> None:
        from sentinel_data_downloder import downloader
        
        self.check_exist_new_eq_item()
        down_loader = downloader((self.connectionDic, self.login_id, self.login_pw, self.download_path, self.log))
        down_loader.run()
        
        from core.repeated_timer import RepeatedTimer
        RepeatedTimer(60, self.check_exist_new_eq_item)        
        RepeatedTimer(30, down_loader.run)        
    
    def check_exist_new_eq_item(self) -> None:
        from datetime import datetime
        from core.earthquake_db import earthquake_DB
        
        eq_data_list = self.get_eq_data()
        
        if(len(eq_data_list) == 0):
            self.log.write_log(f'No new earthquake data')
            return
            
        db = earthquake_DB(self.connectionDic)
        
        for id, properties, geometry in eq_data_list:
            if db.is_exist_eq_item(id) is not None:
                self.log.write_log(f'{id} is already exist')
                continue
            
            mag = properties['mag']
            title = properties['title']
            readableTime = datetime.fromtimestamp(float(properties['time'])/1000.).strftime('%Y-%m-%d %H:%M:%S')
            point = f"POINT ({geometry['coordinates'][0]} {geometry['coordinates'][1]})"
            url = properties['url']
            
            db.insert_eq_data((id, title, point, mag, readableTime, url))
            
        pass
    
    def get_eq_data(self):
        
        # USGS에서 지진 데이터를 가져온다.
        # get data from USGS URL using httprequest :
        # https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2021-08-01&endtime=2021-08-02
        from urllib.request import urlopen
        import json
        from datetime import datetime, timedelta
        
        start_date = datetime.now() + timedelta(days=-7)
        response = urlopen(f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date.strftime("%Y-%m-%d")}&minmagnitude={self.min_magnitude}').read()
        data = json.loads(response)        
        
        return [(item['id'], item['properties'], item['geometry']) for item in data['features']]


if __name__ == '__main__':
    
    monitor = eq_monitor()
    monitor.run()
    pass