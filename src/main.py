#tkinter UI imports
from tkinter                import Tk, Label, Button, Entry, Canvas, Toplevel, Scale, StringVar, IntVar, Checkbutton
from tkinter                import ttk, filedialog, messagebox, font
from tkinter                import NW, HORIZONTAL, VERTICAL, END
from PIL                    import Image as Img
from PIL                    import ImageTk

#Images and byte related modules
from assets                 import patch_template_img_byte
from assets                 import background_img_byte
from assets                 import contact_button_img_byte
from assets                 import float_window_button_img_byte
from assets                 import information_button_img_byte
from assets                 import choose_button_img_byte
from assets                 import repair_button_img_byte
from assets                 import settings_button_img_byte
from assets                 import work_template_img_byte
from base64                 import b64decode
from io                     import BytesIO

# Input related
from win32gui               import FindWindow, GetWindowRect, GetWindowDC, ReleaseDC, DeleteObject
from KeyHandler             import HandleKeyPress, KeyName2Code, Code2KeyName, VirtualKB
from win32ui                import CreateDCFromHandle, CreateBitmap
from win32con               import SRCCOPY, MOUSEEVENTF_MOVE
import pydirectinput; pydirectinput.FAILSAFE = False
import win32api

# CV related
from ctypes                 import windll; user32 = windll.user32; user32.SetProcessDPIAware()
from cv2                    import resize, cvtColor, threshold, matchTemplate, minMaxLoc, imwrite
from cv2                    import COLOR_BGR2GRAY, THRESH_BINARY, TM_CCOEFF_NORMED
from numpy                  import frombuffer, ascontiguousarray, array, uint8

# Web related
from webbrowser             import open as OpenBrowser
from requests               import get as Connect_API
from requests.exceptions    import ConnectionError
from urllib.request         import urlretrieve
from urllib.error           import HTTPError

# Path management
from sys                    import executable as Self_As_Executable
from sys                    import argv as Sys_argv
from os                     import path as Path_Manager
from os                     import listdir, remove

# Process control
from os                     import _exit as Exit_Program
from gc                     import collect as ClearRAM
from time                   import sleep as delay
from threading              import Thread
from sys                    import exc_info as extractError
from traceback              import extract_tb as getError

# ApexGunControl imports
from cfg                    import default_cfg, GunControl_cfg_Base, Movement_cfg_Base, MOVEMENTKEY, SHOOTKEY
from GunData                import Gun_Handler; Gun_Data = Gun_Handler()
from Constants              import PATCH, APPLICATION_NAME, APPLICATION_ICON, Project_Main_URL



def Get_Error(e):
    error_class = e.__class__.__name__
    detail = e.args[0]
    cl, exc, tb = extractError()
    lastCallStack = getError(tb)[-1]
    fileName = lastCallStack[0]
    lineNum = lastCallStack[1]
    funcName = lastCallStack[2]
    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName.split(".")[0], lineNum, funcName, error_class, detail)
    del error_class, detail, cl, exc, tb, lastCallStack, fileName, lineNum, funcName
    ClearRAM()
    return errMsg

def Leave():
    Exit_Program(0)

def Get_Patch():
    try:
        print("[版本管控]", ">>", "正在檢查更新. . .")
        result = Connect_API(f"{Project_Main_URL}/Patch").json()
        Latest_Patch_Info = result.get("Patch", False)
        if Latest_Patch_Info:  
            Latest = int(Latest_Patch_Info.replace(".", ""))
            NowUse = int(PATCH.replace(".", ""))
            if Latest>NowUse:
                YesNo = messagebox.askyesno(
                    title="版本管控", message=f"發現新版本\n是否下載最新版本？ \n當前版本: {PATCH}\n最新版本: {Latest_Patch_Info}\n (使用舊版部分功能可能會出現問題"
                )
                if YesNo:
                    messagebox.showinfo(title="版本管控", message="開始下載後會出現暫時性卡頓\n(請勿關閉視窗\n(下載過程約1~2分鐘\n(按確認開始下載")
                    print("[版本管控]", ">>", "更新最新版本")
                    try:
                        Download_Url = f"{Project_Main_URL}/Download"
                        print("[版本管控]", ">>", "正在嘗試下載: ", Download_Url)
                        urlretrieve(
                            Download_Url, 
                            f"{APPLICATION_NAME}-{Latest_Patch_Info}.exe"
                        )
                        print("[版本管控]", ">>", "更新成功")
                        messagebox.showinfo(title="版本管控", message="最新版本下載完畢\n麻煩關閉輔助並開啟最新版本\n(新版本與目前版本在同一資料夾")
                        return True
                    except HTTPError:
                        print("[版本管控]", ">>", "未找到新版本檔案")
                        messagebox.showinfo(title="版本管控", message="更新失敗\n未找到新版本檔案\n(可能是尚未完全釋出")
            else:
                print("[版本管控]", ">>", "正在嘗試清除上一版本")
                files = []
                for filename in listdir(Path_Manager.dirname(Self_As_Executable)):
                    if (f"{APPLICATION_NAME}-" == filename[:len(APPLICATION_NAME)+1]) and (filename[-4:] == ".exe"):
                        files.append(
                            (
                                int("".join(filename.split("-")[1][:len(PATCH)].split("."))),
                                Path_Manager.join(Path_Manager.dirname(Self_As_Executable), filename)
                            )
                        )
                if len(files) > 1:
                    files.sort(key=lambda x:x[0])
                    for patch, path in files[:-1]:
                        print("[版本管控]", ">>", "移除舊版本檔案:", path)
                        remove(path)
                print("[版本管控]", ">>", "舊版本已被清除")
    except ConnectionError:
        print("[版本管控]", ">>", "網路連線錯誤")
    except Exception as e:
        errMsg = Get_Error(e)
        print(f"[版本管控] >> 發生未知錯誤：\n{errMsg}")
        messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[Updater] >>\n{errMsg}")
    return False

def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False
if not is_admin():
    # Re-run the program with admin rights
    windll.shell32.ShellExecuteW(None, "runas", Self_As_Executable, " ".join(Sys_argv), None, 1)
    Leave()






#Authorization
class User_Login_Info():
    attr_name   = ["account", "pp", "pt", "pb", "sens", "conf", "MovK", "GDps"]
    attr_type   = [      str,  int,  str,  str,  float,  float,    str,    int]
    zh_tw_patch = {0:"試用版", 1:"綜合版", 2:"純壓槍版", 3:"純身法版"}
    def Print(self):
        titles = [_ for _ in self.attr_name]
        values = [str(getattr(self, _)) for _ in self.attr_name]
        title_len = max([len(_) for _ in self.attr_name] + [10])
        value_len = max([len(_) for _ in values] + [25])

        result = []
        for title, value in zip(titles, values):
            result.append((title + " "*(title_len-len(title))) + (" "*(value_len-len(value)) + value) + "\n")

        print("[帳戶管控] >>")
        print("\t登入帳號：", self.account)
        print("\t輔助版本：", self.zh_tw_patch[self.pp])
        print("\t購買時間：", self.pt)
