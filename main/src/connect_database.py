import mysql.connector

class Cdatabase_connect:

    def __init__(self):
        #각자 컴퓨터에서 할때는 각자 user로 바꿔주기
        self.local = mysql.connector.connect(
            host = "localhost",
            port = 3306,
            user = "root",
            password = "0000",
            database = "mlproject" 
        )

    def get_operator(self):
        result_list = []
        cursor = self.local.cursor()

        # 쿼리 실행
        sql = "SELECT * FROM operator;"

        cursor.execute(sql)
        result = cursor.fetchall()

        for val in result:
            result_list.append(list(val))

        return result_list

    def get_workdata(self):
        result_list = []
        cursor = self.local.cursor()

        # 쿼리 실행
        sql = "SELECT * FROM workdata;"
        
        cursor.execute(sql)
        result = cursor.fetchall()

        for val in result:
            result_list.append(list(val))
            
        return result_list

    def insert_workdata(self,work_id, operator_id, workdone_time, status):

        cursor = self.local.cursor()
        # 삽입할 데이터
        data = (work_id,operator_id,workdone_time,status)

        # 쿼리 실행
        sql = "INSERT INTO workdata (work_id, operator_id, workdone_time, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql,data)
        self.local.commit()

    def dbclose(self):
        self.local.close()
