

rend_map = [['1','2','3','4','5','6','7'],['2','3','4','5','6','7','8']]
row = 0
print_map = ["oh","oh"]
for line in print_map:
    line = line.join(rend_map[row][0:4])
    row+=1
print(print_map)