from pymongo import MongoClient


def execute_query(f_d, f_e, cursor):
    import time
    print(f_d)
    print(f_e)
    f_d_utc = time.mktime(f_d.timetuple())
    f_e_utc = time.mktime(f_e.timetuple())
    found = cursor.find({"creation_date": {"$lt": f_e_utc, "$gte": f_d_utc}})

    return found


def find_query_dates(diff, use_date):
    from datetime import timedelta, datetime

    query_date = diff + use_date
    end_query_date = query_date + timedelta(days=1)
    # add block to get all old dates

    return query_date, end_query_date


def date_conversion():
    from datetime import datetime, date
    date_1 = datetime.now().date()
    # date_1 = date(2020, 1, 15)
    fixed_date = date(2020, 1, 14)  # fix to whatever we end up starting with
    date_2 = date(2018, 11, 23)

    diff = date_2 - date_1

    return diff, fixed_date


def main(cursor):
    diff, date_1 = date_conversion()
    final_date, final_end = find_query_dates(diff, date_1)
    data = execute_query(final_date, final_end, cursor)

    d_list = list(data)
    for d in d_list:
        print(d["title"], d["tags"])


if __name__ == "__main__":
    import json
    with open("credentials.json", "r") as f1:
        creds = json.load(f1)["keys"]
        f1.close()
    MONGODB_HOST = creds["host"]
    MONGODB_PORT = creds["port"]
    DB_NAME = creds["db_name"]
    COLLECTION_NAME = creds["collection_name"]
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)

    cursor = connection[DB_NAME][COLLECTION_NAME]

    main(cursor=cursor)
