from bs4 import BeautifulSoup
import requests
import lxml
import json
import pyodbc
import datetime
import time
import sys
import configparser as cfg

server = 'serverteest.database.windows.net'
database = 'testdatabase'
username = 'login12391239'
password = 'HejsanHejsan!1'
driver = '{ODBC Driver 17 for SQL Server}'

class steamConcurrent():
    def __init__(self):
        self.linkGeneral = 'https://store.steampowered.com/stats/'
        self.linkAll = 'https://steamcharts.com/top/p.'
        self.response = requests.get(self.linkGeneral)
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    # FUNCTION IS NOT USED
    def getConcurrent(self):
        all_current = self.soup.find_all('span', class_='statsTopHi')
        current = all_current[0].text.replace(',', '')
        peak_today = all_current[1].text.replace(',', '')

        return int(current), int(peak_today)

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def checkTableExists(self, dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def getTopGamesByPlayerCount(self, page):
        link = self.linkAll + str(page)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')

        all_game_names = []
        current_players = []
        peak_players = []
        hours_played = []

        names = soup.find_all('td', class_='game-name left')
        current_p = soup.find_all('td', class_='num')

        for tittle in names:
            game_name = tittle.find('a')

            # Process the weirdly formatted string output for NAMES
            raw = game_name.text.replace('\t', '')
            final = raw.replace('\n', '')
            all_game_names.append(final)

        for player in current_p:
            peaks = soup.find_all('td', class_='num period-col peak-concurrent')
            hours = soup.find_all('td', class_='num period-col player-hours')
            if (player not in peaks) and (player not in hours):
                current_players.append(player.text)

        for i in range(len(names)):
            peak_players.append(peaks[i].text)
        for i in range(len(names)):
            hours_played.append(hours[i].text)

        return all_game_names, current_players, peak_players, hours_played

    def updateDB(self, pages):
        # total_current, total_peak = self.getConcurrent()  <-- NOT USED ANYWHERE, BUT KEEP FOR NOW

        # SCRAPE THE DATA FIRST
        data = []
        curr_date = datetime.datetime.now()

        for p in range(1, pages):
            self.progress(p, pages, "scraping for <steam_concurrentGames>")
            name, current, peak, hours_played = self.getTopGamesByPlayerCount(p)
            for i in range(len(name)):
                data.append((name[i], current[i], peak[i], hours_played[i], curr_date))
        sys.stdout.write('\n')

        # CONNECT TO DATABASE
        myConnection = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cur = myConnection.cursor()

        if not self.checkTableExists(myConnection, 'steam_concurrentGames'):
            # EXECUTE SQL COMMANDS
            cur.execute("DROP TABLE IF EXISTS steam_concurrentGames;")
            create = """CREATE TABLE steam_concurrentGames(
                Name_               NVARCHAR(255),
                Current_Players     BIGINT,
                Peak_Today          BIGINT,
                Hours_Played        BIGINT,
                Last_Updated        DATETIME
            );"""
            cur.execute(create)
            print("Successully created DB Table: steam_concurrentGames")
            myConnection.commit()

        # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
        if not data:
            print("Not written --> too many requests")
        else:
            # RECORD INITIAL TIME OF WRITING
            t0 = time.time()

            # EXECUTE INSERTION INTO DB TABLE
            cur.fast_executemany = True
            insertion = "INSERT INTO steam_concurrentGames(Name_, Current_Players, Peak_Today, Hours_Played, Last_Updated) VALUES (?, ?, ?, ?, ?)"
            cur.executemany(insertion, data)

            # RECORD END TIME OF WRITING
            t1 = time.time()

            print("Successully written to table <steam_concurrentGames> (db: {0})".format(self.database))

        myConnection.commit()
        myConnection.close()

        return t1 - t0

def run():
    obj = steamConcurrent()
    MAX_pages = 478
    obj.updateDB(MAX_pages)
