import textengine as tx

def main():
    g = tx.Game()
    g.map.set_path('mario/mario_map.txt')
    g.objs.get_sprites('mario/mario_sprites.txt')
    g.camera_follow = ["x"]
    g.game_speed = 0.0
    
    g.objs.new('mario','m',move = "wasd",grav_tick=1,
        xspeed =3,yspeed = 3,enemy_chars=['g','f'],
        dmg_dirs=['down'])
    g.objs.new('goomba','g',move = "leftright",grav_tick=1,
        dmg_dirs=['left','right','down'],enemy_chars=['m'])
    g.objs.new('block','b')
    g.objs.new('block2','v')
    g.objs.new('pipe','p')
    g.objs.new('flag','f',geom="line")

    g.run_game()

while True:
    main()