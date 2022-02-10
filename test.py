import time

def create_array(char):
    array = list()
    for y in range(25):
        line = list()
        for x in range(50):
            line.append(char)
        array.append(line)
    return array

def print_array(array):
    for y in range(25):
        for x in range(50):
            if array[y][x] == 0:
                print(" ",end="")
        print()
    print()

def spaces():
    array = create_array(" ")
    print_array(array)

def zeroes():
    array = create_array(0)
    print_array(array)

def main():
    print("\n" * 1000)
    s_speeds = list()
    z_speeds = list()
    for tests in range(1000):
        z_start = time.time()
        zeroes()
        z_end = time.time()
        s_start = time.time()
        spaces()
        s_end = time.time()
        s = s_end - s_start
        z = z_end - z_start
        s_speeds.append(s)
        z_speeds.append(z)
    print("\033[2J")
    s_avg = sum(s_speeds)/len(s_speeds)
    z_avg = sum(z_speeds)/len(z_speeds)
    if s_avg < z_avg:
        print(f"Printing spaces directly was faster by {((z_avg-s_avg)*100/z_avg):.2f}%")
    else:
        print(f"Printing spaces from zeroes was faster by {((s_avg - z_avg)*100/s_avg):.2f}%")
    print("Spaces average:",s_avg)
    print("Zeroes average:",z_avg)

main()