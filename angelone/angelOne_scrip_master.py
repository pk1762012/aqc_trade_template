import json
import requests
import sqlite3

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
csv_filename = "angelOne_scrip.csv"
db_filename = "../scrip_master.db"
filename = csv_filename

def download_csv_from_url():
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Write the content of the response to a local file
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded successfully as '{filename}'")
    else:
        print("Failed to download CSV file")


def read_csv(file_path):
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        if line:
            objects = json.loads(line)
        else:
            objects = []
    return objects

def create_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS angelOne_scrip_data(
                    Token TEXT,
                    Symbol TEXT,
                    Name TEXT,
                    Expiry TEXT,
                    StrikePrice TEXT,
                    LotSize TEXT,
                    InstrumentType TEXT,
                    Segment TEXT,
                    TickSize TEXT
                    )''')

def insert_data(cursor, data):
    cursor.executemany('INSERT INTO angelOne_scrip_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

def clear_table(cursor):
    cursor.execute('''DELETE FROM angelOne_scrip_data''')

def store_csv_to_sqlite():
    objectList = read_csv(filename)

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    try:
        clear_table(cursor)
    except:
        pass
    # Create table if not exists
    create_table(cursor)

    data = []
    for obj in objectList:
        data.append((obj['token'], obj['symbol'], obj['name'], obj['expiry'], obj['strike'], obj['lotsize'], obj['instrumenttype'], obj['exch_seg'], obj['tick_size']))

    insert_data(cursor, data)

    conn.commit()
    conn.close()

def get_token_id_from_symbol(symbol, exchange):
    """
    Get the token id from the sytmbol and exchange
    :param symbol:
    :param exchange:
        NSE
        BSE
        NFO
        CDS
        MCX
        NCDEX
        BFO
    :return token_id:
    """

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Token FROM angelOne_scrip_data WHERE Symbol = ? AND Segment = ?", (symbol,exchange))
    except:
        download_csv_from_url()
        store_csv_to_sqlite()
        cursor.execute("SELECT Token FROM angelOne_scrip_data WHERE Symbol = ? AND Segment = ?", (symbol,exchange))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        download_csv_from_url()
        store_csv_to_sqlite()
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        cursor.execute("SELECT Token FROM angelOne_scrip_data WHERE Name = ? AND Segment = ?", (symbol,exchange))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        else:
            return None

#print(get_token_id_from_symbol('IRFC-EQ', 'NSE'))