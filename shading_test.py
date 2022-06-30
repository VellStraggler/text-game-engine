from textengine import brighten,color_by_num,RETURN
from time import sleep
sphere=[brighten
    " HHHHH+ ",
    "H##HHH++",
    "H#HH+++.",
    " +++... "]
def rainbow_sphere():
    for i in range (1,256):
        color = color_by_num(i)
        brighter = brighten(color,True)
        darker = brighten(color,False)
        darkest = brighten(darker,False)

        ssphere = str(i)+": \n"
        for row in sphere:
            line = []
            for i in row:
                if i == "H":
                    line.append(color + " ")
                elif i == "#":
                    line.append(brighter + " ")
                elif i == "+":
                    line.append(darker + " ")
                elif i == ".":
                    line.append(darkest + " ")
                else:
                    line.append(color_by_num(16)+ " ")
            ssphere = ssphere +("".join(line)) + color_by_num(16) + "\n"
        ssphere = RETURN + ssphere
        print(ssphere)
        sleep(.1)
while(True):
    rainbow_sphere()