import mysql.connector

def get_machine_uuids():
    conn = mysql.connector.connect(
        host="localhost",
        user="mmc",
        password="pBWfpjErqtsU",
        database="kiosk",  # adapte si besoin
        port=3306
    )
    cursor = conn.cursor()
    cursor.execute("SELECT uuid, hostname FROM up_list_produit")  # adapte si ta table a un autre nom
    result = [{"uuid": row[0], "hostname": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return result
