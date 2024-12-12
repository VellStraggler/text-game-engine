import sys
import os

# Add the parent folder of "textengine.py" to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from linked import Linked
import textengine as tx
from time import sleep,time
g = tx.Game()
g.set_map_path("mariokart/test_map.txt")
g.set_sprite_path("mariokart/karts.txt")
g.set_theme("mariokart/mariokart.wav")

g.objs.sprites["right-block"] = g.objs.get_flipped_sprite(g.objs.sprites["block"])
g.new_object("right-block","b",geom="complex")
g.new_object("finish-line","f",geom="background")
g.new_lap = True
g.counter = 0
g.timer = 0
def cross_line(obj, arg):
    if(not g.new_lap):
        g.counter += 1
        if(g.counter == 3):
            g.act_message(obj,"Finish!")
            g.act_change_theme(obj,"mariokart/finish.wav")
            g.new_action(end_game,"end","timer",arg=[time() + 4,""])
        elif(g.counter == 2):
            g.act_message(obj,"last lap!")
            g.act_change_theme(obj,"mariokart/lastlap.wav")
            g.new_action(g.act_change_theme,"base theme", "timer",arg=[time() + 2,"mariokart/fast.wav"])
        else:
            g.act_message(obj,"new lap!")
            g.act_change_theme(obj,"mariokart/lastlap.wav")
            g.new_action(g.act_change_theme,"base theme", "timer",arg=[time() + 2,"mariokart/mariokart.wav"])

    g.new_lap = True
def cross_mid(obj, arg):
    if(g.new_lap):
        g.new_lap = False
def return_to_theme(obj, arg):
    g.act_change_theme(obj, "mariokart/mariokart.wav")
def end_game(obj,arg):
    quit()
g.new_action(cross_line,"cross line","location",loc_arg=[82,-1])
g.new_action(cross_mid,"cross mid", "location", loc_arg=[32,-1])

g.objs.sprites["qblock-f5"] = g.objs.get_flipped_sprite(g.objs.sprites["qblock-f3"])
g.objs.sprites["qblock-f6"] = g.objs.get_flipped_sprite(g.objs.sprites["qblock-f2"])

g.objs.sprites["mario-a"] = g.objs.get_flipped_sprite(g.objs.sprites["mario"])
g.objs.sprites["mario-a1"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d1"])
g.objs.sprites["mario-a2"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d2"])
g.objs.sprites["mario-a3"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d3"])
g.objs.sprites["mario-a4"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d4"])
skins = Linked(["mario","mario-d3","mario-d4","mario-s","mario-a4","mario-a3",
                "mario-a","mario-a1","mario-a2","mario-w", "mario-d2", "mario-d1"],True)
g.new_object("mario","m",xspeed = 20,yspeed=10,move="drive",geom="line",color=124, animate = skins)

block_frames = Linked(["qblock-f1","qblock-f2","qblock-f3","qblock-f4","qblock-f5","qblock-f6"],True)
g.new_object("qblock-f1","q",animate=block_frames, geom="line")
g.run_game()