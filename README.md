# The TXT Game Engine
Developer: David Wells
## Setup:
There are three main aspects to any videogame made with this engine. The **Sprite file**, the **Map file**, and the **Python Code file**. It is essential that all of these stay in the same folder.

## 1. The Sprite file

It is horribly simple to create a character or a tree, or a house or celery. The image of any one of these is known as a **sprite**. To store a sprite, create a text file under any name you think would be useful. Here's what goes inside:

        $The name of the sprite goes here$ 
        The sprite is drawn here
        $The name of the next sprite or nothing goes here$

Note the "$" symbols. Any sprite name must be between two of these, and unfortunately, this is the *one* character that you cannot use to draw your sprites. Here is an example Sprite File:

        $tree$
         /\ 
        /v \
        /_v\
         || 
        $wall$
        []
        $$
## 2. The Map file
    
The Map File is even more simplified than the Sprite File. To create one, you just need another text file. Any character put in this file will represent a sprite, meaning that the number of different sprites you can have on one map is limited by the number of characters you can manage to come up with. For regular characters, that puts your limit at about 94. More characters can be found on this website:

https://copypastecharacter.com/all-characters
    
    Here is an example map file:

                            w
            t               w
                            w              t
                    t       w
         t                  w                        t
                            w       t

There is very little you have to specify to tell the program what these characters are meant to represent. All of that will go into your **code file**. 
## 3. The Python Code file

So much of the Text Game Engine runs in the background that you need as little as 6 lines to have a map you can move a character on. Here we use 7 (so we can have trees AND walls):
```python
import textengine as tx
g = tx.GameObject()
g.map.set_path('map.txt')
g.sprites.get_sprites('sprites.txt')
g.sprites.new('wall','w')
g.sprites.new('tree','t')
g.run_map()
```
