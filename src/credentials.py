def get_credential(name):
    f = open("keys.txt", "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        data = line.replace("\n", "").split("=", 1)
        if data[0] == name:
            return data[1]

    return None
