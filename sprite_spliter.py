import time
def reverseString(string):
    letter_holder = []
    reversedStr = ""
    for char in string:
        letter_holder.append(char)

    for i in range(len(letter_holder)):
        reversedStr += letter_holder.pop()

    return reversedStr

spritesList = [""]
with open("spriteSheet.txt") as spriteFile:
    print(spriteFile)
    count = 0
    for line in spriteFile:
        # sprites = line.split("$")
        line = line.strip("")
        if "$" in line:
            count += 1
            spritesList.append("")
        else:
            spritesList[count] += line

# for sprite in spritesList:
    # print(sprite)

headSprite = spritesList[0:3]
headSprite.append(spritesList[1])
for i in range(100):
    print(headSprite[i%4])

    time.sleep(.1)
