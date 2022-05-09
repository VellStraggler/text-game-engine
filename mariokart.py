import textengine as tx
from time import sleep,time
g = tx.Game()
g.set_map_path("mariokart/test_map.txt")
g.set_sprite_path("mariokart/karts.txt")
g.objs.new("mario-w","m",xspeed = 20,yspeed=10,geom="line",color=124)
g.objs.new("block","b",geom="complex")

g.objs.sprites["mario-a"] = g.objs.get_flipped_sprite(g.objs.sprites["mario"])
g.objs.sprites["mario-a1"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d1"])
g.objs.sprites["mario-a2"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d2"])
g.objs.sprites["mario-a3"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d3"])
g.objs.sprites["mario-a4"] = g.objs.get_flipped_sprite(g.objs.sprites["mario-d4"])
skins = ["mario-d2","mario-d1","mario","mario-w","mario-a","mario-a1","mario-a2","mario-a3","mario-a4","mario-s","mario-d4","mario-d3"]
def game_loop(g):
    g.frame_start = time()
    g.move_all()
    g.render_all()
    g.map.display_timer()
    g.map.print_all(g.display_data)
    g.run_fps(True)
    return g
g.init_map()
i=0
while not g.quit:
    sleep(.3)
    g.reload_screen()
    g = game_loop(g)
    for obj in g.objs.objs:
        if obj.char == "m":
            mario = obj
            g.set_sprite(mario,skins[i])
            i = (i+1)%len(skins)