class Check_Authorize():
    BASE_URL = f"{Project_Main_URL}"

    Error_State_Representation = {
         0 : "更新伺服器登入狀態失敗",
        -1 : "此帳號已登出或在其他地方登入",
        -2 : "與伺服器連線失敗"
    }

    Credit_path = "C:\ApexGunControl_Credit.txt"

    def __init__(self):
        #Values
        self.Authorize_State = 0
        self.Logging_out = False

        #UI
        self.InputBar = Tk()
        self.InputBar.resizable(False, False)
        self.InputBar.attributes('-topmost', True)
        self.InputBar.protocol("WM_DELETE_WINDOW", Leave)
        self.InputBar.tk.call('wm', 'iconphoto', self.InputBar._w, ImageTk.PhotoImage(image=Img.open(APPLICATION_ICON)))

        self.sw, self.sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.InputBar.geometry(f"+{round((self.sw/2)-130)}+{round((self.sh/2)-13)}")
        self.InputBar.title(f"ApexGunControl {PATCH}")

        self.label1 = Label(self.InputBar, text="請輸入購買時使用的信箱")
        self.label1.grid(column=2, row=0, columnspan=5, padx=20, pady=3)

        self.label2 = Label(self.InputBar, text="[ 等待中 ]", foreground="black")
        self.label2.grid(column=2, row=1, columnspan=5, padx=20, pady=3)

        mail = ""
        if Path_Manager.exists(self.Credit_path):
            try:
                with open(self.Credit_path, "r") as cf:
                    mail = cf.read()
                mail = mail if mail else ""
            except:
                mail = ""
        self.entry1 = Entry(self.InputBar, width=25)
        self.entry1.delete(0,END)
        self.entry1.insert(0,mail)
        self.entry1.grid(column=2, row=2, columnspan=5, padx=20, pady=3)
        
        self.button = Button(self.InputBar, text="驗證", command=self.Start_Classify)
        self.button.grid(column=2, row=3, columnspan=5, padx=20, pady=3)

        self.InputBar.mainloop()

    def On_quit(self):
        self.Run = False
        self.InputBar.destroy()

    def Start_Classify(self):
        self.label2.config(text="[ 驗證中 ]", foreground="blue")
        self.InputBar.after(500, self.Login)

    def Login(self):
        self.LoginAcc = self.entry1.get().replace(" ", "").lower()
        try:
            with open(self.Credit_path, "w") as cf:
                cf.write(self.LoginAcc)
            print("[帳戶管控]", ">>", "成功儲存本次驗證帳號")
        except Exception as e:
            print("[帳戶管控]", ">>", "儲存本次驗證帳號失敗")
        try:
            print("[帳戶管控]", ">>", "驗證中. . .")
            payload = {"account":self.LoginAcc}
            result = Connect_API(self.BASE_URL+"/Auth", params=payload).json()
            State = int(result["State"])
            if State == 1:
                if Get_Patch():
                    self.Authorize_State = 0
                    self.label2.config(text="[ 下載完畢 ]", foreground="green")
                    self.button.config(text="退出", command=lambda:(self.Logout(), self.On_quit()))
                else:
                    print("[帳戶管控]", ">>", "登入驗證成功")

                    User_Info = result.get("User_Info", False)

                    self.Authorize_State = 1
                    self.label2.config(text="[ 驗證成功 ]", foreground="green")

                    for Gun_Name, Need_control in dict(User_Info.pop(0)).items():
                        Gun_Data.Gun_Dict[Gun_Name].Need_Control = int(Need_control).__bool__()

                    self.Login_Info = User_Login_Info()
                    for attr_name, attr_type, attr_value in zip(User_Login_Info.attr_name, User_Login_Info.attr_type, User_Info[:len(User_Login_Info.attr_name)]):
                        self.Login_Info.__setattr__(attr_name, attr_type(attr_value))
                    self.Login_Info.Print()

                    Thread(target=self.Stay_Login).start()
                    self.On_quit()

            elif State == 0:
                print("[帳戶管控]", ">>", "不存在的帳戶")
                self.Authorize_State = 0
                self.label2.config(text="[ 驗證失敗 ]", foreground="red")
            elif State == -1:
                print("[帳戶管控]", ">>", "重複登入或上次關閉時並未登出")
                self.Authorize_State = -1
                self.label2.config(text="[ 重複登入 ]", foreground="red")
                YesNo = messagebox.askyesno(
                    title="重複登入", message=f"已在其他地方登入！\n是否登出上個位置？"
                )
                if YesNo:
                    Logout_result = self.Logout()
                    if Logout_result == 1:
                        self.label2.config(text="[ 登出成功 ]", foreground="green")
                    elif Logout_result == 0:
                        self.label2.config(text="[ 連接網路失敗 ]", foreground="red")
                else:
                    Leave()
        except ConnectionError:
            self.label2.config(text="[ 連接網路失敗 ]", foreground="red")
            print("[帳戶管控]", ">>", "網路連線錯誤")
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[帳戶管控] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[Authorizer] >>\n{errMsg}")

    def Logout(self):
        print("[帳戶管控]", ">>", "正在嘗試登出. . . ")
        self.Logging_out = True
        self.Authorize_State = 0
        State = 0
        for i in range(10):
            try:
                payload = {"account":self.LoginAcc}
                result = Connect_API(self.BASE_URL+"/Logout", params=payload).json()
                State = int(result["State"])
                if State == 1:
                    print("[帳戶管控]", ">>", "登出成功")
                    break
                else:
                    print("[帳戶管控]", ">>", "登出失敗： 伺服器繁忙")
            except ConnectionError:
                print("[帳戶管控]", ">>", "登出失敗： 網路連線錯誤")
        return State

    def Stay_Login(self):
        delay(2)
        while(True):
            if self.Logging_out: break
            try:
                payload = {"account":self.Login_Info.account}
                result = Connect_API(self.BASE_URL+"/StayLogin", params=payload).json()
                State = int(result["State"])
                if State == 1:
                    print("[帳戶管控]", ">>", "維持登入狀態成功：", result["Input"]["User"])
                    self.Authorize_State = 1
                elif State == -1:
                    print("[帳戶管控]", ">>", "維持登入狀態失敗： 帳號從其他IP地址登入或讀取IP時發生錯誤")
                    self.Authorize_State = -1
                del result, payload
            except:
                print("[帳戶管控]", ">>", "維持登入狀態失敗： 網路連線錯誤")
                self.Authorize_State = -2
            ClearRAM()
            delay(1)
        if not self.Logging_out:
            print(f"[帳戶管控] >> 維持登入狀態時發生未知錯誤")
            messagebox.showerror(title="發生錯誤", message=f"請截圖回報給工作人員\n[SLGN] >>\nSLGN Error: SLGN Exiting")
            Leave()

    def UpdateSC(self, payload):
        try:
            result = Connect_API(f"{Project_Main_URL}/UpdateSC", params=payload).json()
            if result["User_Info"]:
                print("[帳戶管控] >>")
                print("成功儲存使用者設定")
            del result
            ClearRAM()
            return 

        except ConnectionError:
            print("[帳戶管控]", ">>", "儲存使用者設定失敗： 網路連線錯誤")


