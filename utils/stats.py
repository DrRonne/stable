import json

LEVEL_EXP = json.load(open("./resources/level_experience.json", "r"))

def calcLevel(exp):
    for i in range(0, len(LEVEL_EXP)):
        if exp < LEVEL_EXP[i]:
            return i