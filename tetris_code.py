import textengine as tx
import random

g = tx.Game()
g.map.set_path('tetris/tetris2p_map.txt')
g.objs.get_sprites('tetris/tetris_sprites.txt')

g.objs.new(str(random.randint(1,9)),'l',move = "wasd",grav_tick=8,
    xspeed =2,yspeed = 1,geom="complex",spawn=[9,27])
p1_box = [8,12,27,42]
p1_score = '\033[27;32H'

g.objs.new(str(random.randint(1,9)),'o',move = "dirs",grav_tick=10,
    xspeed =2,yspeed = 1,geom="complex",spawn=[9,73])
p2_box = [8,60,27,90]
p2_score = '\033[27;78H'

g.objs.new('piece','p')
g.objs.new('side','s')
g.objs.new('floor','f')
g.objs.new('title','t')
g.objs.new('score2','y')
g.objs.new('score1','u')

g.gamespeed = .03

def run_tetris():
    stuck = 0
    g.init_map()
    while(not g.quit):
        g.game_loop()
        # ADDED ITEMS
        for i in g.objs.live_objs:
            obj = g.objs.objs[i]
            if not g.tick%obj.grav_tick:
                if not g.can_move(obj,move_y=1):
                    stuck += 1
                    if obj.move == "wasd" or obj.move == "dirs":
                        g.replace_chars(obj,'p')
                        g.teleport_obj(obj,obj.spawn[0],obj.spawn[1])
                        g.set_new_img(obj,str(random.randint(1,9)))
                        
                        if obj.move == "wasd":  box = p1_box
                        else:                   box = p2_box
                        for y in range(box[0],box[2]):
                            no_space = True
                            for x in range(box[1],box[3]):
                                if g.map.is_xy(x,y," ",'o'):
                                    no_space = False
                            if no_space:
                                for by in range(y,box[0],-1):
                                    for x in range(box[1],box[3]):
                                        g.map.set_xy(x,by,g.map.get_xy(x,by-1,'i'),'i')
                                obj.score += 100
                    if stuck > 3:
                        g.quit = True
                else:
                    stuck = 0
            if obj.topleft[0]%2 != 1:
                g.move_obj(obj,-1)
    g.end_game()

run_tetris()