#Create cfg file
class cfg_Installer():
    def Write_cfg(cfg_path, pp, modify):
        def Get_Modify_cfg(pp, _modify, _default):
            Need_Tapping  = _modify.get("Need_Tapping" , 0)
            TapS_Movement = _modify.get("TapS_Movement", 0)
            Jump_Movement = _modify.get("Jump_Movement", 0)
            Rope_Movement = _modify.get("Rope_Movement", 0)

            ApexGunControl_cfg = ""

            if pp == 1:
                Lines = []
                Movements = []
                if Need_Tapping:
                    if Need_Tapping.get():
                        Lines.append(GunControl_cfg_Base)
                if TapS_Movement:
                    if TapS_Movement.get():
                        Movements.append("+forward")
                if Jump_Movement:
                    if Jump_Movement.get():
                        Movements.append("+jump")
                if Rope_Movement:
                    if Rope_Movement.get():
                        Movements.append("+use")
                if len(Movements) > 0:
                    Lines.append(" ".join([Movement_cfg_Base, f"\"{'; '.join(Movements)}\""]) + "\n")
                ApexGunControl_cfg = "".join(Lines)

                for idx, line in enumerate(_default):
                    if "f2" in line:
                        line = line.replace("f2", "f9")

                    elif "+toggle_zoom" in line:
                        line = line.replace("+toggle_zoom", "+zoom")

                    elif "mouse1" in line:
                        if Need_Tapping:
                            if Need_Tapping.get():
                                line = line.replace("mouse1", SHOOTKEY)

                    elif "mouse4" in line:
                        if len(Movements) > 0:
                            line = ""
                    _default[idx] = line

            elif pp == 2:
                Lines = []
                if Need_Tapping:
                    if Need_Tapping.get():
                        Lines.append(GunControl_cfg_Base)
                ApexGunControl_cfg = "".join(Lines)

                for idx, line in enumerate(_default):
                    if "f2" in line:
                        line = line.replace("f2", "f9")

                    elif "+toggle_zoom" in line:
                        line = line.replace("+toggle_zoom", "+zoom")

                    elif "mouse1" in line:
                        if Need_Tapping:
                            if Need_Tapping.get():
                                line = line.replace("mouse1", SHOOTKEY)
                    _default[idx] = line

            elif pp == 3:
                Movements = []
                if TapS_Movement:
                    if TapS_Movement.get():
                        Movements.append("+forward")
                if Jump_Movement:
                    if Jump_Movement.get():
                        Movements.append("+jump")
                if Rope_Movement:
                    if Rope_Movement.get():
                        Movements.append("+use")
                if len(Movements) > 0:
                    ApexGunControl_cfg = " ".join([Movement_cfg_Base, f"\"{'; '.join(Movements)}\""]) + "\n"

                if len(Movements) > 0:
                    for idx, line in enumerate(_default):
                        if "mouse4" in line:
                            line = ""
                    _default[idx] = line
            
            return _default, ApexGunControl_cfg

        with open(Path_Manager.join(cfg_path, "config_default_pc.cfg"), "w") as cfg_file:
            cfg_file.write(default_cfg)
        with open(Path_Manager.join(cfg_path, "config_default_pc.cfg"), "r") as cfg_file:
            Old_Default_cfg = cfg_file.readlines()

        New_Default_cfg, ApexGunControl_cfg = Get_Modify_cfg(pp, modify, Old_Default_cfg)
        with open(Path_Manager.join(cfg_path, "config_default_pc.cfg"), "w") as cfg_file:
            cfg_file.writelines(New_Default_cfg)
        with open(Path_Manager.join(cfg_path, "ApexGunControl.cfg"), "w") as cfg_file:
            cfg_file.write(ApexGunControl_cfg)


