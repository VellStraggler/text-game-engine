import textengine as tx
from random import randint
from time import time

g = tx.Game()
g.curr_map.set_path('tetris/tetris_map.txt')
g.objs.get_sprites('tetris/tetris_sprites.txt')
g.add_theme('tetris/song.wav')

p1 = g.objs.Obj(str(randint(1,9)),'l',move = "wasd",grav=True,
    xspeed =50,yspeed = 5,geom="complex",animate=None,
    data={"spawn":[27,9],"box":[6,12,25,42],"rest":0})
g.objs.append_obj(p1)

p2 = g.objs.Obj(str(randint(1,9)),'o',move = "dirs",grav=False,
    xspeed =50,yspeed = 4,geom="complex",animate=None,
    data = {"spawn":[73,9],"box":[6,58,25,88],"rest":0})
g.objs.append_obj(p2)

g.acts.new("","interact","l","rotate")
g.acts.new("","interact","o","rotate")

g.objs.new('piece','p')
g.objs.new('side','s')
g.objs.new('floor','f')
g.objs.new('title','t')
g.objs.new('score2','y')
g.objs.new('score1','u')

def main():
    g.init_map()
    while(not g.quit):
        g.frame_start = time()
        g.move_all()
        for obj in g.objs.objs:
            if obj.move in ["wasd","dirs"]:
                if g.can_move(obj,move_y=1):
                    obj.data["rest"] = time()
                elif g.frame_start - obj.data["rest"] > .2:
                    for y in range(obj.origy-obj.height(),obj.origy+1):
                        for x in range(obj.origx,obj.origx+obj.width()):
                            if g.curr_map.get_xy_geom(x,y) != tx.BLANK:
                                g.add_to_sparse(x,y,"p")
                    g.set_new_img(obj,str(randint(1,9)))
                    obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
                    g.teleport_obj(obj,obj.data["spawn"][0],obj.data["spawn"][1])
                    for y in range(obj.data["box"][0],obj.data["box"][2]):
                        no_space = True
                        for x in range(obj.data["box"][1],obj.data["box"][3]):
                            if g.curr_map.get_xy_rend(x,y) == tx.BLANK:
                                no_space = False
                        if no_space:
                            obj.score += 100
                            for by in range(y,obj.data["box"][0],-1):
                                for x in range(obj.data["box"][1],obj.data["box"][3]):
                                    g.curr_map.set_xy_rend(x,by,g.curr_map.get_xy_rend(x,by-1))
        g.create_map()
        g.curr_map.print_all()
        g.run_fps()
    g.end_game()
main()