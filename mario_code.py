import textengine as tx

def main():
    g = tx.Game()
    g.curr_map.set_path('mario/mario_map.txt')
    g.objs.get_sprites('mario/mario_sprites.txt')
    g.add_theme('mario/text_mario.wav')
    g.add_sounds_simple(["jump","death","quit"],"mario")
    g.set_default_color(tx.color_by_num(4))
    g.camera_follow = ["x","y"]

    g.acts.new("","touch","g","switch_map",["f","mario/mario_test_.txt"])
    g.acts.new("","touch","g","up_score",["g",10])
    g.acts.new("","location","m","quit",[-1,31])
    
    g.objs.new('mario','m',geom="complex",move = "wasd",grav=True,
        xspeed =70,yspeed = 30,max_jump=15,enemy_chars=['g','f'],
        dmg_dirs=['down'],animate="flip",color=1)
    g.objs.new('goomba','g',move = None,grav=True,
        xspeed =10,yspeed=30,animate="flip",
        dmg_dirs=['left','right','down'],enemy_chars=['m'],color=52)
    g.objs.new('block','b',color=237)
    g.objs.new('block2','v')
    g.objs.new('pipe','p',color=40)
    g.objs.new('flag','f',geom="line",color=11)

    g.run_game()

while True:
    main()