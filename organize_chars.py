from keyboard import is_pressed,record
BADS = ["shift","space","down","enter"]
QUIT = "esc"
PREFIX = "[KeyboardEvent("
def decode_record(rec_list:list):
    index = 0
    while index < len(rec_list):
        item = str(rec_list[index])
        bad_found = False
        for subs in BADS:
            if item.find(subs) > -1:
                rec_list.pop(index)
                bad_found = True
                break
        if not bad_found:
            index += 1
    rec_list = str(rec_list)
    if rec_list[len(PREFIX)+1] != " ":
        return rec_list[len(PREFIX):len(PREFIX)+3] # for esc, alt, etc.
    return rec_list[len(PREFIX)]

with open("texil_chars.txt",encoding="utf=8") as file:
    file_str = file.readline()
organized = dict()
with open("texil_chars_org.txt",encoding="utf-8") as file:
    oldline = file.readline()
    oldtext = ""
    if len(oldline) > 0:
        last_char = oldline[0]
        start = file_str.find(last_char) + 1
        oldline = file.readline() # Do not include last_char
        while oldline != '':
            key = oldline[0]
            organized[key] = list()
            for i in range(1,len(oldline)-1):
                char = oldline[i]
                if char != " ":
                    organized[key].append(char)
            oldline = file.readline()
    else:
        start = 0 # new file
open_msg = "You must type the character that is closest to the given special"
open_msg += " character, or press space to go to the next. Press "
open_msg += QUIT + "+space to save and quit."
print(open_msg)
for i in range(start,len(file_str)):
    char = file_str[i]
    if char != " ":
        print("Where does",char,"go? ")
        key_pressed = (decode_record(record(' ')))
        if key_pressed == QUIT:
            cancelled = char
            char = last_char
            break
        if key_pressed not in organized.keys():
            organized[key_pressed] = list()
        if char != key_pressed:
            organized[key_pressed].append(char)
        last_char = char
print(cancelled,"was cancelled. Saving progress point to",last_char)
with open("texil_chars_org.txt",mode="w",encoding="utf-8") as save_file:
    line = char + "\n"
    for char in organized.keys():
        line += char
        for match_char in organized[char]:
            line += " " + match_char
        line += "\n"
    save_file.write(line)