#Capture ScreenShot for GunDetection
class WindowCapture():
    # properties
    hwnd = None
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=0):
        self.get_window(window_name=window_name)
    
    def get_window(self, window_name):
        if window_name:
            self.hwnd = FindWindow(None, window_name)
        else:
            self.hwnd = 0

    def get_screenshot(self, region=None):
        if not region:
            if self.hwnd:
                info = GetWindowRect(self.hwnd)
                region = (info[0], info[1], info[2]-info[0], info[3]-info[1])
            else:
                region = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        if self.hwnd:
            if GetWindowRect(self.hwnd) == (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)):
                hwnd = 0
            else:
                hwnd = self.hwnd
        else:
            hwnd = self.hwnd

        # get the window image data
        wDC = GetWindowDC(hwnd)
        dcObj = CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, region[2], region[3])
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (region[2]+region[0], region[3]+region[1]), dcObj, (region[0], region[1]), SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (region[3], region[2], 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        ReleaseDC(hwnd, wDC)
        DeleteObject(dataBitMap.GetHandle())
        del hwnd, wDC, dcObj, cDC, dataBitMap, signedIntsArray
        ClearRAM()

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = ascontiguousarray(img)

        return img


#GunDetection using OpenCV-matchtemplate
class Detection():
    F9_data = [
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0, 255, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0, 255,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0, 255,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0, 255,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0, 255,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0, 255,   0,   0,   0, ],
        [  0,   0, 255, 255, 255,   0, 255, 255, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0, 255, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0, 255, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0, 255, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 255, 255,   0,   0,   0,   0,   0, ],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, ],
    ]
    Image_data = array(F9_data, dtype=uint8)
    del F9_data
    ClearRAM()
    def __init__(self):
        self.wwc = WindowCapture("Apex Legends")
        if self.wwc.hwnd:
            window_info = GetWindowRect(self.wwc.hwnd)
            self.offset_x, self.offset_y, self.sw, self.sh = 0, 0, window_info[2]-window_info[0], window_info[3]-window_info[1]
        else:
            self.offset_x, self.offset_y = 0, 0
            self.sw, self.sh= (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        self.scale = 1920/self.sw

    def Set_offset(self):
        self.wwc.get_window("Apex Legends")
        if self.wwc.hwnd:
            window_info = GetWindowRect(self.wwc.hwnd)
            self.offset_x, self.offset_y, self.sw, self.sh = -5, -5, window_info[2]-window_info[0], window_info[3]-window_info[1]
        else:
            self.offset_x, self.offset_y, self.sw, self.sh = 0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def Detect_Champion(self, confidence):
        try:
            self.Set_offset()
            self.scale = 1920/self.sw
            originalImage = self.wwc.get_screenshot(region=[round(_) for _ in (0, self.sh/4*3, self.sw/4, self.sh/4)])
            h, w, c = originalImage.shape
            originalImage = resize(originalImage, (round(w*self.scale), round(h*self.scale)))
            grayImage = cvtColor(originalImage, COLOR_BGR2GRAY)
            thresh, grayImg = threshold(grayImage, 140, 255, THRESH_BINARY)
            del originalImage, grayImage, h, w, c, thresh
            ClearRAM()
            try:
                result = matchTemplate(grayImg.copy(), self.Image_data, TM_CCOEFF_NORMED)
                cof = minMaxLoc(result)[1]
                if cof >= confidence:
                    return True
            except:
                pass
            return False
        except:
            return False

    def Detect_Gun(self, confidence):
        try:
            self.Set_offset()
            self.scale = 1920/self.sw
            originalImage = self.wwc.get_screenshot(region=[round(_) for _ in (self.sw/4*3, self.sh/4*3, self.sw/4, self.sh/4)])
            h, w, c = originalImage.shape
            originalImage = resize(originalImage, (round(w*self.scale), round(h*self.scale)))
            grayImage = cvtColor(originalImage, COLOR_BGR2GRAY)
            del originalImage, h, w, c
            ClearRAM()
            for name, target in Gun_Data.Gun_Dict_With_None.items():
                if name:
                    try:
                        result = matchTemplate(grayImage.copy(), target.Image, TM_CCOEFF_NORMED)

                        if minMaxLoc(result)[1] >= confidence[0]:
                            if target.Detect_Attachment:
                                Attachment_result = matchTemplate(grayImage.copy(), target.Attachment, TM_CCOEFF_NORMED)

                                if minMaxLoc(Attachment_result)[1] >= confidence[1]:
                                    return name
                            else:
                                return name
                    except:
                        pass
            return None
        except:
            return None


#User Interface
class UI():
    def __init__(self, OutPutFunction, Auth):
        global patch_template_img_byte, background_img_byte, contact_button_img_byte, float_window_button_img_byte, information_button_img_byte, choose_button_img_byte, repair_button_img_byte, settings_button_img_byte, work_template_img_byte
        self.Authorizer = Auth
        self.init(OutPutFunction=OutPutFunction)
        self.Build_Window()
        del patch_template_img_byte, background_img_byte, contact_button_img_byte, float_window_button_img_byte, information_button_img_byte, choose_button_img_byte, repair_button_img_byte, settings_button_img_byte, work_template_img_byte
        ClearRAM()



    def init(self, OutPutFunction):
        self.Busy = False
        self.Login_Info = None

        #UI Configs
        self.Float_Window = None
        self.HotKey_Window = None
        self.Working_elements = {}

        #GunControl Configs
        self.OutPutFunction = OutPutFunction
        self.GunControl_Sensitive = 8.0
        self.GunControl_Confidence = 0.8
        self.GunControl_GDps = 100
        self.Run_Application_InnerLoop = False
        self.Currently_Holding_Gun = "N\A"
        self.Choose_CheckBox_Values = []
        self.Repair_CheckBox_Values = {}
        self.Gun_Name_Len = max([len(Gun_Name) for Gun_Name in Gun_Data.Gun_Names])

        #Repair Configs
        self.Repairing = False
        self.Repairing_idx = 0

    def Build_Window(self):
        try:
            self.window = Tk()
            self.window.tk.call('wm', 'iconphoto', self.window._w, ImageTk.PhotoImage(image=Img.open(APPLICATION_ICON)))
            self.window.title(f"ApexGunControl {PATCH}")
            self.window.geometry(f"1282x939+{(user32.GetSystemMetrics(0)-1282)//2}+{(user32.GetSystemMetrics(1)-939)//2}")
            self.window.protocol("WM_DELETE_WINDOW", self.On_quit)
            self.window.configure(bg="#edf1ff")
            self.window.resizable(False, False)

            self.fontStyle = font.Font(family="Terminal", size=12)

            self.canvas = Canvas(self.window, bg="#edf1ff", height=939, width=1282, bd=0, highlightthickness=0, relief="ridge")
            self.canvas.place(x=0, y=0)

            self.background_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(background_img_byte))))
            self.background = self.canvas.create_image(641.0, 469.5, image=self.background_img)


            def Get_Coord():
                Coords = [[126, 227], [126, 283], [126, 339], [126, 394], [126, 450], [126, 505]]
                for coord in Coords:
                    yield coord
            Function_Coord_Generator = Get_Coord()

            self.float_window_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(float_window_button_img_byte))))
            self.float_window_button = Button(image=self.float_window_button_img, borderwidth=0, highlightthickness=0, command=self.Float_Window_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.float_window_button.place(x=coord[0], y=coord[1], width=290, height=35)

            self.settings_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(settings_button_img_byte))))
            self.settings_button = Button(image=self.settings_button_img, borderwidth=0, highlightthickness=0, command=self.Settings_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.settings_button.place(x=coord[0], y=coord[1], width=290, height=36)

            self.choose_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(choose_button_img_byte))))
            self.choose_button = Button(image=self.choose_button_img, borderwidth=0, highlightthickness=0, command=self.Choose_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.choose_button.place(x=coord[0], y=coord[1], width=290, height=36)

            self.repair_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(repair_button_img_byte))))
            self.repair_button = Button(image=self.repair_button_img, borderwidth=0, highlightthickness=0, command=self.Repair_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.repair_button.place(x=coord[0], y=coord[1], width=290, height=35)

            self.contact_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(contact_button_img_byte))))
            self.contact_button = Button(image=self.contact_button_img, borderwidth=0, highlightthickness=0, command=self.Contact_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.contact_button.place(x=coord[0], y=coord[1], width=290, height=36)

            self.information_button_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(information_button_img_byte))))
            self.information_button = Button(image=self.information_button_img, borderwidth=0, highlightthickness=0, command=self.Information_Button_Clicked, relief="flat")
            coord = next(Function_Coord_Generator)
            self.information_button.place(x=coord[0], y=coord[1], width=290, height=35)

            self.patch_template_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(patch_template_img_byte))))
            self.patch_template = self.canvas.create_image(138, 797, anchor=NW, image=self.patch_template_img)

            self.work_canvas_x, self.work_canvas_y = 391, 631
            self.work_canvas_width, self.work_canvas_height = 828, 235
            self.work_template_img = ImageTk.PhotoImage(image=Img.open(BytesIO(b64decode(work_template_img_byte))))
            self.work_template = self.canvas.create_image(self.work_canvas_x, self.work_canvas_y, anchor=NW, image=self.work_template_img)

            self.work_canvas = Canvas(self.window, width=self.work_canvas_width, height=self.work_canvas_height, bd=0, highlightthickness=0, relief="ridge")
            self.work_canvas.place(x=self.work_canvas_x, y=self.work_canvas_y)

            del Function_Coord_Generator, coord, Get_Coord
            ClearRAM()
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")

    def Update(self):
        self.window.mainloop()

    def On_quit(self):
        if messagebox.askyesno(title="退出", message="確認關閉輔助？"):
            def _():
                self.Authorizer.Logout()
                Leave()
            Thread(target=_).start()
            self.window.destroy()

    def Get_Busy(self):
        if self.Busy:
            return True
        elif self.Repairing:
            return "正在檢查檔案完整度 . . ."
        else:
            return False

    def Clear_Working_Element(self):
        if self.Float_Window:
            self.Float_Window.destroy()
        if self.HotKey_Window:
            self.HotKey_Window.Close()
        self.work_canvas.destroy()
        del self.Float_Window, self.HotKey_Window, self.Run_Application_InnerLoop, self.Choose_CheckBox_Values, self.Repair_CheckBox_Values, self.work_canvas, self.Working_elements
        ClearRAM()
        self.Float_Window = None
        self.HotKey_Window = None
        self.Run_Application_InnerLoop = False
        self.Choose_CheckBox_Values = []
        self.Repair_CheckBox_Values = {}
        self.Working_elements = {}
        self.work_canvas = Canvas(self.window, width=self.work_canvas_width, height=self.work_canvas_height, bd=0, highlightthickness=0, relief="ridge")
        self.work_canvas.place(x=self.work_canvas_x, y=self.work_canvas_y)

    def Center_Canvas(self):
        self.work_canvas.update()

        offset_x = (self.work_canvas_width-self.work_canvas.winfo_width())/2
        offset_y = (self.work_canvas_height-self.work_canvas.winfo_height())/2

        self.work_canvas.place(x=self.work_canvas_x+offset_x, y=self.work_canvas_y+offset_y)



    def Start_ApexGunControl(self):
        try:
            paydict = {}
            Gun_Need_Control_dict = {}
            if self.Login_Info.pp in [0, 1, 2]: #Movementonly dont need to update gun
                for Gun_Name, Gun_Class in Gun_Data.Gun_Dict.items():
                    Gun_Need_Control_dict[Gun_Name] = int(Gun_Class.Need_Control)
                paydict = { **paydict, **Gun_Need_Control_dict }

            payload = {**paydict, **{
                "account":self.Login_Info.account, 
                "S":self.GunControl_Sensitive, 
                "C":self.GunControl_Confidence, 
                "G":self.GunControl_GDps, 
                "M":self.Authorizer.Login_Info.MovK
            }}
            Thread(target=self.Authorizer.UpdateSC, args=(payload, )).start()

            self.Run_Application_InnerLoop = True

            del paydict, Gun_Need_Control_dict
            ClearRAM()

            print("[輔助系統]", ">>", "輔助啟動成功")

        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[輔助系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")
        return True



    def Float_Window_Button_Clicked(self):
        try:
            is_Busy = self.Get_Busy()
            if not is_Busy:
                self.Busy = True
                self.Clear_Working_Element()
                if self.Start_ApexGunControl():
                    if self.Login_Info.pp in [0, 1, 2]: #Only TryUse&ApexGunControl&GunControlOnly needs to show Sens&Conf UI
                        #Clear previous canvas
                        self.Float_Window = Toplevel(self.window)
                        self.Float_Window.geometry("+-5+0")
                        self.Float_Window.attributes('-topmost', True)
                        self.Float_Window.tk.call('wm', 'iconphoto', self.Float_Window._w, ImageTk.PhotoImage(image=Img.open(APPLICATION_ICON)))
                        self.Float_Window.protocol("WM_DELETE_WINDOW", self.Float_Window_On_quit)
                        self.Float_Window.title(f"ApexGunControl {PATCH} - Float")
                        self.Float_Window.resizable(False, False)
                        self.work_canvas.grid_columnconfigure(0, weight=10, uniform="fred")
                        self.work_canvas.grid_columnconfigure(1, weight=10, uniform="fred")

                        Float_Window_Sensitive_Label = Label(self.Float_Window, text="遊戲壓槍靈敏度： ", foreground="black")
                        Float_Window_Sensitive_Label.grid(column=0, row=1, padx=10, pady=2)
                        Float_Window_Sensitive_Value = Label(self.Float_Window, text=f"{self.GunControl_Sensitive}", foreground="black")
                        Float_Window_Sensitive_Value.grid(column=1, row=1, padx=10, pady=2)

                        Float_Window_Confidence_Label = Label(self.Float_Window, text="槍枝偵測靈敏度： ", foreground="black")
                        Float_Window_Confidence_Label.grid(column=0, row=2, padx=10, pady=2)
                        Float_Window_Confidence_Value = Label(self.Float_Window, text=f"{self.GunControl_Confidence}", foreground="black")
                        Float_Window_Confidence_Value.grid(column=1, row=2, padx=10, pady=2)

                        Float_Window_GDps_Label = Label(self.Float_Window, text="每秒偵測槍次數： ", foreground="black")
                        Float_Window_GDps_Label.grid(column=0, row=3, padx=10, pady=2)
                        Float_Window_GDps_Value = Label(self.Float_Window, text=f"{self.GunControl_GDps}", foreground="black")
                        Float_Window_GDps_Value.grid(column=1, row=3, padx=10, pady=2)

                        Currently_Holding_Gun_Label = Label(self.Float_Window, text=f"手持槍枝： ", foreground="black")
                        Currently_Holding_Gun_Label.grid(column=0, row=4, padx=10, pady=2)
                        Currently_Holding_Gun_Value = Label(self.Float_Window, text=f"{self.Currently_Holding_Gun}", foreground="red")
                        Currently_Holding_Gun_Value.grid(column=1, row=4, padx=10, pady=2)

                        self.Float_Window.after(int(5000/self.GunControl_GDps), self.Float_Window_Update)

                        self.Working_elements = {
                            "Currently_Holding_Gun_Value":Currently_Holding_Gun_Value,
                            "Float_Window":self.Float_Window
                        }
                        del Float_Window_Sensitive_Label, Float_Window_Sensitive_Value, Float_Window_Confidence_Label, Float_Window_Confidence_Value, Float_Window_GDps_Label, Float_Window_GDps_Value, Currently_Holding_Gun_Label,
                        ClearRAM()

                    else: #MovementOnly UI
                        #Clear previous canvas
                        self.Float_Window = Toplevel(self.window)
                        self.Float_Window.geometry("+-5+0")
                        self.Float_Window.attributes('-topmost', True)
                        self.Float_Window.tk.call('wm', 'iconphoto', self.Float_Window._w, ImageTk.PhotoImage(image=Img.open(APPLICATION_ICON)))
                        self.Float_Window.protocol("WM_DELETE_WINDOW", self.Float_Window_On_quit)
                        self.Float_Window.title(f"ApexGunControl {PATCH} - Float")
                        self.Float_Window.resizable(False, False)

                        MovementOnly_Label = Label(self.Float_Window, text="身法輔助運行中. . .", foreground="black")
                        MovementOnly_Label.grid(column=0, row=0, padx=10, pady=5)

                        self.Float_Window.update()

                        self.Working_elements = {
                            "Float_Window":self.Float_Window
                        }
                        del MovementOnly_Label
                        ClearRAM()
                self.Busy = False
            else:
                if type(is_Busy) == str:
                    messagebox.showerror(message=is_Busy)
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")

    def Float_Window_Update(self):
        if self.Float_Window:
            self.Working_elements[
                "Currently_Holding_Gun_Value"
            ].config(
                text=self.Currently_Holding_Gun.center(self.Gun_Name_Len), 
                fg="red" if self.Currently_Holding_Gun == "N\A" else "green"
            )
            self.Float_Window.after(int(5000/self.GunControl_GDps), self.Float_Window_Update)

    def Float_Window_On_quit(self):
        if self.Float_Window:
            self.Float_Window.destroy()
            self.Run_Application_InnerLoop = False



    def Settings_Button_Clicked(self):
        try:
            is_Busy = self.Get_Busy()
            if not is_Busy:
                self.Busy = True
                #Clear previous canvas
                self.Clear_Working_Element()
                print("[介面系統]", ">>", "前往設定介面")
                self.Working_elements = {}

                if self.Login_Info.pp not in [3, ]: #MovementOnly dont need guncontrol settings
                    #Sens Label 
                    sensitive_label = Label(self.work_canvas, text="輔助壓槍靈敏度： ", font=self.fontStyle, foreground="black")
                    sensitive_label.grid(column=0, row=0, padx=10, pady=10)
                    #Sens Slider 1
                    sensitive_slider = Scale(self.work_canvas, variable=StringVar(), from_=0.2, to=20, length=500, digits=3, resolution=0.1, orient=HORIZONTAL, command=self.Settings_Update)
                    sensitive_slider.set(self.GunControl_Sensitive)
                    sensitive_slider.grid(column=1, row=0, columnspan=2)

                    #Confidence Label
                    confidence_label = Label(self.work_canvas, text="槍枝偵測靈敏度： ", font=self.fontStyle, foreground="black")
                    confidence_label.grid(column=0, row=1, padx=10, pady=10)
                    #Confidence Slider 1
                    confidence_slider = Scale(self.work_canvas, variable=StringVar(), from_=0.5, to=1, length=500, digits=3, resolution=0.01, orient=HORIZONTAL, command=self.Settings_Update)
                    confidence_slider.set(self.GunControl_Confidence)
                    confidence_slider.grid(column=1, row=1, columnspan=2)

                    #GDps Label
                    gdps_label = Label(self.work_canvas, text="每秒偵測槍次數： ", font=self.fontStyle, foreground="black")
                    gdps_label.grid(column=0, row=2, padx=10, pady=10)
                    #GDps Slider 1
                    gdps_slider = Scale(self.work_canvas, variable=StringVar(), from_=1, to=100, length=500, digits=3, resolution=1, orient=HORIZONTAL, command=self.Settings_Update)
                    gdps_slider.set(self.GunControl_GDps)
                    gdps_slider.grid(column=1, row=2, columnspan=2)

                    self.Working_elements = {**self.Working_elements, **{
                        "sensitive_slider":sensitive_slider,
                        "confidence_slider":confidence_slider,
                        "gdps_slider":gdps_slider,
                    }}
                    del sensitive_label, confidence_label, gdps_label
                    ClearRAM()
                
                if self.Login_Info.pp not in [0, 2]: #TryUse&GunControl dont need movement settings
                    movement_kb_label = Label(self.work_canvas, text="身法輔助啟動鍵： ", font=self.fontStyle, foreground="black")
                    movement_kb_label.grid(column=0, row=3, padx=10, pady=10)
                    movement_kb_now = Label(self.work_canvas, text=Code2KeyName.get(self.Authorizer.Login_Info.MovK, "M4"), font=font.Font(family="Arial", size=16), foreground="black")
                    movement_kb_now.grid(column=1, row=3, padx=10, pady=10)
                    movement_kb_button = Button(self.work_canvas, text="重新選擇身法輔助熱鍵", command=self.Settings_Choose_MovK)
                    movement_kb_button.grid(column=2, row=3, padx=10, pady=10)

                    self.Working_elements = {**self.Working_elements, **{
                        "movement_kb_label":movement_kb_label,
                        "movement_kb_now":movement_kb_now,
                        "movement_kb_button":movement_kb_button
                    }}
                    del movement_kb_label
                    ClearRAM()

                self.Center_Canvas()

                self.Busy = False
            else:
                if type(is_Busy) == str:
                    messagebox.showerror(message=is_Busy)
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")
    
    def Settings_Choose_MovK(self):
        def _return_func(key_name):
            self.Authorizer.Login_Info.MovK = KeyName2Code[key_name.upper()]
            self.Working_elements["movement_kb_now"].config(text=key_name)
        if self.HotKey_Window:
            self.HotKey_Window.Close()
            self.HotKey_Window = None
        self.HotKey_Window = VirtualKB(main_window=self.window, default=Code2KeyName.get(self.Authorizer.Login_Info.MovK, "M4"), return_func=_return_func)
        self.work_canvas.after(0, self.HotKey_Window.Update)

    def Settings_Update(self, evt):
        sensitive_slider = self.Working_elements.get("sensitive_slider", None)
        confidence_slider = self.Working_elements.get("confidence_slider", None)
        gdps_slider = self.Working_elements.get("gdps_slider", None)

        if sensitive_slider: self.GunControl_Sensitive = float(sensitive_slider.get())
        if confidence_slider: self.GunControl_Confidence = float(confidence_slider.get())
        if gdps_slider: self.GunControl_GDps = int(gdps_slider.get())

        self.OutPutFunction(sens=self.GunControl_Sensitive, confidence=self.GunControl_Confidence, gdps=self.GunControl_GDps)



    def Choose_Button_Clicked(self):
        try:
            No_Permission_pp = [0, 3] #TryUse cant choose GunNeedControl / MovementOnly dont need to choose GunNeedControl
            if self.Login_Info.pp not in No_Permission_pp:
                is_Busy = self.Get_Busy()
                if not is_Busy:
                    self.Busy = True
                    #Clear previous canvas
                    self.Clear_Working_Element()
                    print("[介面系統]", ">>", "前往槍枝選擇")

                    ttk.Separator(self.work_canvas, orient=HORIZONTAL).grid(column=0, row=0, columnspan=5000, sticky='ew')
                    ttk.Separator(self.work_canvas, orient=VERTICAL).grid(column=0, row=0, rowspan=5000, sticky='ns')
                    
                    total_Column, total_Row = 5, 7
                    Column, Row = 1, 1
                    Choosing_Guns = Gun_Data.Gun_Dict.copy()
                    del Choosing_Guns["Turbo_HAVOC"]
                    del Choosing_Guns["Turbo_Devotion"]
                    Gun_Names = list(Choosing_Guns.keys())
                    Gun_Classes = list(Choosing_Guns.values())
                    for i in range(total_Column):
                        self.work_canvas.grid_columnconfigure(Column, weight=25, uniform="fred")
                        for j in range(total_Row):
                            if total_Row*i + j < len(Gun_Names):
                                self.Working_elements[
                                    total_Row*i + j
                                ] = self.Choose_CheckBox(
                                    n=Gun_Names[total_Row*i + j],
                                    c=Column,
                                    r=Row,
                                    v=Gun_Classes[total_Row*i + j].Need_Control
                                )
                            else:
                                ttk.Separator(self.work_canvas, orient=HORIZONTAL).grid(column=Column, row=Row+1, columnspan=5000, sticky='ew')
                                ttk.Separator(self.work_canvas, orient=VERTICAL).grid(column=Column+2, row=Row, rowspan=5000, sticky='ns')
                            Row+=2
                        Column+=3
                        Row=1
                    self.Center_Canvas()
                    del total_Column, total_Row, Column, Row, Choosing_Guns, Gun_Classes, Gun_Names
                    ClearRAM()
                    self.Busy = False
                else:
                    if type(is_Busy) == str:
                        messagebox.showerror(message=is_Busy)
            else:
                messagebox.showwarning(title="權限錯誤", message=f"{User_Login_Info.zh_tw_patch[self.Login_Info.pp]}不包含此功能")
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")

    def Choose_CheckBox(self, n, c, r, v):
        Label(self.work_canvas, text=n).grid(column=c, row=r)
        v1 = IntVar(value=v)
        v1.__setattr__("GunName", n)
        Checkbutton(self.work_canvas, variable=v1, onvalue=1, offvalue=0, command=self.Choose_Update).grid(column=c+1, row=r)
        self.Choose_CheckBox_Values.append(v1)
        ttk.Separator(self.work_canvas, orient=HORIZONTAL).grid(column=c, row=r+1, columnspan=5000, sticky='ew')
        ttk.Separator(self.work_canvas, orient=VERTICAL).grid(column=c+2, row=r, rowspan=5000, sticky='ns')

    def Choose_Update(self):
        for value in self.Choose_CheckBox_Values:
            Gun_Data.Gun_Dict[value.GunName].Need_Control = value.get()

            if value.GunName == "HAVOC":
                Gun_Data.Gun_Dict["Turbo_HAVOC"].Need_Control = value.get()

            elif value.GunName == "Devotion":
                Gun_Data.Gun_Dict["Turbo_Devotion"].Need_Control = value.get()



    def Repair_Button_Clicked(self):
        try:
            No_Permission_pp = [0, ] #TryUse cant install cfg
            if self.Login_Info.pp not in No_Permission_pp:
                is_Busy = self.Get_Busy()
                if not is_Busy:
                    self.Busy = True
                    #Clear previous canvas
                    self.Clear_Working_Element()
                    print("[介面系統]", ">>", "前往修復介面")

                    cfg_path_label = Label(self.work_canvas, text="Apex cfg資料夾路徑： ")
                    cfg_path_label.grid(column=0, row=0, columnspan=2, padx=10, pady=14)
                    cfg_path_inputbar = Entry(self.work_canvas, width=50)
                    cfg_path_inputbar.grid(column=2, row=0, columnspan=3, padx=10, pady=14)
                    cfg_path_button = Button(self.work_canvas, text="開啟", command=self.Repair_Get_Path)
                    cfg_path_button.grid(column=5, row=0, padx=10, pady=14)


                    Choose_cfg_label = Label(self.work_canvas, text="參數選項： ")
                    Choose_cfg_label.grid(column=0, row=1, rowspan=2, padx=3, pady=10)
                    Permission_to_Choose_TappingGun_cfg = [1, 2] #ApexGunControl & GunControlOnly
                    if self.Login_Info.pp in Permission_to_Choose_TappingGun_cfg:
                        Choose_GunControl_cfg_label = Label(self.work_canvas, text=(" "*10) + "壓槍輔助： " + (" "*10))
                        Choose_GunControl_cfg_label.grid(column=1, row=1, padx=3, pady=2)

                        Need_Tapping = IntVar(value=1)
                        Checkbutton(self.work_canvas, text="單點槍自動連點", variable=Need_Tapping, onvalue=1, offvalue=0).grid(column=3, row=1)
                        self.Repair_CheckBox_Values["Need_Tapping"] = Need_Tapping


                    Permission_to_Choose_Movement_cfg = [1, 3] #ApexGunControl & MovementOnly
                    if self.Login_Info.pp in Permission_to_Choose_Movement_cfg:
                        Choose_Movement_cfg_label = Label(self.work_canvas, text=(" "*10) + "身法輔助： " + (" "*10))
                        Choose_Movement_cfg_label.grid(column=1, row=2, padx=3, pady=2)

                        TapS_Movement= IntVar(value=1)
                        self.Repair_CheckBox_Values["TapS_Movement"] = TapS_Movement
                        Checkbutton(self.work_canvas, text="ＴＳ身法", variable=TapS_Movement, onvalue=1, offvalue=0).grid(column=2, row=2)

                        Jump_Movement = IntVar(value=1)
                        self.Repair_CheckBox_Values["Jump_Movement"] = Jump_Movement
                        Checkbutton(self.work_canvas, text="跳躍身法", variable=Jump_Movement, onvalue=1, offvalue=0).grid(column=3, row=2)

                        Rope_Movement = IntVar(value=1)
                        self.Repair_CheckBox_Values["Rope_Movement"] = Rope_Movement
                        Checkbutton(self.work_canvas, text="繩索身法", variable=Rope_Movement, onvalue=1, offvalue=0).grid(column=4, row=2)


                    state_show_label = Label(self.work_canvas, text="修復狀態： ")
                    state_show_label.grid(column=0, row=3, padx=3, pady=14)
                    state_show_state = Label(self.work_canvas, text="[ 等待中 ]")
                    state_show_state.grid(column=1, row=3, padx=10, pady=14)
                    state_processbar = ttk.Progressbar(self.work_canvas, orient='horizontal', mode='determinate', length=400)
                    state_processbar.grid(column=2, row=3, columnspan=3, padx=10, pady=14)

                    state_result_label = Label(self.work_canvas, text="修復結果： ")
                    state_result_label.grid(column=0, row=4, padx=3, pady=14)
                    state_show_result = Label(self.work_canvas, text="[ 等待中 ]")
                    state_show_result.grid(column=1, row=4, padx=10, pady=14)
                    start_repair_button = Button(self.work_canvas, text="檢查並重新安裝cfg檔", command=self.Repair_Start)
                    start_repair_button.grid(column=2, row=4, columnspan=3, padx=10, pady=14)

                    self.Center_Canvas()

                    self.Working_elements = {
                        "cfg_path_label":cfg_path_label,
                        "cfg_path_inputbar":cfg_path_inputbar,
                        "cfg_path_button":cfg_path_button,
                        "state_show_label":state_show_label,
                        "state_show_state":state_show_state,
                        "state_processbar":state_processbar,
                        "state_result_label":state_result_label,
                        "state_show_result":state_show_result,
                        "start_repair_button":start_repair_button
                    }
                    self.Busy = False
                else:
                    if type(is_Busy) == str:
                        messagebox.showerror(message=is_Busy)
            else:
                messagebox.showwarning(title="權限錯誤", message=f"{User_Login_Info.zh_tw_patch[self.Login_Info.pp]}不包含此功能")
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")

    def Repair_Get_Path(self):
        path = filedialog.askdirectory()
        if path:
            self.Working_elements["cfg_path_inputbar"].delete(0, END)
            self.Working_elements["cfg_path_inputbar"].insert(0, path)

    def Repair_Start(self):
        self.Repairing = True
        self.Working_elements["state_processbar"]["value"] = 0
        self.Working_elements["state_show_state"].config(text="[ 檢查中 ]", fg="black")
        self.Working_elements["state_show_result"].config(text="[ 等待中 ]", fg="black")
        path = self.Working_elements["cfg_path_inputbar"].get()
        if Path_Manager.exists(path):
            files = listdir(path)
            if "config_default_pc.cfg" in files and "video_settings_changed_quit.cfg" in files:
                cfg_Installer.Write_cfg(path, self.Login_Info.pp, self.Repair_CheckBox_Values)
                self.Working_elements["state_show_state"].config(
                    text="[ cfg安裝完畢 ]", fg="green"
                )
                self.Working_elements["state_processbar"]["value"] += 100/len(Gun_Data.Gun_Names)
                self.work_canvas.after(500, self.Repair_GetPatch)
            else:
                self.Working_elements["state_show_result"].config(
                    text="[ 錯誤路徑 ]", fg="red"
                )
        else:
            self.Working_elements["state_show_result"].config(
                text="[ 無效路徑 ]", fg="red"
            )

    def Repair_Gun(self):
        Guns = Gun_Data.Gun_Names
        if self.Repairing_idx < len(Guns):
            self.Working_elements["state_show_state"].config(
                text=f"[ {Guns[self.Repairing_idx]} ]", fg="green"
            )
            self.Repairing_idx += 1
            self.Working_elements["state_processbar"]["value"] += 100/len(Gun_Data.Gun_Names)
            self.work_canvas.after(200, self.Repair_Gun)
        else:
            self.work_canvas.after(200, self.Repair_End)

    def Repair_GetPatch(self):
        self.Working_elements["state_show_state"].config(text="[ 檢查版本 ]", fg="green")
        Get_Patch()
        if self.Login_Info.pp in [0, 1, 2]:
            self.work_canvas.after(200, self.Repair_Gun)
        else:
            self.work_canvas.after(200, self.Repair_End)

    def Repair_End(self):
        self.Repairing = False
        self.Repairing_idx = 0
        self.Working_elements["state_processbar"]["value"] = 100
        self.Working_elements["state_show_state"].config(text="[ 檢查完畢 ]", fg="green")
        self.Working_elements["state_show_result"].config(text="[ 檢查完畢 ]", fg="green")



    def Contact_Button_Clicked(self):
        try:
            No_Permission_pp = [0, ] #TryUse cant use contact function
            if self.Login_Info.pp not in No_Permission_pp:
                if not self.Get_Busy():
                    self.Busy = False
                    print("[介面系統]", ">>", "前往取得聯繫")
                    OpenBrowser(Project_Main_URL)
                    self.Busy = False
            else:
                messagebox.showwarning(title="權限錯誤", message=f"{User_Login_Info.zh_tw_patch[self.Login_Info.pp]}不包含此功能")
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")



    def Information_Button_Clicked(self):
        try:
            is_Busy = self.Get_Busy()
            if not is_Busy:
                self.Busy = True
                #Clear previous canvas
                self.Clear_Working_Element()
                print("[介面系統]", ">>", "前往輔助資訊")

                #values
                Login_account = self.Login_Info.account
                Purchase_Time = self.Login_Info.pt

                #Styling
                Information_font = font.Font(family="Terminal", size=16)

                #Login account
                account_label = Label(self.work_canvas, text="當前登入帳號： ", font=Information_font, foreground="black")
                account_label.grid(column=0, row=0, padx=10, pady=10)
                account_value = Label(self.work_canvas, text=f"{Login_account}", font=Information_font, foreground="black")
                account_value.grid(column=1, row=0, padx=10, pady=10)
                #Purchase time
                purchase_label = Label(self.work_canvas, text="輔助購買時間： ", font=Information_font, foreground="black")
                purchase_label.grid(column=0, row=1, padx=10, pady=10)
                purchase_value = Label(self.work_canvas, text=f"{Purchase_Time}", font=Information_font, foreground="black")
                purchase_value.grid(column=1, row=1, padx=10, pady=10)
                #Purchase time
                patch_label = Label(self.work_canvas, text="當前輔助版本： ", font=Information_font, foreground="black")
                patch_label.grid(column=0, row=3, padx=10, pady=10)
                patch_value = Label(self.work_canvas, text=f"{PATCH} {User_Login_Info.zh_tw_patch[self.Login_Info.pp]}", font=Information_font, foreground="black")
                patch_value.grid(column=1, row=3, padx=10, pady=10)

                self.Center_Canvas()
                
                self.Working_elements = {
                    "account_label":account_label,
                    "account_value":account_value,
                    "purchase_label":purchase_label,
                    "purchase_value":purchase_value,
                    "patch_label":patch_label,
                    "patch_value":patch_value
                }
                self.Busy = False
            else:
                if type(is_Busy) == str:
                    messagebox.showerror(message=is_Busy)
        except Exception as e:
            errMsg = Get_Error(e)
            print(f"[介面系統] >> 發生未知錯誤\n{errMsg}")
            messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[UserInterface] >>\n{errMsg}")


#Main Application
class Application():
    def __init__(self, Login_Info):
        # initlizing
        self.Login_Info = Login_Info
        self.sens = Login_Info.sens if Login_Info.sens >= 0.2 else 0.2
        self.confidence = Login_Info.conf if Login_Info.conf >= 0.5 else 0.5
        self.gdps = Login_Info.GDps if 100 >= Login_Info.GDps > 0 else 100
        self.Can_Shoot = False
        self.idx = 0
        self.modifier = 8/self.sens
        self.Holding = Gun_Data.Gun_Dict_With_None[None]
        self.Looping_Function = self.Default_Looping_Function
        self.UnDetected_Champion_Count = 0

    def BindAuth(self, Auth):
        self.Authorizer = Auth

    def BindUI(self, UI):
        self.UI = UI
        self.UI.Login_Info = self.Login_Info
        self.UI.GunControl_Sensitive  = self.sens
        self.UI.GunControl_Confidence = self.confidence
        self.UI.GunControl_GDps = self.gdps

    def reset(self, sens, confidence, gdps):
        self.idx = 0
        self.sens = sens
        self.confidence = confidence
        self.gdps = gdps
        self.modifier = 8/self.sens
        self.Holding = Gun_Data.Gun_Dict_With_None[None]

    def Background_Loop_Function(self):
        See_Champion = result = None
        while(self.UI.Run_Application_InnerLoop):
            try:
                delay(0.25/self.gdps)
                See_Champion = Detecter.Detect_Champion(confidence=(self.confidence/8)*7)
                if See_Champion:
                    self.UnDetected_Champion_Count = 0
                elif self.UnDetected_Champion_Count < 5:
                    self.UnDetected_Champion_Count += 1
                if not HandleKeyPress["M1"]() and self.UnDetected_Champion_Count < 5:
                    result = Detecter.Detect_Gun(confidence=(self.confidence, (self.confidence/16)*15))
                    self.Holding = Gun_Data.Gun_Dict.get(result, Gun_Data.Gun_Dict_With_None[None])
                    if self.Holding.name != "N\A" and self.Holding.name != self.UI.Currently_Holding_Gun:
                        print("[偵測系統]", ">>", "偵測到槍枝：", self.Holding.name)
                    self.UI.Currently_Holding_Gun = self.Holding.name
            except Exception as e:
                errMsg = Get_Error(e)
                print(f"[偵測系統] >> 發生未知錯誤\n{errMsg}")
                messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[BackgroundLoop] >>\n{errMsg}")
        del See_Champion, result
        ClearRAM()
        return

    def Looping_Control_Function(self):
        delay_time = self.Holding.Shake_gap
        if HandleKeyPress["M1"]():
            if self.Holding.Clicking and self.Login_Info.pp != 0: #TryUse does not support tapping guns
                pydirectinput.keyDown(SHOOTKEY , _pause=False)
                delay(delay_time)
                pydirectinput.keyUp(SHOOTKEY , _pause=False)
            else:
                pydirectinput.keyDown(SHOOTKEY , _pause=False)

            control = HandleKeyPress["M2"]() and self.Holding.Need_Control
            params = ( #UP / DOWN / LEFT / RIGHT / GAP
                -round( ( (self.Holding.Up   [self.idx] if len(self.Holding.Up   )>self.idx else self.Holding.Up   [-1]) +1) *self.modifier *self.Holding.Shaking_rate) * control,
                -round( ( (self.Holding.Left [self.idx] if len(self.Holding.Left )>self.idx else self.Holding.Left [-1]) +1) *self.modifier *self.Holding.Shaking_rate) * control,
                round( ( (self.Holding.Down [self.idx] if len(self.Holding.Down )>self.idx else self.Holding.Down [-1]) +1) *self.modifier *self.Holding.Shaking_rate ) * control,
                round( ( (self.Holding.Right[self.idx] if len(self.Holding.Right)>self.idx else self.Holding.Right[-1]) +1) *self.modifier *self.Holding.Shaking_rate ) * control,
            )
            win32api.mouse_event(MOUSEEVENTF_MOVE, 0, params[0], 0, 0)
            delay(delay_time)
            win32api.mouse_event(MOUSEEVENTF_MOVE, params[1], 0, 0, 0)
            delay(delay_time)
            win32api.mouse_event(MOUSEEVENTF_MOVE, 0, params[2], 0, 0)
            delay(delay_time)
            win32api.mouse_event(MOUSEEVENTF_MOVE, params[3], 0, 0, 0)
            delay(delay_time)

            if self.idx+1 < self.Holding.length:
                self.idx += 1

        else:
            self.Looping_Function = self.Default_Looping_Function
            pydirectinput.keyUp(SHOOTKEY , _pause=False)
            self.idx = 0

    def Default_Looping_Function(self):
        if self.UnDetected_Champion_Count < 5:
            if not HandleKeyPress["M1"]():
                self.Can_Shoot = True
            if HandleKeyPress["M1"]() and self.Can_Shoot:
                pydirectinput.keyDown(SHOOTKEY , _pause=False)
                self.Looping_Function = self.Looping_Control_Function
        else:
            self.Can_Shoot = False

    def Run(self):
        while(self.Authorizer.Authorize_State > 0):
            if self.UI.Run_Application_InnerLoop:
                Thread(target=self.Background_Loop_Function).start()
                while(self.UI.Run_Application_InnerLoop):
                    try:
                        if self.Login_Info.pp in [0, 1, 2]: #TryUse & ApexGunControl & GunControlOnly can use GunControl Loop
                            self.Looping_Function()

                        if HandleKeyPress[self.Authorizer.Login_Info.MovK]() and self.Login_Info.pp in [1, 3]: #ApexGunControl & MovementOnly can use Movement Loop
                            pydirectinput.keyDown(MOVEMENTKEY, _pause=False)
                            delay(0.005)
                            pydirectinput.keyUp(MOVEMENTKEY, _pause=False)
                            delay(0.005)

                    except Exception as e:
                        errMsg = Get_Error(e)
                        print(f"[主體系統] >> 發生未知錯誤\n{errMsg}")
                        messagebox.showerror(title="未知錯誤", message=f"請截圖回報給工作人員\n[MainInner] >>\n{errMsg}")
            delay(0.5)
        else:
            if not self.Authorizer.Logging_out:
                messagebox.showerror(title="發生錯誤", message=self.Authorizer.Error_State_Representation[self.Authorizer.Authorize_State])
                Leave()




if __name__ == "__main__":
    Authorizer = Check_Authorize()
    if Authorizer.Authorize_State:
        Detecter = Detection()

        App = Application(Login_Info=Authorizer.Login_Info)

        AppUI = UI(OutPutFunction=App.reset, Auth=Authorizer)

        App.BindAuth(Auth=Authorizer)
        App.BindUI(UI=AppUI)

        Thread(target=App.Run).start()

        AppUI.Update()
    else:
        Leave()
