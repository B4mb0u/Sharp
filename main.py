version = "1.0"

import win32api, win32con, win32gui, win32process, psutil, time, threading, random, winsound, os, json, subprocess, sys, asyncio, itertools, pyMeow, base64, re
import dearpygui.dearpygui as dpg
from pypresence import Presence

class configListener(dict): # Detecting changes to config
    def __init__(self, initialDict):
        for k, v in initialDict.items():
            if isinstance(v, dict):
                initialDict[k] = configListener(v)

        super().__init__(initialDict)

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            _value = configListener(value)
        else:
            _value = value

        super().__setitem__(item, _value)

        # try:
        #     sharpClass
        # except:
        #     while True:
        #         try:
        #             sharpClass

        #             break
        #         except:
        #             pass

        if sharpClass.config["misc"]["saveSettings"]:
            json.dump(sharpClass.config, open(f"{os.environ['LOCALAPPDATA']}\\temp\\{hwid}", "w", encoding="utf-8"), indent=4)

class sharp():
    def __init__(self, hwid: str):
        self.config = {
            "left": {
                "enabled": False,
                "mode": "Hold",
                "bind": 0,
                "averageCPS": 12,
                "onlyWhenFocused": True,
                "breakBlocks": False,
                "RMBLock": False,
                "blockHit": False,
                "blockHitChance": 25,
                "shakeEffect": False,
                "shakeEffectForce": 5,
                "soundPath": "",
                "workInMenus": False,
                "blatant": False,
            },
            "right": {
                "enabled": False,
                "mode": "Hold",
                "bind": 0,
                "averageCPS": 12,
                "onlyWhenFocused": True,
                "LMBLock": False,
                "shakeEffect": False,
                "shakeEffectForce": False,
                "soundPath": "",
                "workInMenus": False,
                "blatant": False
            },
            "recorder": {
                "enabled": False,
                "record": [0.08] # Default 12 CPS
            },
            "misc": {
                "overlay": False,
                "saveSettings": True,
                "guiHidden": False,
                "bindHideGUI": 0,
                "discordRichPresence": True
            }     
        }

        if os.path.isfile(f"{os.environ['LOCALAPPDATA']}\\temp\\{hwid}"):
            try:
                config = json.loads(open(f"{os.environ['LOCALAPPDATA']}\\temp\\{hwid}", encoding="utf-8").read())

                isConfigOk = True
                for key in self.config:
                    if not key in config or len(self.config[key]) != len(config[key]):
                        isConfigOk = False

                        break

                if isConfigOk:
                    if not config["misc"]["saveSettings"]:
                        self.config["misc"]["saveSettings"] = False
                    else:
                        self.config = config
            except:
                pass

        self.config = configListener(self.config)

        self.record = itertools.cycle(self.config["recorder"]["record"])

        self.lParam = win32api.MAKELONG(0, 0)

        threading.Thread(target=self.discordRichPresence, daemon=True).start()
        
        threading.Thread(target=self.windowListener, daemon=True).start()
        threading.Thread(target=self.leftBindListener, daemon=True).start()
        threading.Thread(target=self.rightBindListener, daemon=True).start()
        threading.Thread(target=self.hideGUIBindListener, daemon=True).start()

        threading.Thread(target=self.leftClicker, daemon=True).start()
        threading.Thread(target=self.rightClicker, daemon=True).start()

    def discordRichPresence(self):
        asyncio.set_event_loop(asyncio.new_event_loop())

        discordRPC = Presence("1044302531272126534")
        discordRPC.connect()

        startTime = time.time()

        states = [
            "Not cheating unless you get caught ;)",
            "The #1 Minecraft AutoClicker by Bambou"
        ]

        while True:
            if self.config["misc"]["discordRichPresence"]:
                discordRPC.update(state=random.choice(states), start=startTime, large_image="logo", large_text="#1 Minecraft AutoClicker", buttons=[{"label": "Website", "url": "https://github.com/B4mb0u/Sharp"}])
            else:
                discordRPC.clear()

            time.sleep(15)

    def windowListener(self):
        while True:
            currentWindow = win32gui.GetForegroundWindow()
            self.realTitle = win32gui.GetWindowText(currentWindow)
            self.title = win32gui.FindWindow(None, self.realTitle)

            try:
                self.focusedProcess = psutil.Process(win32process.GetWindowThreadProcessId(currentWindow)[-1]).name()
            except:
                self.focusedProcess = ""

            time.sleep(0.5)

    def overlay(self):
        pyMeow.overlay_init(title="Sharp - Overlay")

        image = base64.b64decode(re.sub("data:image/png;base64", "", "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"))

        logo = pyMeow.load_texture_bytes(".png", image)

        try: # Trash way of checking if config, focusedProcess and realTitle are initialized
            self.focusedProcess
            self.realTitle
            self.config
        except:
            while True:
                try:
                    self.focusedProcess
                    self.realTitle
                    self.config

                    break
                except:
                    pass

        while pyMeow.overlay_loop():
            if not self.config["misc"]["overlay"]:
                pyMeow.overlay_close()

                continue

            if not "java" in self.focusedProcess and not "AZ-Launcher" in self.focusedProcess:
                pyMeow.end_drawing()

                time.sleep(0.5)

                continue

            try: # so it doesn't crash when Minecraft closed
                rect = pyMeow.get_window_info(self.realTitle)
            except:
                time.sleep(0.5)

                continue                

            pyMeow.begin_drawing()

            pyMeow.draw_texture(logo, rect[0]+2, rect[1]+2, pyMeow.get_color("white"), 0, 0.10)

            # Modules
            pyMeow.draw_text(f"Left", rect[0]+60, rect[1]+12.1, 15, pyMeow.get_color("orange"))
            pyMeow.draw_text(f"Right", rect[0]+60, rect[1]+27, 15, pyMeow.get_color("orange"))

            # Modules Status
            pyMeow.draw_text(f"[Enabled]" if self.config["left"]["enabled"] else "[Disabled]", rect[0]+100, rect[1]+12.1, 15, pyMeow.get_color("green") if self.config["left"]["enabled"] else pyMeow.get_color("red"))
            pyMeow.draw_text(f"[Enabled]" if self.config["right"]["enabled"] else "[Disabled]", rect[0]+100, rect[1]+27, 15, pyMeow.get_color("green") if self.config["right"]["enabled"] else pyMeow.get_color("red"))

            pyMeow.end_drawing()

            time.sleep(0.5)

    def leftClicker(self):
        while True:
            if not self.config["recorder"]["enabled"]:
                if self.config["left"]["blatant"]:
                    delay = 1 / self.config["left"]["averageCPS"]
                else:
                    delay = random.random() % (2 / self.config["left"]["averageCPS"])
            else:
                delay = float(next(self.record))

            if self.config["left"]["enabled"]:
                if self.config["left"]["mode"] == "Hold" and not win32api.GetAsyncKeyState(0x01) < 0:
                    time.sleep(delay)

                    continue
            
                if self.config["left"]["RMBLock"]:
                    if win32api.GetAsyncKeyState(0x02) < 0:
                        time.sleep(delay)

                        continue

                if self.config["left"]["onlyWhenFocused"]:
                    if not "java" in self.focusedProcess and not "AZ-Launcher" in self.focusedProcess:
                        time.sleep(delay)

                        continue

                    if not self.config["left"]["workInMenus"]:
                        cursorInfo = win32gui.GetCursorInfo()[1]
                        if cursorInfo > 50000 and cursorInfo < 100000:
                            time.sleep(delay)

                            continue

                if self.config["left"]["onlyWhenFocused"]:
                    threading.Thread(target=self.leftClick, args=(True,), daemon=True).start()
                else:
                    threading.Thread(target=self.leftClick, args=(None,), daemon=True).start()

            time.sleep(delay)

    def leftClick(self, focused):
        if focused != None:
            if self.config["left"]["breakBlocks"]:
                # time.sleep(0.02)
                win32api.SendMessage(self.title, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, self.lParam)
                # win32api.SendMessage(self.title, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, self.lParam)
            else:
                win32api.SendMessage(self.title, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, self.lParam)
                time.sleep(0.02)
                win32api.SendMessage(self.title, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, self.lParam)

            if self.config["left"]["blockHit"] or (self.config["left"]["blockHit"] and self.config["right"]["enabled"] and self.config["right"]["LMBLock"] and not win32api.GetAsyncKeyState(0x02) < 0):
                if random.uniform(0, 1) <= self.config["left"]["blockHitChance"] / 100.0:
                    win32api.SendMessage(self.title, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, self.lParam)
                    time.sleep(0.02)
                    win32api.SendMessage(self.title, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, self.lParam)             
        else:
            if self.config["left"]["breakBlocks"]:
                # time.sleep(0.02)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                # win32api.SendMessage(self.title, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, self.lParam)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.02)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            if self.config["left"]["blockHit"] or (self.config["left"]["blockHit"] and self.config["right"]["enabled"] and self.config["right"]["LMBLock"] and not win32api.GetAsyncKeyState(0x02) < 0):
                if random.uniform(0, 1) <= self.config["left"]["blockHitChance"] / 100.0:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

        if self.config["left"]["soundPath"] != "" and os.path.isfile(self.config["left"]["soundPath"]):
            winsound.PlaySound(self.config["left"]["soundPath"], winsound.SND_ASYNC)

        if self.config["left"]["shakeEffect"]:
            currentPos = win32api.GetCursorPos()
            direction = random.randint(0, 3)
            pixels = random.randint(-self.config["left"]["shakeEffectForce"], self.config["left"]["shakeEffectForce"])

            if direction == 0:
                win32api.SetCursorPos((currentPos[0] + pixels, currentPos[1] - pixels))
            elif direction == 1:
                win32api.SetCursorPos((currentPos[0] - pixels, currentPos[1] + pixels))
            elif direction == 2:
                win32api.SetCursorPos((currentPos[0] + pixels, currentPos[1] + pixels))
            elif direction == 3:
                win32api.SetCursorPos((currentPos[0] - pixels, currentPos[1] - pixels))

    def leftBindListener(self):
        while True:
            if win32api.GetAsyncKeyState(self.config["left"]["bind"]) != 0:
                if "java" in self.focusedProcess or "AZ-Launcher" in self.focusedProcess:
                    cursorInfo = win32gui.GetCursorInfo()[1]
                    if cursorInfo > 50000 and cursorInfo < 100000:
                        time.sleep(0.001)

                        continue

                self.config["left"]["enabled"] = not self.config["left"]["enabled"]

                while True:
                    try:
                        dpg.set_value(checkboxToggleLeftClicker, not dpg.get_value(checkboxToggleLeftClicker))

                        break
                    except:
                        pass

                while win32api.GetAsyncKeyState(self.config["left"]["bind"]) != 0:
                    time.sleep(0.001)

            time.sleep(0.001)

    def rightClicker(self):
        while True:
            if self.config["right"]["blatant"]:
                delay = 1 / self.config["right"]["averageCPS"]
            else:
                delay = random.random() % (2 / self.config["right"]["averageCPS"])

            if self.config["right"]["enabled"]:
                if self.config["right"]["mode"] == "Hold" and not win32api.GetAsyncKeyState(0x02) < 0:
                    time.sleep(delay)

                    continue

                if self.config["right"]["LMBLock"]:
                    if win32api.GetAsyncKeyState(0x01) < 0:
                        time.sleep(delay)

                        continue

                if self.config["right"]["onlyWhenFocused"]:
                    if not "java" in self.focusedProcess and not "AZ-Launcher" in self.focusedProcess:
                        time.sleep(delay)

                        continue
            
                    if not self.config["right"]["workInMenus"]:
                        cursorInfo = win32gui.GetCursorInfo()[1]
                        if cursorInfo > 50000 and cursorInfo < 100000:
                            time.sleep(delay)

                            continue

                if self.config["right"]["onlyWhenFocused"]:
                    threading.Thread(target=self.rightClick, args=(True,), daemon=True).start()
                else:
                    threading.Thread(target=self.rightClick, args=(None,), daemon=True).start()

            time.sleep(delay)

    def rightClick(self, focused):
        if focused != None:
            win32api.SendMessage(self.title, win32con.WM_RBUTTONDOWN, win32con.MK_LBUTTON, self.lParam)
            time.sleep(0.02)
            win32api.SendMessage(self.title, win32con.WM_RBUTTONUP, win32con.MK_LBUTTON, self.lParam)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
            time.sleep(0.02)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

        if self.config["right"]["soundPath"] != "" and os.path.isfile(self.config["right"]["soundPath"]):
            winsound.PlaySound(self.config["right"]["soundPath"], winsound.SND_ASYNC)

        if self.config["right"]["shakeEffect"]:
            currentPos = win32api.GetCursorPos()
            direction = random.randint(0, 3)
            pixels = random.randint(-self.config["right"]["shakeEffectForce"], self.config["right"]["shakeEffectForce"])

            if direction == 0:
                win32api.SetCursorPos((currentPos[0] + pixels, currentPos[1] - pixels))
            elif direction == 1:
                win32api.SetCursorPos((currentPos[0] - pixels, currentPos[1] + pixels))
            elif direction == 2:
                win32api.SetCursorPos((currentPos[0] + pixels, currentPos[1] + pixels))
            elif direction == 3:
                win32api.SetCursorPos((currentPos[0] - pixels, currentPos[1] - pixels))

    def rightBindListener(self):
        while True:
            if win32api.GetAsyncKeyState(self.config["right"]["bind"]) != 0:
                if "java" in self.focusedProcess or "AZ-Launcher" in self.focusedProcess:
                    cursorInfo = win32gui.GetCursorInfo()[1]
                    if cursorInfo > 50000 and cursorInfo < 100000:
                        time.sleep(0.001)

                        continue

                self.config["right"]["enabled"] = not self.config["right"]["enabled"]

                while True:
                    try:
                        dpg.set_value(checkboxToggleRightClicker, not dpg.get_value(checkboxToggleRightClicker))

                        break
                    except:
                        pass

                while win32api.GetAsyncKeyState(self.config["right"]["bind"]) != 0:
                    time.sleep(0.001)

            time.sleep(0.001)

    def hideGUIBindListener(self):
        while True:
            if win32api.GetAsyncKeyState(self.config["misc"]["bindHideGUI"]) != 0:
                self.config["misc"]["guiHidden"] = not self.config["misc"]["guiHidden"]

                if not self.config["misc"]["guiHidden"]:
                    win32gui.ShowWindow(guiWindows, win32con.SW_SHOW)
                else:
                    win32gui.ShowWindow(guiWindows, win32con.SW_HIDE)

                while win32api.GetAsyncKeyState(self.config["misc"]["bindHideGUI"]) != 0:
                    time.sleep(0.001)

            time.sleep(0.001)

