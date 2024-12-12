import sys
import os

# Add the parent folder of "textengine.py" to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import textengine as tx
from random import randint
from time import time

g = tx.Game()
g.set_map_path('tetris/tetris_map.txt')
g.set_sprite_path('tetris/tetris_sprites.txt')
g.set_theme('tetris/song.wav')
g.camera_follow = []

p1 = g.objs.Obj(str(randint(1,9)),'l',move = "wasd",grav=True,
    xspeed =50,yspeed = 5,geom="complex",animate=None,
    data={"spawn":[27,9],"box":[6,12,25,42],"rest":0})
g.objs.add_to_pallete(p1)

p2 = g.objs.Obj(str(randint(1,9)),'o',move = "dirs",grav=False,
    xspeed =50,yspeed = 4,geom="complex",animate=None,
    data = {"spawn":[73,9],"box":[6,58,25,88],"rest":0})
g.objs.add_to_pallete(p2)

g.new_action(g.act_rotate,"interact","l","rotate")
g.new_action(g.act_rotate,"interact","o","rotate")

g.new_object('piece','p')
g.new_object('side','s')
g.new_object('floor','f')
g.new_object('title','t')
g.new_object('score2','y')
g.new_object('score1','u')

# g.new_action(new_block)
g.run_game()

# def main():
#     g.init_map()
#     while(not g.quit):
#         g.frame_start = time()
#         g.set_all_movement()
#         g.set_load_chunks()
#         g.remove_the_dead()
#         for chunk in g.objs.load_chunks:
#             for line in chunk.values():
#                 for obj in line:
#                     if obj.move in ["wasd","dirs"]:
#                         if g.can_move(obj,0,1):
#                             obj.data["rest"] = time()
#                         elif g.frame_start - obj.data["rest"] > .2:
#                             for y in range(obj.origy-obj.height(),obj.origy+1):
#                                 for x in range(obj.origx,obj.origx+obj.width()):
#                                     if g.map.get_xy_geom(x,y) != tx.BLANK:
#                                         g.add_to_sparse(x,y,"p")
#                             g.set_new_img(obj,str(randint(1,9)))
#                             obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
#                             g.teleport_obj(obj,obj.data["spawn"][0],obj.data["spawn"][1])
#                             for y in range(obj.data["box"][0],obj.data["box"][2]):
#                                 no_space = True
#                                 for x in range(obj.data["box"][1],obj.data["box"][3]):
#                                     if g.map.get_xy_rend(x,y) == tx.BLANK:
#                                         no_space = False
#                                 if no_space:
#                                     obj.score += 100
#                                     for by in range(y,obj.data["box"][0],-1):
#                                         for x in range(obj.data["box"][1],obj.data["box"][3]):
#                                             g.map.set_xy_rend(x,by,g.map.get_xy_rend(x,by-1))
#         g.print_all()
#     g.end_game()
# main()