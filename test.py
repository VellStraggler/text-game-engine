import keyboard
from time import sleep,time
key_dict_1 = {"w":'move_up',"a":'move_left',
                            "s": 'move_down',"d": 'move_right',
                            "e": 'interact_true',"r": 'rotate_right'}
start = time()
while time() - start < 30:
    for key in key_dict_1.keys():
        if keyboard.is_pressed(key):
            print(key_dict_1[key])