if __name__ == "__main__":
    try:
        if os.name != "nt":
            input("sharp is only working on Windows.")

            os._exit(0)

        (suppost_sid, error) = subprocess.Popen("wmic useraccount where name='%username%' get sid", stdout=subprocess.PIPE, shell=True).communicate()
        hwid = suppost_sid.split(b"\n")[1].strip().decode()

        currentWindow = win32gui.GetForegroundWindow()
        processName = psutil.Process(win32process.GetWindowThreadProcessId(currentWindow)[-1]).name()
        if processName == "cmd.exe" or processName in sys.argv[0]:
            win32gui.ShowWindow(currentWindow, win32con.SW_HIDE)

        sharpClass = sharp(hwid)
        dpg.create_context()

        def toggleLeftClicker(id: int, value: bool):
            sharpClass.config["left"]["enabled"] = value

        waitingForKeyLeft = False
        def statusBindLeftClicker(id: int):
            global waitingForKeyLeft

            if not waitingForKeyLeft:
                with dpg.handler_registry(tag="Left Bind Handler"):
                    dpg.add_key_press_handler(callback=setBindLeftClicker)

                dpg.set_item_label(buttonBindLeftClicker, "...")

                waitingForKeyLeft = True

        def setBindLeftClicker(id: int, value: str):
            global waitingForKeyLeft

            if waitingForKeyLeft:
                sharpClass.config["left"]["bind"] = value

                dpg.set_item_label(buttonBindLeftClicker, f"Bind: {chr(value)}")
                dpg.delete_item("Left Bind Handler")

                waitingForKeyLeft = False

        def setLeftMode(id: int, value: str):
            sharpClass.config["left"]["mode"] = value

        def setLeftAverageCPS(id: int, value: int):
            sharpClass.config["left"]["averageCPS"] = value

        def toggleLeftOnlyWhenFocused(id: int, value:bool):
            sharpClass.config["left"]["onlyWhenFocused"] = value

        def toggleLeftBreakBlocks(id: int, value: bool):
            sharpClass.config["left"]["breakBlocks"] = value

        def toggleLeftRMBLock(id: int, value: bool):
            sharpClass.config["left"]["RMBLock"] = value

        def toggleLeftBlockHit(id: int, value: bool):
            sharpClass.config["left"]["blockHit"] = value

        def setLeftBlockHitChance(id: int, value: int):
            sharpClass.config["left"]["blockHitChance"] = value

        def toggleLeftShakeEffect(id: int, value: bool):
            sharpClass.config["left"]["shakeEffect"] = value

        def setLeftShakeEffectForce(id: int, value: int):
            sharpClass.config["left"]["shakeEffectForce"] = value

        def setLeftClickSoundPath(id: int, value: str):
            sharpClass.config["left"]["soundPath"] = value

        def toggleLeftWorkInMenus(id: int, value: bool):
            sharpClass.config["left"]["workInMenus"] = value

        def toggleLeftBlatantMode(id: int, value: bool):
            sharpClass.config["left"]["blatant"] = value

        def toggleRightClicker(id: int, value: bool):
            sharpClass.config["right"]["enabled"] = value

        waitingForKeyRight = False
        def statusBindRightClicker(id: int):
            global waitingForKeyRight

            if not waitingForKeyRight:
                with dpg.handler_registry(tag="Right Bind Handler"):
                    dpg.add_key_press_handler(callback=setBindRightClicker)

                dpg.set_item_label(buttonBindRightClicker, "...")

                waitingForKeyRight = True

        def setBindRightClicker(id: int, value: str):
            global waitingForKeyRight

            if waitingForKeyRight:
                sharpClass.config["right"]["bind"] = value

                dpg.set_item_label(buttonBindRightClicker, f"Bind: {chr(value)}")
                dpg.delete_item("Right Bind Handler")

                waitingForKeyRight = False

        def setRightMode(id: int, value: str):
            sharpClass.config["right"]["mode"] = value

        def setRightAverageCPS(id: int, value: int):
            sharpClass.config["right"]["averageCPS"] = value

        def toggleRightOnlyWhenFocused(id: int, value: int):
            sharpClass.config["right"]["onlyWhenFocused"] = True

        def toggleRightLMBLock(id: int, value: bool):
            sharpClass.config["right"]["LMBLock"] = value

        def toggleRightShakeEffect(id: int, value: bool):
            sharpClass.config["right"]["shakeEffect"] = value

        def setRightShakeEffectForce(id: int, value: int):
            sharpClass.config["right"]["shakeEffectForce"] = value

        def setRightClickSoundPath(id: int, value: str):
            sharpClass.config["right"]["soundPath"] = value

        def toggleRightWorkInMenus(id: int, value: bool):
            sharpClass.config["right"]["workInMenus"] = value

        def toggleRightBlatantMode(id: int, value: bool):
            sharpClass.config["right"]["blatant"] = value

        def toggleRecorder(id: int, value: bool):
            sharpClass.config["recorder"]["enabled"] = value

        recording = False
        def recorder():
            global recording

            recording = True
            dpg.set_value(recordingStatusText, f"Recording: True")

            recorded = []
            start = 0

            while True:
                if not recording:
                    if len(recorded) < 2: # Avoid saving a record with 0 click
                        recorded[0] = 0.08
                    else:
                        recorded[0] = 0 # No delay for the first click

                        del recorded[-1] # Deleting last record time because that's when you click on stop button and it can take some time

                    sharpClass.config["recorder"]["record"] = recorded

                    sharpClass.record = itertools.cycle(recorded)

                    totalTime = 0
                    for clickTime in recorded:
                        totalTime += float(clickTime)

                    dpg.set_value(averageRecordCPSText, f"Average CPS of previous Record: {round(len(recorded) / totalTime, 2)}")

                    break

                if win32api.GetAsyncKeyState(0x01) < 0:
                    recorded.append(time.time() - start)

                    dpg.set_value(recordingStatusText, f"Recording: True - Recorded clicks: {len(recorded)}")

                    start = time.time()

                    while win32api.GetAsyncKeyState(0x01) < 0:
                        time.sleep(0.001)

        def startRecording():
            if not recording:
                threading.Thread(target=recorder, daemon=True).start()

        def stopRecording():
            global recording

            recording = False

            dpg.set_value(recordingStatusText, f"Recording: False")

        def selfDestruct():
            dpg.destroy_context()

        waitingForKeyHideGUI = False
        def statusBindHideGUI():
            global waitingForKeyHideGUI

            if not waitingForKeyHideGUI:
                with dpg.handler_registry(tag="Hide GUI Bind Handler"):
                    dpg.add_key_press_handler(callback=setBindHideGUI)

                dpg.set_item_label(buttonBindHideGUI, "...")

                waitingForKeyHideGUI = True

        def setBindHideGUI(id: int, value: str):
            global waitingForKeyHideGUI

            if waitingForKeyHideGUI:
                sharpClass.config["misc"]["bindHideGUI"] = value

                dpg.set_item_label(buttonBindHideGUI, f"Bind: {chr(value)}")
                dpg.delete_item("Hide GUI Bind Handler")

                waitingForKeyHideGUI = False

        def toggleOverlay(id: int, value: bool):
            sharpClass.config["misc"]["overlay"] = value

            if value:
                threading.Thread(target=sharpClass.overlay, daemon=True).start()

        def toggleSaveSettings(id: int, value: bool):
            sharpClass.config["misc"]["saveSettings"] = value

        def toggleAlwaysOnTop(id: int, value: bool):
            if value:
                win32gui.SetWindowPos(guiWindows, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(guiWindows, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        def toggleDiscordRPC(id: int, value: bool):
            sharpClass.config["misc"]["discordRichPresence"] = value

        dpg.create_viewport(title=f"[v{version}] sharp - clicker.best", width=810, height=435)

        with dpg.window(tag="Primary Window"):
            with dpg.tab_bar():
                with dpg.tab(label="Left Clicker"):
                    dpg.add_spacer(width=75)

                    with dpg.group(horizontal=True):
                        checkboxToggleLeftClicker = dpg.add_checkbox(label="Toggle", default_value=sharpClass.config["left"]["enabled"], callback=toggleLeftClicker)
                        buttonBindLeftClicker = dpg.add_button(label="Click to Bind", callback=statusBindLeftClicker)
                        dropdownLeftMode = dpg.add_combo(label="Mode", items=["Hold", "Always"], default_value=sharpClass.config["left"]["mode"], callback=setLeftMode)

                        bind = sharpClass.config["left"]["bind"]
                        if bind != 0:
                            dpg.set_item_label(buttonBindLeftClicker, f"Bind: {chr(bind)}")

                    dpg.add_spacer(width=75)

                    sliderLeftAverageCPS = dpg.add_slider_int(label="Average CPS", default_value=sharpClass.config["left"]["averageCPS"], min_value=1, callback=setLeftAverageCPS)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    checkboxLeftOnlyWhenFocused = dpg.add_checkbox(label="Only In Game", default_value=sharpClass.config["left"]["onlyWhenFocused"], callback=toggleLeftOnlyWhenFocused)

                    dpg.add_spacer(width=75)

                    checkBoxLeftBreakBlocks = dpg.add_checkbox(label="Break Blocks", default_value=sharpClass.config["left"]["breakBlocks"], callback=toggleLeftBreakBlocks)

                    dpg.add_spacer(width=75)

                    checkboxLeftRMBLock = dpg.add_checkbox(label="RMB-Lock", default_value=sharpClass.config["left"]["RMBLock"], callback=toggleLeftRMBLock)

                    dpg.add_spacer(width=125)

                    checkboxLeftBlockHit = dpg.add_checkbox(label="BlockHit", default_value=sharpClass.config["left"]["blockHit"], callback=toggleLeftBlockHit)
                    sliderLeftBlockHitChance = dpg.add_slider_int(label="BlockHit Chance", default_value=sharpClass.config["left"]["blockHitChance"], min_value=1, max_value=100, callback=setLeftBlockHitChance)

                    dpg.add_spacer(width=125)

                    checkboxLeftShakeEffect = dpg.add_checkbox(label="Shake Effect", default_value=sharpClass.config["left"]["shakeEffect"], callback=toggleLeftShakeEffect)
                    sliderLeftShakeEffectForce = dpg.add_slider_int(label="Shake Effect Force", default_value=sharpClass.config["left"]["shakeEffectForce"], min_value=1, max_value=20, callback=setLeftShakeEffectForce)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    inputLeftClickSoundPath = dpg.add_input_text(label="Click Sound Path (empty for no sound)", default_value=sharpClass.config["left"]["soundPath"], hint="Exemple: mysounds/G505.wav", callback=setLeftClickSoundPath)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    checkboxLeftWorkInMenus = dpg.add_checkbox(label="Work in Menus", default_value=sharpClass.config["left"]["workInMenus"], callback=toggleLeftWorkInMenus)
                    checkboxLeftBlatantMode = dpg.add_checkbox(label="Blatant Mode", default_value=sharpClass.config["left"]["blatant"], callback=toggleLeftBlatantMode)
                
                with dpg.tab(label="Right Clicker"):
                    dpg.add_spacer(width=75)

                    with dpg.group(horizontal=True):
                        checkboxToggleRightClicker = dpg.add_checkbox(label="Toggle", default_value=sharpClass.config["right"]["enabled"], callback=toggleRightClicker)
                        buttonBindRightClicker = dpg.add_button(label="Click to Bind", callback=statusBindRightClicker)
                        dropdownRightMode = dpg.add_combo(label="Mode", items=["Hold", "Always"], default_value=sharpClass.config["right"]["mode"], callback=setRightMode)

                        bind = sharpClass.config["right"]["bind"]
                        if bind != 0:
                            dpg.set_item_label(buttonBindRightClicker, f"Bind: {chr(bind)}")

                    dpg.add_spacer(width=75)

                    sliderRightAverageCPS = dpg.add_slider_int(label="Average CPS", default_value=sharpClass.config["right"]["averageCPS"], min_value=1, callback=setRightAverageCPS)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    checkboxRightOnlyWhenFocused = dpg.add_checkbox(label="Only In Game", default_value=sharpClass.config["right"]["onlyWhenFocused"], callback=toggleRightOnlyWhenFocused)

                    dpg.add_spacer(width=75)

                    checkboxRightLMBLock = dpg.add_checkbox(label="LMB-Lock", default_value=sharpClass.config["right"]["LMBLock"], callback=toggleRightLMBLock)

                    dpg.add_spacer(width=75)

                    checkboxRightShakeEffect = dpg.add_checkbox(label="Shake Effect", default_value=sharpClass.config["right"]["shakeEffect"], callback=toggleRightShakeEffect)
                    sliderRightShakeEffectForce = dpg.add_slider_int(label="Shake Effect Force", default_value=sharpClass.config["right"]["shakeEffectForce"], min_value=1, max_value=20, callback=setRightShakeEffectForce)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    inputRightClickSoundPath = dpg.add_input_text(label="Click Sound Path (empty for no sound)", default_value=sharpClass.config["right"]["soundPath"], hint="Exemple: mysounds/G505.wav", callback=setRightClickSoundPath)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    checkboxRightWorkInMenus = dpg.add_checkbox(label="Work in Menus", default_value=sharpClass.config["right"]["workInMenus"], callback=toggleRightWorkInMenus)
                    checkboxRightBlatantMode = dpg.add_checkbox(label="Blatant Mode", default_value=sharpClass.config["right"]["blatant"], callback=toggleRightBlatantMode)
                with dpg.tab(label="Recorder"):
                    dpg.add_spacer(width=75)

                    recorderInfoText = dpg.add_text(default_value="Records your legit way of clicking in order to produce clicks even less detectable by AntiCheat.\nAfter pressing the \"Start\" button, click as if you were in PvP for a few seconds. Then press the \"Stop\" button.\nOnly works for the left click.")

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    checkboxRecorderEnabled = dpg.add_checkbox(label="Enabled", default_value=sharpClass.config["recorder"]["enabled"], callback=toggleRecorder)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    with dpg.group(horizontal=True):
                        buttonStartRecording = dpg.add_button(label="Start Recording", callback=startRecording)
                        buttonStopRecording = dpg.add_button(label="Stop Recording", callback=stopRecording)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    averageRecordCPSText = dpg.add_text(default_value="Average CPS of previous Record: ")
                    
                    totalTime = 0
                    for clickTime in sharpClass.config["recorder"]["record"]:
                        totalTime += float(clickTime)

                    dpg.set_value(averageRecordCPSText, f"Average CPS of previous Record: {round(len(sharpClass.config['recorder']['record']) / totalTime, 2)}")

                    recordingStatusText = dpg.add_text(default_value="Recording: ")
                    dpg.set_value(recordingStatusText, f"Recording: {recording}")
                with dpg.tab(label="Misc"):
                    dpg.add_spacer(width=75)

                    buttonSelfDestruct = dpg.add_button(label="Destruct", callback=selfDestruct)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    with dpg.group(horizontal=True):
                        buttonBindHideGUI = dpg.add_button(label="Click to Bind", callback=statusBindHideGUI)
                        hideGUIText = dpg.add_text(default_value="Hide GUI")

                        bind = sharpClass.config["misc"]["bindHideGUI"]
                        if bind != 0:
                            dpg.set_item_label(buttonBindHideGUI, f"Bind: {chr(bind)}")

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    overlayInfoText = dpg.add_text(default_value="Displays an in-game GUI with Sharp's modules status info. Useful but does not work in fullscreen mode (F11)!")
                    overlayToggle = dpg.add_checkbox(label="Overlay", default_value=sharpClass.config["misc"]["overlay"], callback=toggleOverlay)

                    if sharpClass.config["misc"]["overlay"]:
                        toggleOverlay(1, True)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    saveSettings = dpg.add_checkbox(label="Save Settings", default_value=sharpClass.config["misc"]["saveSettings"], callback=toggleSaveSettings)

                    dpg.add_spacer(width=75)

                    checkboxAlwaysOnTop = dpg.add_checkbox(label="Always On Top", callback=toggleAlwaysOnTop)

                    dpg.add_spacer(width=75)

                    checkboxAlwaysOnTop = dpg.add_checkbox(label="Discord Rich Presence", default_value=sharpClass.config["misc"]["discordRichPresence"], callback=toggleDiscordRPC)

                    dpg.add_spacer(width=75)
                    dpg.add_separator()
                    dpg.add_spacer(width=75)

                    creditsText = dpg.add_text(default_value="Credits: Bambou (Developer)")
                    githubText = dpg.add_text(default_value="https://github.com/B4mb0u/Sharp")

        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 1)
                dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 20)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 1)
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (107, 110, 248))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (71, 71, 77))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (71, 71, 77))

        dpg.bind_theme(global_theme)

        dpg.create_context()
        dpg.show_viewport()
        
        guiWindows = win32gui.GetForegroundWindow()

        dpg.setup_dearpygui()
        dpg.set_primary_window("Primary Window", True)
        dpg.start_dearpygui()

        selfDestruct()
    except KeyboardInterrupt:
        os._exit(0)