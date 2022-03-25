move_dict = {0:{1:"w",0:"d",-1:"s"}, 
                          1:{0:"d"},
                         -1:{0:"a"}}
assert move_dict[0][1] == "w"
assert move_dict[0][0] == "d"