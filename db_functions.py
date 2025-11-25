import mysql.connector

# chỉnh thông tin kết nối cho phù hợp
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="Minh@120705",
    database="qlch_vlxd",
    port=3307
)

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def load_table(table):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_record(table, fields, values):
    conn = connect_db()
    cur = conn.cursor()
    placeholders = ", ".join(["%s"] * len(values))
    field_list = ", ".join(fields)
    sql = f"INSERT INTO {table} ({field_list}) VALUES ({placeholders})"
    cur.execute(sql, tuple(values))
    conn.commit()
    cur.close()
    conn.close()

def delete_record(table, pk_field, pk_value):
    conn = connect_db()
    cur = conn.cursor()
    sql = f"DELETE FROM {table} WHERE {pk_field}=%s"
    cur.execute(sql, (pk_value,))
    conn.commit()
    cur.close()
    conn.close()

def update_record(table, pk_field, pk_value, fields, values):
    conn = connect_db()
    cur = conn.cursor()
    set_clause = ", ".join([f"{f}=%s" for f in fields])
    sql = f"UPDATE {table} SET {set_clause} WHERE {pk_field}=%s"
    cur.execute(sql, tuple(values) + (pk_value,))
    conn.commit()
    cur.close()
    conn.close()

def search_record(table, field, keyword):
    """Nếu field rỗng hoặc keyword rỗng -> trả về toàn bộ"""
    conn = connect_db()
    cur = conn.cursor()
    if not field or field.strip() == "":
        cur.execute(f"SELECT * FROM {table}")
    else:
        # nếu tìm theo exact mã, dùng = ; còn tìm theo tên thì LIKE
        if field.lower().startswith("ma"):
            cur.execute(f"SELECT * FROM {table} WHERE {field} = %s", (keyword,))
        else:
            cur.execute(f"SELECT * FROM {table} WHERE {field} LIKE %s", ('%'+keyword+'%',))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
