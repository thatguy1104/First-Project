import datetime
import logging
import pyodbc

import azure.functions as func

def writeToDB():
    server = 'serverteest.database.windows.net'
    database = 'testdatabase'
    username = 'login12391239'
    password = 'HejsanHejsan!1'
    driver= '{ODBC Driver 17 for SQL Server}'

    myConnection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password)
    cur = myConnection.cursor()

    create = """DROP TABLE IF EXISTS staticfunction_data;"""
    cur.execute(create)
    script = """
        CREATE TABLE staticfunction_data(
            appid               INT,
            name_               text,
            release_date        text
        );
        """
    cur.execute(script)
    print("Successully created DB: Table -> staticfunction_data DB -> {0}".format(database))

    dummy_data = ((248820,	"Risk of Rain", "2025-11-08)"),                                                                                                                                                                                                                                                                                 
                 (248860,	"NEO Scavenger", "2025-12-15"),                                                                                                                                                                                                                                                                                               
                 (249050,	"Dungeon of the Endless™", "2015-20-27"),                                                                                                                                                                                                                                                                                       
                 (249130,	"LEGO® Marvel™ Super Heroes", "2015-21-15"),                                                                                                                                                                                                                                                                                               
                 (249190,	"Ancient Space", "2015-29-23"),                                                                                                                                                                                                                                                                               
                 (249230,	"Risen 3 - Titan Lords", "2015-28-13"))
    
    for data in dummy_data:
        insertion = """INSERT INTO staticfunction_data(appid, name_, release_date) VALUES(?, ?, ?)"""
        cur.execute(insertion, data)
    
    print("Successfully written to table -> {0}, DB -> {1}".format("staticfunction_data", database))

    myConnection.commit()
    myConnection.close()

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    writeToDB()

