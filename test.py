from textengine import brighten_color,color_by_num
sphere=[
    " HHHH+ ",
    "H##HH++",
    "H#HH+++",
    " +++++ "]
for i in range (1,256):
    color = color_by_num(i)
    brighter = brighten_color(color,True)
    darker = brighten_color(color,False)

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
            else:
                line.append(color_by_num(16)+ " ")
        ssphere = ssphere +("".join(line)) + color_by_num(16) + "\n"
    print(ssphere)