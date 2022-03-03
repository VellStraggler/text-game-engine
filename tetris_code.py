import textengine as tx
import random

g = tx.Game()
g.map.set_path('tetris2p_map.txt')
g.objs.get_sprites('tetris_sprites.txt')

blocks = ['1','2','3','4','5','6']
g.objs.new(blocks[random.randint(0,5)],'l',move = "wasd",grav=True,
    xspeed =2,yspeed = 1,geom="all")
g.objs.new(blocks[random.randint(0,5)],'o',move = "dirs",grav=True,
    xspeed =2,yspeed = 1,geom="all")
g.objs.new('piece','p',geom="all")
g.objs.new('side','s',geom="all")
g.objs.new('corner','c',geom="all")
g.objs.new('floor','f',geom="all")
g.objs.new('title','t')

def run_tetris():
    g.init_map()
    while(not g.quit):
        for i in g.objs.live_objs:
            obj = g.objs.objs[i]
            if not g.can_move(obj,move_y=1):
                if obj.move == "wasd":
                    g.teleport_obj(obj,9,28,"p")
                    obj.array = g.objs.sprites[blocks[random.randint(0,5)]]
                elif obj.move == "dirs":
                    g.teleport_obj(obj,9,74,"p")
                    obj.array = g.objs.sprites[blocks[random.randint(0,5)]]
        g.game_loop()
        # ADDED ITEMS
    g.end_game()

run_tetris()