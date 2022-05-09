import textengine as tx

def rand():
    return tx.color_by_num(tx.randint(0,255))

def main():
    g = tx.Game()
    g.set_map_path('mario/mario_map.txt')
    g.set_sprite_path('mario/mario_sprites.txt')
    g.set_theme('mario/text_mario.wav')
    g.add_sounds_simple(["jump","death","quit"],"mario")
    g.camera_follow = ["x","y"]

    g.acts.new("","touch","g","switch_map",["f","mario/mario_test_.txt"])
    g.acts.new("","touch","g","up_score",["g",10])
    g.acts.new("","location","m","quit",[-1,31])
    
    g.objs.new('mario','m',geom="complex",move = "wasd",grav=True,
        xspeed =70,yspeed = 30,max_jump=15,enemy_chars=['g','f'],
        dmg_dirs=['down'],animate="flip",color=rand())
    g.objs.new('goomba','g',move = "leftright",grav=True,
        xspeed =10,yspeed=30,animate="flip",
        dmg_dirs=['left','right','down'],enemy_chars=['m'],color=rand())
    g.objs.new('block','b',color=rand())
    g.objs.new('block2','v')
    g.objs.new('pipe','p',color=rand())
    g.objs.new('flag','f',geom="line",color=rand())

    g.run_game()

while True:
    main()