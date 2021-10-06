from tkinter import *
import time
def main():
    root = Tk()
    root.geometry("600x700+300+0")
    canvas = Canvas(root)
    canvas.master.title('Text Art V2.1')

    charx = 67
    chary = 40
    doclen = charx*chary

    doc=""
    for cols in range(0,charx):
        for rows in range(0,chary):
            doc += " "

    e = Text(root, width=67, height=40)
    e.insert('1.0',doc)
    e.grid(column=1,columnspan=9,row=3,padx=28)

    srch_entry = Entry(root)
    srch_entry.insert(0,"File Name: ")
    srch_entry.grid(row=2,column=3)
    
    def press_save(alltext,textname):
        if textname == 'File Name: ':
            textname = untitled.txt  
        with open(textname,"w") as file_name:
            file_name.write(alltext)

    save = Button(root, text='Save')
    save.configure(command= lambda: press_save(e.get('1.0',END),srch_entry.get()))
    save.grid(row=2,column=1,pady=5)
    
    def clear(txt):
        txt.delete('1.0',END)
        txt.insert('1.0',doc)
        return txt
    clear_e = Button(root, text='Clear Page',command=lambda: clear(e))
    clear_e.grid(row=2, column=6)

    def search(doc_name):
        try:
            filename = open(doc_name,"r")
            clear(e)
            copy = filename.read()
            e.insert('1.0',copy)
        except FileNotFoundError as ex:
            srch_entry.delete(0,len(srch_entry.get()))
            srch_entry.insert(0,'FILE NOT FOUND')
        return copy

    open_button = Button(root, text='Open',command=lambda: search(srch_entry.get()))
    open_button.grid(row=2,column=2)

    while True:
        ins = int((str(e.index(INSERT)).split('.'))[1])
        if len(e.get('1.0',END)) > doclen: #A CHARACTER HAS BEEN ADDED    
            if e.get(INSERT,'insert+2c') == "  ":
                e.delete('insert+2c')
        elif len(e.get('1.0',END)) < doclen:
            addspace = '1.'+str(ins-(ins % charx)+charx-1)
            e.insert( addspace ,' ')
        root.update()
    root.mainloop()
    
main()