from win32api   import GetAsyncKeyState
from keyboard   import is_pressed as GetKBpressed
from tkinter    import Frame, Button, Toplevel, font, Tk
from Constants  import PATCH, APPLICATION_ICON
from PIL        import Image as Img
from PIL        import ImageTk



HandleKeyPress = {
    "AC":lambda:GetKBpressed(           "f2"), #F2
    "AD":lambda:GetKBpressed(           "f3"), #F3
    "AE":lambda:GetKBpressed(           "f4"), #F4
    "AF":lambda:GetKBpressed(           "f5"), #F5
    "AG":lambda:GetKBpressed(           "f6"), #F6
    "AH":lambda:GetKBpressed(           "f7"), #F7
    "AI":lambda:GetKBpressed(           "f8"), #F8
    "AK":lambda:GetKBpressed(          "f10"), #F10
    "AL":lambda:GetKBpressed(          "f11"), #F11

    "BA":lambda:GetKBpressed(            "~"), #~
    "BN":lambda:GetKBpressed(    "backspace"), #Backspace

    "CG":lambda:GetKBpressed(            "y"), #y
    "CH":lambda:GetKBpressed(            "u"), #u
    "CN":lambda:GetKBpressed(           "\\"), #\

    "DA":lambda:GetKBpressed(     "capslock"), #CapsLock
    "DH":lambda:GetKBpressed(            "j"), #j
    "DI":lambda:GetKBpressed(            "k"), #k
    "DJ":lambda:GetKBpressed(            "l"), #l
    "DK":lambda:GetKBpressed(            ";"), #;
    "DL":lambda:GetKBpressed(           "\""), #"

    "EB":lambda:GetKBpressed(            "z"), #c
    "EC":lambda:GetKBpressed(            "x"), #c
    "ED":lambda:GetKBpressed(            "c"), #c
    "EF":lambda:GetKBpressed(            "b"), #b
    "EI":lambda:GetKBpressed(            ","), #,
    "EJ":lambda:GetKBpressed(            "."), #.
    "EK":lambda:GetKBpressed(            "/"), #/
    "EL":lambda:GetKBpressed(  "right shift"), #Right-Shift
    "EM":lambda:GetKBpressed(           "up"), #Up-Arrow

    "FC":lambda:GetKBpressed(     "left alt"), #Left-Alt
    "FD":lambda:GetKBpressed(        "space"), #Space
    "FE":lambda:GetKBpressed(    "right alt"), #Right-Alt
    "FH":lambda:GetKBpressed("right control"), #Right-Control
    "FI":lambda:GetKBpressed(         "left"), #/
    "FJ":lambda:GetKBpressed(         "down"), #Right-Shift
    "FK":lambda:GetKBpressed(        "right"), #Up-Arrow

    "M1":lambda:(GetAsyncKeyState(0x1) & 0x8000 > 0), #Mouse 1
    "M2":lambda:(GetAsyncKeyState(0x2) & 0x8000 > 0), #Mouse 2
    "M4":lambda:(GetAsyncKeyState(0x5) & 0x8000 > 0), #Mouse 4
    "M5":lambda:(GetAsyncKeyState(0x6) & 0x8000 > 0), #Mouse 5
}
Button_Info = [
    #text     , repr, c, r, cs, rs, support
    ["ESC"    , "AA", 0, 0,  2,  2,   False],
    ["GAP"    ,   "", 2, 0,  1,  2,   False],
    ["F1"     , "AB", 3, 0,  2,  2,   False],
    ["F2"     , "AC", 5, 0,  2,  2,    True],
    ["F3"     , "AD", 7, 0,  2,  2,    True],
    ["F4"     , "AE", 9, 0,  2,  2,    True],
    ["GAP"    ,   "",11, 0,  2,  2,   False],
    ["F5"     , "AF",13, 0,  2,  2,    True],
    ["F6"     , "AG",15, 0,  2,  2,    True],
    ["F7"     , "AH",17, 0,  2,  2,    True],
    ["F8"     , "AI",19, 0,  2,  2,    True],
    ["GAP"    ,   "",21, 0,  1,  2,   False],
    ["F9"     , "AJ",22, 0,  2,  2,   False],
    ["F10"    , "AK",24, 0,  2,  2,    True],
    ["F11"    , "AL",26, 0,  2,  2,    True],
    ["F12"    , "AM",28, 0,  2,  2,   False],

    ["~"      , "BA", 0, 2,  2,  2,    True],
    ["1"      , "BB", 2, 2,  2,  2,   False],
    ["2"      , "BC", 4, 2,  2,  2,   False],
    ["3"      , "BD", 6, 2,  2,  2,   False],
    ["4"      , "BE", 8, 2,  2,  2,   False],
    ["5"      , "BF",10, 2,  2,  2,   False],
    ["6"      , "BG",12, 2,  2,  2,   False],
    ["7"      , "BH",14, 2,  2,  2,   False],
    ["8"      , "BI",16, 2,  2,  2,   False],
    ["9"      , "BJ",18, 2,  2,  2,   False],
    ["0"      , "BK",20, 2,  2,  2,   False],
    ["-"      , "BL",22, 2,  2,  2,   False],
    ["="      , "BM",24, 2,  2,  2,   False],
    ["<--"    , "BN",26, 2,  4,  2,    True],
    ["GAP"    ,   "",30, 2,  1,  2,   False],
    ["SC"     , "BO",31, 2,  2,  2,   False],
    ["SL"     , "BP",33, 2,  2,  2,   False],
    ["PB"     , "BQ",35, 2,  2,  2,   False],
    ["GAP"    ,   "",37, 2,  1,  2,   False],
    ["NL"     , "BR",38, 2,  2,  2,   False],
    ["/"      , "BS",40, 2,  2,  2,   False],
    ["*"      , "BT",42, 2,  2,  2,   False],
    ["-"      , "BU",44, 2,  2,  2,   False],
    ["GAP"    ,   "",46, 2,  2,  2,   False],
    ["GAP"    ,   "",48, 2,  2,  2,   False],
    ["M1"     , "M1",50, 2,  2,  4,   False],
    ["M3"     , "M3",52, 2,  2,  4,   False],
    ["M2"     , "M2",54, 2,  2,  4,   False],

    ["Tab"    , "CA", 0, 4,  3,  2,   False],
    ["Q"      , "CB", 3, 4,  2,  2,   False],
    ["W"      , "CC", 5, 4,  2,  2,   False],
    ["E"      , "CD", 7, 4,  2,  2,   False],
    ["R"      , "CE", 9, 4,  2,  2,   False],
    ["T"      , "CF",11, 4,  2,  2,   False],
    ["Y"      , "CG",13, 4,  2,  2,    True],
    ["U"      , "CH",15, 4,  2,  2,    True],
    ["I"      , "CI",17, 4,  2,  2,   False],
    ["O"      , "CJ",19, 4,  2,  2,   False],
    ["P"      , "CK",21, 4,  2,  2,   False],
    ["["      , "CL",23, 4,  2,  2,   False],
    ["]"      , "CM",25, 4,  2,  2,   False],
    ["\\"     , "CN",27, 4,  3,  2,    True],
    ["GAP"    ,   "",30, 4,  1,  2,   False],
    ["Ins"    , "CO",31, 4,  2,  2,   False],
    ["Home"   , "CP",33, 4,  2,  2,   False],
    ["PgU"    , "CQ",35, 4,  2,  2,   False],
    ["GAP"    ,   "",37, 4,  1,  2,   False],
    ["7"      , "CR",38, 4,  2,  2,   False],
    ["8"      , "CS",40, 4,  2,  2,   False],
    ["9"      , "CT",42, 4,  2,  2,   False],
    ["+"      , "DT",44, 4,  2,  4,   False],
    ["GAP"    ,   "",46, 4,  2,  2,   False],
    ["M5"     , "M5",48, 4,  2,  4,    True],

    ["Caps"   , "DA", 0, 6,  4,  2,    True],
    ["A"      , "DB", 4, 6,  2,  2,   False],
    ["S"      , "DC", 6, 6,  2,  2,   False],
    ["D"      , "DD", 8, 6,  2,  2,   False],
    ["F"      , "DE",10, 6,  2,  2,   False],
    ["G"      , "DF",12, 6,  2,  2,   False],
    ["H"      , "DG",14, 6,  2,  2,   False],
    ["J"      , "DH",16, 6,  2,  2,    True],
    ["K"      , "DI",18, 6,  2,  2,    True],
    ["L"      , "DJ",20, 6,  2,  2,    True],
    [";"      , "DK",22, 6,  2,  2,    True],
    ["\""     , "DL",24, 6,  2,  2,    True],
    ["Entr"   , "DM",26, 6,  4,  2,   False],
    ["GAP"    ,   "",30, 6,  1,  2,   False],
    ["Del"    , "DN",31, 6,  2,  2,   False],
    ["End"    , "DO",33, 6,  2,  2,   False],
    ["PgD"    , "DP",35, 6,  2,  2,   False],
    ["GAP"    ,   "",37, 6,  1,  2,   False],
    ["4"      , "DQ",38, 6,  2,  2,   False],
    ["5"      , "DR",40, 6,  2,  2,   False],
    ["6"      , "DS",42, 6,  2,  2,   False],
    ["GAP"    ,   "",46, 6,  2,  2,   False],
    [""       ,   "",50, 6,  6,  6,   False],

    ["L-Shift", "EA", 0, 8,  5,  2,   False],
    ["Z"      , "EB", 5, 8,  2,  2,    True],
    ["X"      , "EC", 7, 8,  2,  2,    True],
    ["C"      , "ED", 9, 8,  2,  2,    True],
    ["V"      , "EE",11, 8,  2,  2,   False],
    ["B"      , "EF",13, 8,  2,  2,    True],
    ["N"      , "EG",15, 8,  2,  2,   False],
    ["M"      , "EH",17, 8,  2,  2,   False],
    [","      , "EI",19, 8,  2,  2,    True],
    ["."      , "EJ",21, 8,  2,  2,    True],
    ["/"      , "EK",23, 8,  2,  2,    True],
    ["R-Shift", "EL",25, 8,  5,  2,    True],
    ["GAP"    ,   "",30, 8,  1,  2,   False],
    ["GAP"    ,   "",31, 8,  2,  2,   False],
    ["Up"     , "EM",33, 8,  2,  2,    True],
    ["GAP"    ,   "",35, 8,  2,  2,   False],
    ["GAP"    ,   "",37, 8,  1,  2,   False],
    ["1"      , "EN",38, 8,  2,  2,   False],
    ["2"      , "EO",40, 8,  2,  2,   False],
    ["3"      , "EP",42, 8,  2,  2,   False],
    ["Enter"  , "FN",44, 8,  2,  4,   False],
    ["GAP"    ,   "",46, 8,  2,  2,   False],
    ["M4"     , "M4",48, 8,  2,  4,    True],

    ["L-Ctrl" , "FA", 0,10,  3,  2,   False],
    ["Win"    , "FB", 3,10,  2,  2,   False],
    ["L-Alt"  , "FC", 5,10,  2,  2,    True],
    ["Space"  , "FD", 7,10, 14,  2,    True],
    ["R-Alt"  , "FE",21,10,  2,  2,    True],
    ["Fn"     , "FF",23,10,  2,  2,   False],
    ["Pg"     , "FG",25,10,  2,  2,   False],
    ["R-Ctrl" , "FH",27,10,  3,  2,    True],
    ["GAP"    ,   "",30,10,  1,  2,   False],
    ["Left"   , "FI",31,10,  2,  2,    True],
    ["Down"   , "FJ",33,10,  2,  2,    True],
    ["Right"  , "FK",35,10,  2,  2,    True],
    ["GAP"    ,   "",37,10,  1,  2,   False],
    ["0"      , "FL",38,10,  4,  2,   False],
    ["."      , "FM",42,10,  2,  2,   False],
]
KeyName2Code = {k[0].upper():k[1].upper() for k in Button_Info}
Code2KeyName = {k[1].upper():k[0].upper() for k in Button_Info}


