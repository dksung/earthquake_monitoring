from core.control_code import *
import pymysql as mysql

class earthquake_DB():
    def __init__(self, connectionDic) -> None:
        self.Open(connectionDic)
    
    def Open(self, connectionDic):
        self.connection = mysql.connect(**connectionDic)
        self.cur = self.connection.cursor(mysql.cursors.DictCursor)
        
    def Close(self):
        self.connection.close()
        
    def is_exist_eq_item(self, eq_id) -> bool:
        query = "SELECT eq_id FROM cx_earthquake WHERE eq_id=%s"
        self.cur.execute(query, eq_id)
        res = self.cur.fetchone()
        item = dict(res) if res is not None else None    
        return item
    
    def insert_eq_data(self, params):
        query = "INSERT INTO cx_earthquake \
            (eq_id, title, eq_point, eq_power, event_time, description) \
                VALUES(%s, %s, %s, %s, %s, %s)"
        self.cur.execute(query, params)
        self.connection.commit()
    
    def get_eq_item_from_db(self, controlCode:ControlCode):
        query = "SELECT eq_id, eq_point, event_time, is_descending FROM cx_earthquake WHERE control_code=%s"
        self.cur.execute(query, controlCode.value)
        res = self.cur.fetchall()
        if res is not None:
            return [(one_item['eq_id'], one_item['eq_point'], one_item['event_time'], one_item['is_descending']) for one_item in res]

    def update_contorl_code(self, eq_id:str, controlCode:ControlCode):
        query = "UPDATE cx_earthquake SET control_code=%s WHERE eq_id=%s"
        try:
            self.cur.execute(query, (controlCode.value, eq_id))
            self.connection.commit()
        except Exception as e:
            print(e)
            
    def change_descending(self, eq_id:str):
        query = "UPDATE cx_earthquake SET is_descending=1 WHERE eq_id=%s"
        try:
            self.cur.execute(query, eq_id)
            self.connection.commit()
        except Exception as e:
            print(e)