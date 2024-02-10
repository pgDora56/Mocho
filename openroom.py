import requests
import random
import urllib
import time
import json

with open("config.json", "r") as f:
    conf = json.load(f)
console_id = conf["console"]  # for debug


class NagayaOpener:
    def openroom(user, pw):
        roomnumbers = [str(i) for i in range(1, 9)]
        random.shuffle(roomnumbers)
        roomno = ""
        result = ""

        while result != "ok":
            if len(roomnumbers) == 0:
                return None
            roomno = roomnumbers.pop()
            url = "https://penpenpng.com/nqa2/api/create/room" + \
                roomno
            params = {
                "name": user,
                "password": pw
            }
            response = requests.post(
                url=url,
                data=urllib.parse.urlencode(params),
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            result = response.text
            print(response.status_code)
            print(response.text)
            time.sleep(1)
        return roomno


if __name__ == '__main__':
    NagayaOpener.openroom("Test", "test")
