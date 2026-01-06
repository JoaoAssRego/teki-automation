import sys

BASE = "Monitora"

def building(name):
    if "bl" in name:
        aux = name.split("bl")
        letter = aux[1][0].upper()
        return ord(letter) - ord('A') + 1
    return 0


def create(name):
    c = 0
    for letter in name:
        if letter == '-':
            c += 1
    password = BASE + str(building(name)) + str(c)
    return password

if __name__ == "__main__":
    print(create(sys.argv[1]))