from runsql import runsql
import requests, time


def update_inscription_db():
    ts = int(time.time()//3600)*3600
    sql = "insert ignore into inscription(inscription,ts,fdv,price) values"
    sql += "(%s,%s,%s,%s),"
    data = ["ordi", ts, "50000000", "1000"]
    runsql(sql, data)


if __name__ == '__main__':
    update_inscription_db()