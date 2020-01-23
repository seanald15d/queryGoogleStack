from pymongo import MongoClient
from datetime import timedelta, datetime, date
import json


def check_tables(cs, q_id_list):
    found_list = []
    for q_id in q_id_list:
        found = cs.find({"question_id": q_id})
        if len(list(found)) > 0:
            found_list.append({q_id: True})
        else:
            found_list.append({q_id: False})
    return found_list


def execute_search(data, cs):
    from googlesearch import search
    import re

    # to search
    query = data["search"]
    query_id = data["question_id"]
    print(query)
    print(query_id)

    # regex
    regex = re.compile("stackoverflow.com\/questions\/(\d+)")

    hit_list = []
    for j in search(query, tld="com", num=10, stop=20, pause=2):
        x = regex.search(j)

        if x:
            print(j)
            hit_list.append(int(x.group(1)))

    print(hit_list)

    # check for question id objects in dataset
    f_list = check_tables(cs, hit_list)
    print("already have:")
    print(f_list)
    print(len(f_list))


def execute_query(f_d, f_e, cs):
    import time

    # construct days to pass for searches
    days = [0, 365, 365*2, 365*3, 365*4, 365*5, 365*6, 365*7, 365*8, 365*9]
    plus_days = [0, 365, 365*2, 365*3, 365*4, 365*5, 365*6, 365*7, 365*8, 365*9]

    # initialize list for appending
    data_list = []

    for i in range(0, len(days)):
        temp_fd = f_d - timedelta(days=days[i])
        temp_fe = f_e - timedelta(days=plus_days[i])

        f_d_utc = time.mktime(temp_fd.timetuple())
        f_e_utc = time.mktime(temp_fe.timetuple())
        found = cs.find({"creation_date": {"$lt": f_e_utc, "$gte": f_d_utc}})

        found_list = list(found)

        temp_list = []

        for fl in found_list:
            out_dict = dict()

            out_dict["date"] = str(temp_fd)
            out_dict["question_id"] = fl["question_id"]
            out_dict["title"] = fl["title"]
            out_dict["tags"] = fl["tags"]
            fl["tags"].insert(0, "stack overflow")
            out_dict["search"] = " ".join(fl["tags"])

            temp_list.append(out_dict)
            data_list.append(out_dict)

    return data_list


def find_query_dates(diff, use_date):
    query_date = diff + use_date
    end_query_date = query_date + timedelta(days=1)
    # add block to get all old dates

    return query_date, end_query_date


def date_conversion():
    date_1 = datetime.now().date()
    # date_1 = date(2020, 1, 15)
    fixed_date = date(2020, 1, 21)  # fix to whatever we end up starting with
    date_2 = date(2018, 11, 23)

    diff = date_2 - date_1

    return diff, fixed_date


def main(cs, stack):
    diff, date_1 = date_conversion()
    final_date, final_end = find_query_dates(diff, date_1)
    d_list = execute_query(final_date, final_end, cs)

    print(len(d_list))
    print(d_list[4])
    execute_search(d_list[4], cs)  # send cursor object and update


if __name__ == "__main__":
    with open("credentials.json", "r") as f1:
        creds = json.load(f1)["keys"]
        f1.close()
    MONGODB_HOST = creds["host"]
    MONGODB_PORT = creds["port"]
    DB_NAME = creds["db_name"]
    COLLECTION_NAME = creds["collection_name"]
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)

    cursor = connection[DB_NAME][COLLECTION_NAME]

    stack_key = creds["stack"]

    main(cursor, stack_key)
