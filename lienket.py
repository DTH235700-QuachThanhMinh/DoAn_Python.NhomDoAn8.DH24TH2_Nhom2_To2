import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Minh@120705",
            database="qlch_vlxd",
            port=3307
        )
        return conn
    except Error as e:
        print("Lỗi kết nối:", e)
        return None

# Test kết nối khi chạy trực tiếp file
if __name__ == "__main__":
    conn = connect_db()
    if conn:
        print("Kết nối thành công!")
        conn.close()