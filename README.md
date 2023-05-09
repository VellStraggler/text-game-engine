# The TXT Game Engine
Developer: David Wells
## Setup:
There are four main file-types to any videogame made with this engine. The **Sprite file**, the **Map file**, the **Speech file** and the **Python Code file**. All of these are to remain in the same folder.

## 1. The Sprite file

This is simply a text file filled with sprite designs. The image of any one of these is known as a **sprite**. To store a sprite, create a text file under any name you think would be useful. Here's what goes inside:

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

There is very little you have to specify to tell the program what these characters are meant to represent. All of that will go into your **code file** except for ONE character.
"g" is already stored as invisible geometry 1x1 in size. These only get initiated as objects, and once the map is loaded, all that is left behind is plain collidable geometry. We suggest using these as often as you can along with background objects for a faster game. We talk about background objects in "The Python Code file".
## 3. The Python Code file
### The Basics
So much of the Text Game Engine runs in the background that you need as little as 6 lines to have a map you can move a character on. Here we use 7 (so we can have trees AND walls):
```python
import textengine as tx
g = tx.Game()
g.map.set_path('map.txt')
g.objs.get_sprites('sprites.txt')
g.objs.new('wall','w')
g.objs.new('tree','t')
g.run_map()
```
### Adding Objects
In this engine, maps are made up of objects of all kinds. As shown in the section "The Basics", it is simple to get a quick number of objects created. But suppose you want your character to be able to walk *behind* an object. By default, object geometry (with the variable name *geom*) is set to "all", meaning nothing can go through any part of it. By setting this to "line", you can give it collision only on the bottom row of characters, like so:
```python
g.objs.new('tree','t',geom="line")
```
Here is a visual of where the geometry is drawn with almost every kind of geometry:

                with "all"    with "line"   with "complex"   with "skeleton"
       sprite:   geometry:     geometry:      geometry:        geometry:
         /\        ####          ____           _##_             ____
        /v \       ####          ____           ####             ____
        /_v\       ####          ____           ####             ____
         ||        ####          ####           _##_             _##_

The exceptions not shown are "background" and None. Neither actually produce any geometry, so you might wonder about the difference. An object with "background" geometry actually gets removed after drawing on the map. It is purely a detail. This was added so that *1*, you could have things like carpets, and *2*, so that your game would not be slowed down by looping through it. This means that you can add lots and lots of background objects with very few side effects

### Adding Sounds
Something that simplifies TGE is that certain actions taken by any object will produce the same sound. For example, when an object jumps, it looks in the g.sounds dictionary for "jump", and plays the sound stored there. There are no default sounds, so the user must add this themselves. The code to do so is very simple. Say the audio file happens to be called "jump.wav" and in a folder called "afolder". Just write this into your code file:
```python
g.add_sound("afolder/jump.wav")
```
The add_sound function will take the given sound path argument, remove the ".wav", and remove the folder names and slashes if there are any, and then will use that as the dictionary key. It can also take a second argument as the dictionary key instead. If your file path is "anotherfolder/sound4.wav", and you want to add a pain sound, do this:
```python
g.add_sound("anotherfolder/sound4.wav"."pain")
```
Here is the full list of supported sounds that the game will play automatically:
* jump
* death
* quit
Here are the sounds we may add in the future.
* move
* pain
* attack
* teleport
* rotate
* pause
* objective-get
* objective-finish
* objective-failed
* talk


### Conclusion
There are some pre-made programs that you can look at, the primary one being undertaker. Most recently, a reflection feature was added so that things like water and mirrors could be placed in-game. If you have any questions you need answered, please contact me from any of the social media sites featured in my bio:

https://github.com/VellStraggler

# DEVELOPER NOTES
* Textengine uses the module playsound version 1.2.2, NOT the latest
* Only WAV files work for playing sound or music. MP3 will probably not work.
* There is a MAX SPEED for any given object. It is the framerate.
* Every line of any map file must have SOMETHING in it (such as a space).
* The escape codes used in this engine are SCO sequences.
* icoconverter.com is a great website to create an icon for a SHORTCUT to your Python executable.
* It is suggested that the dimensions of your sprites do not exceed the dimensions of a chunk.
