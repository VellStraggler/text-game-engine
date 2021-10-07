import tkinter as tk
import random,time
import code_translator as ct
    #Necessary for two functions: can_be_read() and store_map()

def main():
    map_file_name = input('What is the map_file_name?')
    code_file_name = input('What is the code_file_name?')
    My_Map = MapEditor(code_file_name,map_file_name)
    #My_Window = tk.Window()
    
class MapEditor():
    #Takes only the addresses of the code and map files
    def __init__(self, code_file_name, map_file_name):
        self.map_file_name = map_file_name
        self.code_file_name = code_file_name
        if(ct.can_be_read(map_file_name)):
            #store file text in 2D Array
            self.map_array = ct.store_map(map_file_name)
        if(ct.can_be_read(code_file_name)):
            self.code = ct.store_map()
        self.view_bounds = 25
        self.set_map_bounds()


    def longest_x(self):
        
        return
    def set_map_bounds(self):
        self.longest_x()

#Read input file or last stored file
#Store input file name in txt
#Store file text in 2D Array

#CREATE GUI
#Box one allows input, titled "INPUT"
#Coordinates box put below Box one, can be changed
#Coord jump arrow buttons surround another input box, which adds that amount to the viewbounds
#  /\
#< 10 >
#  \/
#Box two does not allow input, titled "OUTPUT"
#code file name input box placed below Box two
#"update" button next to code file name input box
#Create small input box LAST, asking for inputfilename

#FILE WRITING
#When item is changed, next item over is deleted
#Change is stored in a 3-length list: x,y,character
#Coordinate Markers on outside edge of Box one text canNOT be changed
#Outside edge is colored GREY
'''
30
>


25
>
  ^10  ^15  ^20
'''