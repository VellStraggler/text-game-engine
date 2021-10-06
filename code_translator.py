def main():
    #read code line by line
    code_file_name = "code.txt"
    lines = []
    with open(code_file_name, 'r') as code:
        currentline = code_file_name.readline()
        if len(currentline) > 0:
            if currentline[0] != '#':

#FILE READING
def can_be_read(filename):
    try: file = open(filename,'r')
    except: return False
    file.close()
    return True

def store_code(code_file_name):
    with open(code_file_name, 'r') as code:


def store_map(map_file_name):
        map_array = [][]
        with open(map_file_name,'r') as file:
            currentline = file.readline()
            y = 0
            while currentline:
                for x in range(0,len(currentline)):
                    map_array[y][x] = currentline[x]
                y += 1
                currentline = file.readline()
        return map_array()




#START HERE (MATTHEW)
def make_import(string):
    pass

def make_function(string):
    pass

def make_add(string):
    pass

def make_subtract(string):
    pass

def make_multiply(string):
    pass

def make_divide(string):
    pass

def make_for(string):
    pass

def make_if(string):
    pass
#END HERE (MATTHEW)

def make_window_resolution(string):
    pass

def make_current_map(string):
    pass

def make_sprite(string):
    pass

main()