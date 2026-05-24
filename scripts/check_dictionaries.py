from clickhouse_driver import Client

def check_dictionaries():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    print("Dictionaries in sunculture_db:")
    try:
        dicts = client.execute("SHOW DICTIONARIES FROM sunculture_db")
        print(dicts)
    except Exception as e:
        print("Error showing dictionaries:", e)
        
    print("\nAll Dictionaries in ClickHouse:")
    try:
        dicts = client.execute("SHOW DICTIONARIES")
        print(dicts)
    except Exception as e:
        print("Error showing all dictionaries:", e)

    print("\nDatabase list:")
    try:
        dbs = client.execute("SHOW DATABASES")
        print(dbs)
    except Exception as e:
        print("Error showing databases:", e)

if __name__ == "__main__":
    check_dictionaries()
