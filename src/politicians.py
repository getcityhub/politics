from consts import *

import os
import requests
import shutil

def get_politicians(api_key, conn, s3, zipcode):
    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    query = {"address": zipcode, "key": api_key}
    response = requests.get(url, params=query)
    response_data = response.json()

    positions = {}

    for office in response_data["offices"]:
        for index in office["officialIndices"]:
            positions[index] = office["name"]

    for i, politician in enumerate(response_data["officials"]):
        data = {"name": politician["name"], "zipcodes": str(zipcode)}

        if i in positions:
            if positions[i] in POSITIONS:
                data["position"] = POSITIONS[positions[i]]
            else:
                data["position"] = positions[i]

        if "party" in politician:
            party = politician["party"]

            if party == "Democratic":
                party = "Democrat"

            if party.lower() != "unknown":
                data["party"] = party

        if "photoUrl" in politician:
            data["photo_url"] = politician["photoUrl"]

        if "emails" in politician:
            data["email"] = politician["emails"][0]

        if "phones" in politician:
            data["phone"] = politician["phones"][0]

        if "urls" in politician:
            data["website"] = politician["urls"][0]

        if "channels" in politician:
            for channel in politician["channels"]:
                data[channel["type"].lower()] = channel["id"]

        cur = conn.cursor()
        cur.execute("SELECT * FROM politicians WHERE name = %s", (politician["name"],))

        existing_data = None

        for row in cur:
            existing_data = row

        if existing_data == None:
            if "photo_url" in data:
                file_name = data["photo_url"].split("/")[-1]
                response = requests.get(data["photo_url"], stream=True)
                data["photo_url"] = "https://s3.amazonaws.com/cityhub/politicians/" + file_name

                with open(file_name, "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)

                s3.upload_file(file_name, "cityhub", "politicians/" + file_name)
                os.remove(file_name)

            keys = []
            values = []

            for key, val in data.iteritems():
                keys.append(key)
                values.append(val)

            command = "INSERT INTO politicians (" + ", ".join(x for x in keys) + ") VALUES (" + ", ".join("%s" for x in keys) + ")"
            cur.execute(command, tuple(values))

            conn.commit()
            cur.close()
        else:
            new_data = {}

            zipcodes = [x for x in existing_data[2].split(",")]

            if zipcode not in zipcodes:
                zipcodes.append(zipcode)
                new_data["zipcodes"] = ",".join([str(x) for x in zipcodes])

            def check(pos, key):
                if key in data:
                    if pos not in existing_data or data[key] != existing_data[pos]:
                        new_data[key] = data[key]

            check(3, "position")
            check(4, "party")
            check(6, "email")
            check(7, "phone")
            check(8, "website")
            check(9, "facebook")
            check(10, "googleplus")
            check(11, "twitter")
            check(12, "youtube")

            if len(new_data) > 0:
                keys_values_str = ""
                values = []

                for j, key in enumerate(new_data):
                    keys_values_str += key + " = %s" + ("" if j == len(new_data) - 1 else ", ")
                    values.append(new_data[key])

                command = "UPDATE politicians SET " + keys_values_str + " WHERE id = " + str(existing_data[0])
                cur.execute(command, tuple(values))

                conn.commit()
                cur.close()
