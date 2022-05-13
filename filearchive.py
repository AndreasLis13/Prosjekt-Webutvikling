import mysql.connector 
from mysql.connector import errorcode

class FileArchive: 
    def __init__(self) -> None:
        
        dbconfig = { 'host': 'kark.uit.no',
                     'user': 'stud_v22_lislelidand',
                     'password': '63D4tl84',
                     'database': 'stud_v22_lislelidand', }
        
        self.configuration = dbconfig 


    def __enter__(self) -> 'cursor':
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(buffered=True)
        return self 

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def query(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall
        return result 

    
    def getAll(self):
        try:
            self.cursor.execute("SELECT * from Dokument")
            result = self.cursor.fetchall()

        except mysql.connector.Error as err:
            print(err)

    
    def get(self, id):
        try:
            self.cursor.execute("SELECT * FROM Dokument WHERE id =(%s)", (id,))
            result = self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(err)
            
        return result 
    

