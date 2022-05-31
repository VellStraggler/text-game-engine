import textengine as tx

def rand():
    return tx.color_by_num(tx.randint(0,255))

def main():
    g = tx.Game()
    g.set_map_path('mario/map.txt')
    g.set_sprite_path('mario/sprites.txt')
    g.set_theme('mario/text_mario.wav')
    g.add_sounds_simple(["jump","death","quit"],"mario")
    g.camera_follow = ["x","y"]

    g.acts.new("","touch","g","change_map",["f","mario/map.txt","mario/map2.txt"])
    g.acts.new("","location","m","quit",[-1,31])
    
    g.objs.new('mario','m',geom="complex",move = "wasd",grav=True,
        xspeed =70,yspeed = 30,max_jump=15,enemy_chars=['g'],
        dmg_dirs=['up','down'],animate="flip")
    g.objs.new('goomba','k',move = "leftright",grav=True,
        xspeed =10,yspeed=30,animate="flip",geom="all",
        dmg_dirs=[],enemy_chars=['m'])
    g.objs.new('block','b',color=rand())
    g.objs.new('block2','v')
    g.objs.new('pipe','p')
    g.objs.new('flag','f',geom="line",color=rand())

    g.run_game()

while True:
    main()