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
        #             time.sleep(0.1)

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
            "overlay": {
                "enabled": False,
                "onlyWhenFocused": True,
                "x": 0,
                "y": 0
            },
            "misc": {
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
                    time.sleep(0.1)

                    pass

        pyMeow.overlay_init(title="Sharp - Overlay")

        # image = base64.b64decode(re.sub("data:image/png;base64", "", "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"))

        # logo = pyMeow.load_texture_bytes(".png", image)

        while pyMeow.overlay_loop():
            if not self.config["overlay"]["enabled"]:
                pyMeow.overlay_close()

                continue

            if not "java" in self.focusedProcess and not "AZ-Launcher" in self.focusedProcess:
                if self.config["overlay"]["onlyWhenFocused"]:
                    pyMeow.end_drawing()

                    time.sleep(0.5)

                    continue
                else:
                    rect = (0, 0)

            try: # so it doesn't crash when Minecraft closed
                if not rect:
                    rect = pyMeow.get_window_info(self.realTitle)
            except:
                time.sleep(0.5)

                continue

            pyMeow.begin_drawing()

            # pyMeow.draw_texture(logo, rect[0]+2, rect[1]+2, pyMeow.get_color(""), 0, 0.5)

            # Modules
            pyMeow.draw_text(f"Left", rect[0]+self.config["overlay"]["x"]+2, rect[1]+self.config["overlay"]["y"]+2, 15, pyMeow.get_color("orange"))
            pyMeow.draw_text(f"Right", rect[0]+self.config["overlay"]["x"]+2, rect[1]+self.config["overlay"]["y"]+16.9, 15, pyMeow.get_color("orange"))

            # Modules Status
            pyMeow.draw_text(f"[Enabled]" if self.config["left"]["enabled"] else "[Disabled]", rect[0]+self.config["overlay"]["x"]+40, rect[1]+self.config["overlay"]["y"]+2, 15, pyMeow.get_color("green") if self.config["left"]["enabled"] else pyMeow.get_color("red"))
            pyMeow.draw_text(f"[Enabled]" if self.config["right"]["enabled"] else "[Disabled]", rect[0]+self.config["overlay"]["x"]+40, rect[1]+self.config["overlay"]["y"]+16.9, 15, pyMeow.get_color("green") if self.config["right"]["enabled"] else pyMeow.get_color("red"))

            pyMeow.end_drawing()

            rect = None

            time.sleep(0.1)

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
                        time.sleep(0.1)

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
                        time.sleep(0.1)

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
            sharpClass.config["overlay"]["enabled"] = value

            if value:
                threading.Thread(target=sharpClass.overlay, daemon=True).start()

        def toggleOverlayOnlyWhenFocused(id: int, value: bool):
            sharpClass.config["overlay"]["onlyWhenFocused"] = value

        def setOverlayX(id: int, value: int):
            sharpClass.config["overlay"]["x"] = value

        def setOverlayY(id: int, value: int):
            sharpClass.config["overlay"]["y"] = value

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

                    with dpg.group(horizontal=True):
                        overlayToggle = dpg.add_checkbox(label="Overlay", default_value=sharpClass.config["overlay"]["enabled"], callback=toggleOverlay)

                        if sharpClass.config["overlay"]["enabled"]:
                            toggleOverlay(1, True)

                        overlayOnlyWhenFocusedToggle = dpg.add_checkbox(label="Only when game focused (easier to change overlay position when disabled)", default_value=sharpClass.config["overlay"]["onlyWhenFocused"], callback=toggleOverlayOnlyWhenFocused)

                    overlayXSlider = dpg.add_slider_int(label="X Position", default_value=sharpClass.config["overlay"]["x"], min_value=0, max_value=1920, callback=setOverlayX)
                    overlayYSlider = dpg.add_slider_int(label="Y Position", default_value=sharpClass.config["overlay"]["y"], min_value=0, max_value=1080, callback=setOverlayY)

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