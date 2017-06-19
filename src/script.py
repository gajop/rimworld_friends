import os
import math
import csv
import sys

from dateutil import parser
from bs4 import BeautifulSoup

# set to True to obtain friend 'importance' from message count (not used in mod)
GET_IMPORTANCE = False

# set to True to obtain gender based on name; requires a key to be set (register at https://gender-api.com/en/)
GET_GENDER = False
GENDER_API_KEY = "" # Provided version might work SVlpDsZvjtJXjjzxCH

if GET_GENDER:
    import requests
    import json

def _getFriendsElements():
    FILE = "../html/friends.htm"

    if not os.path.exists(FILE):
        print("Missing file: " + FILE + ". Make sure you have exported your facebook data and placed in the correct directory.")
        sys.exit(-1)

    html_doc = open(FILE).read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    contents = soup.find("div", class_="contents")
    friendsEl = contents.contents[1].contents[1].find_all("li")
    return friendsEl

def _parseFriendsBasic():
    friendsEl = _getFriendsElements()

    friendsStr = []
    for f in friendsEl:
        friendsStr.append(f.string)

    friends = []

    for f in friendsStr:
        name, date = f.split("(", maxsplit=1)
        name = name.split("[")[0].strip()
        date = date[:-1]
        dt = parser.parse(date)
        friends.append({"name" : name, "added" : dt})

    return friends

def _parseFriendNames(friends):
    for f in friends:
        first = f["name"].split()[0].strip()
        last = f["name"].split()[-1].strip()
        f["first_name"] = first
        f["last_name"] = last
        f["nick"] = first
        if first != last and f["name"].split()[1] != last:
            nick = " ".join(f["name"].split()[1:-1])
            f["nick"] = nick

def get_friends():
    friends = _parseFriendsBasic()
    _parseFriendNames(friends)
    return friends

def _query_genders(first_list):
    myKey = GENDER_API_KEY
    names = ""
    data = []

    names = '; '.join(first_list)
    request = "https://gender-api.com/get?key=" + myKey + "&name=" + names

    r = requests.get(request)
    data = json.loads(r.content.decode("utf-8"))

    if "result" not in data:
        return data["gender"]
    else:
        return data["result"]


def download_genders(friends):
    first_names = []
    for f in friends:
        first_names.append(f["first_name"])

    genders = []
    NAMES_PER_REQUEST = 50
    TOTAL_REQUESTS = math.ceil(len(first_names) / NAMES_PER_REQUEST)
    for i in range(TOTAL_REQUESTS):
        print("Request: {}/{}".format(i+1, TOTAL_REQUESTS))
        startIndex = i * NAMES_PER_REQUEST
        endIndex = (i + 1) * NAMES_PER_REQUEST
        names = first_names[startIndex:endIndex]
        genders += _query_genders(names)
    print("Done")

    for f in friends:
        found = False
        for g in genders:
            if f["first_name"] == g["name"].capitalize():
                f["gender"] = g["gender"]
                found = True
                break
        if not found:
            print(f)
                #print(f["name"], g["name"])

    gendersFound = 0
    printOnce = True

    for f in friends:
        if f["gender"] == "unknown":
            if printOnce:
                print("Couldn't determine the gender of the following people:")
                print()
                printOnce = False
            print(f["name"].capitalize())
            f["gender"] = "None"
        else:
            f["gender"] = f["gender"].capitalize()
            gendersFound += 1

    print()
    print("Total genders found {}/{}: {:.2%}".format(gendersFound, len(friends), gendersFound/len(friends)))

# Not used atm
def get_importance(friends):
    FILE = "../html/messages.htm"
    html_doc = open(FILE).read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    friend_name_map = {}

    for i, f in enumerate(friends):
        friend_name_map[f["name"]] = 0

    msgHeaderEls = soup.find_all("div", class_="message_header")

    for msgHeaderEl in msgHeaderEls:
        userEl = msgHeaderEl.find(class_="user")
        metaEl = msgHeaderEl.find(class_="meta")
        name = userEl.string
        if name in friend_name_map:
            friend_name_map[name] += 1

    items = [item for item in friend_name_map.items()]
    important_people = sorted(items, key = lambda x: -x[1])
    total_weight = sum(p[1] for p in important_people)
    smooth_factor = total_weight / 100 + 1
    total_weight = total_weight + smooth_factor

    weighted_people_map = {p[0] : (p[1] + smooth_factor) / total_weight for p in important_people}

    for f in friends:
        f["importance"] = weighted_people_map[f["name"]]

def output_friends(friends):
    with open('NameDatabase.csv', 'w') as csvfile:
        fieldnames = ['first_name', 'nick', 'last_name', 'gender', 'importance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for f in friends:
            writer.writerow({
                'first_name': f['first_name'],
                'nick': f['nick'],
                'last_name': f['last_name'],
                'gender': f['gender'] if 'gender' in f else 'None',
                'importance' : f['importance'] if 'importance' in f else 1
            })
    print("Written output to file NameDatabase.csv")
    print("Remember to copy it in your Rimworld folder under Mods/FriendNameBank/NameDatabase.csv")

def run():
    friends = get_friends()
    if GET_GENDER:
        if GENDER_API_KEY == "":
            print("Missing GENDER_API_KEY. Either set the provided one or get one by registering at https://gender-api.com/en/")
            sys.exit(-1)
        print("Downloading gender from Gender-API")
        download_genders(friends)
    if GET_IMPORTANCE:
        get_importance(friends)
    output_friends(friends)

if __name__ == "__main__":
    run()