class VirtualKB():
    def __init__(self, main_window, default, return_func):
        #attributes
        self.Clicked = default
        self.return_func = return_func

        #UI attributes
        self.VBK_Root = Toplevel(main_window)
        self.VBK_Root.attributes('-topmost', True)
        self.VBK_Root.tk.call('wm', 'iconphoto', self.VBK_Root._w, ImageTk.PhotoImage(image=Img.open(APPLICATION_ICON)))
        self.VBK_Root.title(f"ApexGunControl {PATCH} - HotKey")
        self.VBK_Root.resizable(False, False)
        self.VBK_Root["bg"] = "light gray"

        self.VBK_Frame = Frame(self.VBK_Root, background="light gray")
        self.VBK_Frame.pack(padx=20, pady=20)

        for t, rep, c, r, cs, rs, s in Button_Info:
            if t=="GAP":
                self.Create_VKG(canvas=self.VBK_Frame, c=c, cs=cs, r=r, rs=rs, w=30*cs, h=30*rs)
            else:    
                self.Create_VKB(s=s, canvas=self.VBK_Frame, text=t, c=c, cs=cs, r=r, rs=rs, w=30*cs, h=30*rs)

        self.VBK_Root.update()

        x = (main_window.winfo_x()+(main_window.winfo_width()//2))-(self.VBK_Root.winfo_width()//2)
        y = (main_window.winfo_y()+(main_window.winfo_height()//2))-(self.VBK_Root.winfo_height()//2)
        self.VBK_Root.geometry(f"+{x}+{y}")


    def Update(self):
        self.VBK_Root.mainloop()


    def Create_VKB(self, s, canvas, text, c, cs, r, rs, w, h):
        button_frame = Frame(canvas, width=w, height=h)
        button_frame.rowconfigure(0, weight = 1)
        button_frame.columnconfigure(0, weight = 1)
        button_frame.grid_propagate(0)
        button_frame.grid(column=c, columnspan=cs, row=r, rowspan=rs)

        def _Clicked():
            print(text)
            self.Clicked = text
            self.return_func(text)
            self.Close()
        button_button = Button(button_frame, text=text, font=font.Font(family="Terminal", size=16), foreground="green", disabledforeground="red", command=_Clicked)
        button_button.grid(sticky="NWSE")
        button_button["state"] = "normal" if s else "disabled"
        return button_frame, button_button
    
    def Create_VKG(self, canvas, c, cs, r, rs, w, h):
        Gap_frame = Frame(canvas, width=w, height=h, background="light gray")
        Gap_frame.rowconfigure(0, weight = 1)
        Gap_frame.columnconfigure(0, weight = 1)
        Gap_frame.grid_propagate(0)
        Gap_frame.grid(column=c, columnspan=cs, row=r, rowspan=rs)
        return Gap_frame

    
    def Close(self):
        self.VBK_Root.destroy()
        print("close")



if __name__ == "__main__":
    for data in Button_Info:
        if not data[6]: continue
        if not HandleKeyPress.get(data[1], False):
            raise KeyError(data[1])


    tk = Tk()
    VirtualKB(tk, "M4", lambda x:x).Update()
    tk.mainloop()
