import ctypes
import argparse
import binascii
import glob
import os
import re
import shlex
import subprocess
import time
import sys
import logging
import requests
from bs4 import BeautifulSoup
import dearpygui.dearpygui as dpg
from dataclasses import asdict, dataclass
from typing import Optional
from playwright.sync_api import sync_playwright
import json
from pathlib import Path

SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)

APP_NAME = "AutoRag"


def appdata_roaming_dir() -> Path:
    base = Path(os.environ["APPDATA"])
    dir = base / APP_NAME
    dir.mkdir(parents=True, exist_ok=True)
    return dir


STATE_FILE = appdata_roaming_dir() / "appstate.json"


@dataclass
class AppState:
    session: Optional[requests.Session] = None
    username: Optional[str] = None
    password: Optional[str] = None
    authName: Optional[str] = None
    authValue: Optional[str] = None
    roAccount: Optional[dict[str, str]] = None

    def save(self, path=STATE_FILE):
        d = asdict(self)
        d.pop("session", None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)

    @classmethod
    def load(cls, path=STATE_FILE):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception as e:
            return cls()
        return cls(**d)


appState = AppState.load()
appState.session = requests.Session()


def waitForGameMon():
    while 1:
        output = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq GameMon.des"]
        )
        if "GameMon.des" in output.decode():
            log.debug("GameMon.des exists")
            # TODO: might not be reliable for user
            time.sleep(3)
            return
        log.debug("Waiting for GameMon.des")
        time.sleep(0.5)


def delete_gg_files(rag_path):
    trash = glob.glob(rag_path + "/GameGuard/*.erl")
    trash += glob.glob(rag_path + "/GameGuard/*.erv")
    trash += glob.glob(rag_path + "/GameGuard/*.ver")
    for t in trash:
        os.remove(t)


def killAll():
    log.debug("Killing ragexe")
    ragKill = subprocess.run(
        "taskkill /im Ragexe.exe /F", capture_output=True, shell=True
    )
    log.debug(ragKill.stdout.decode())
    log.debug(ragKill.stderr.decode())

    log.debug("Killing wxstart.exe so ragnarok can launch. Or you can use openkore.pl")
    perlKill = subprocess.run(
        "taskkill /im perl.exe /F /T", capture_output=True, shell=True
    )
    log.debug(perlKill.stdout.decode())
    log.debug(perlKill.stderr.decode())

    wxKill = subprocess.run(
        "taskkill /im wxstart.exe /F /T", capture_output=True, shell=True
    )
    log.debug(wxKill.stdout.decode())
    log.debug(wxKill.stderr.decode())


parser = argparse.ArgumentParser(
    description="Retrieve Rgarnok login hash and intial bring-up"
)
parser.add_argument("-u", help="username", required=False)
parser.add_argument("-p", help="password", required=False)
parser.add_argument("-k", help="website login cookie key", required=False)
parser.add_argument("-v", help="webstie login cookie value", required=False)
parser.add_argument("-g", help="Game path", default="C:/Gravity/Ragnarok")
parser.add_argument("-a", help="roaccount")
parser.add_argument("-f", help="forward to openkore")

args = parser.parse_args()

cwd = os.getcwd()

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    # "origin": "https://member.gungho.jp",
    # "referer": "https://member.gungho.jp/front/ro/iframe/login.aspx"
}


# Parse roaccount from menu.aspx
def parseRoAccountsFromMenuHtml(html: bytes):
    soup = BeautifulSoup(html, "lxml")
    sel = soup.select_one("select#ddlCPID")
    if not sel:
        return []

    accounts = []
    for opt in sel.select("option[value]"):
        siid = opt.get("value")
        label = opt.get_text()
        if not siid or siid == "select":
            continue

        accounts.append((label, siid))
    return accounts


def populateAccountDropdown(accounts):
    labels = [label for (label, _siid) in accounts]
    dpg.configure_item("roAccountCombo", items=labels)
    dpg.set_value("roAccountCombo", labels[0])


# Log in and parse ro accounts
def getLaunchUrl(username, password, authCookieName, authCookieValue):
    host = "https://member.gungho.jp"
    login_url = "https://member.gungho.jp/front/ro/iframe/login.aspx"

    session = appState.session
    session.cookies.set(
        name=authCookieName, value=authCookieValue, domain="member.gungho.jp", path="/"
    )

    # wireguard
    #  wireguard = "C:/Program Files/WireGuard/wireguard.exe"
    #  proxy_conf = os.path.join(cwd, "Japan.conf")
    #  start_proxy = [wireguard, "/installtunnelservice", proxy_conf]
    #  subprocess.Popen(start_proxy);
    #  time.sleep(1)

    loginGet = session.get(login_url, timeout=3)
    loginGet.raise_for_status()

    # Build POST data from all hidden inputs, then add username and password
    # eg. __VIEWSTATE, __VIEWSTATEGENERATOR
    soup = BeautifulSoup(loginGet.content, "lxml")
    newPayload = {
        i["name"]: i.get("value", "") for i in soup.select('input[type="hidden"][name]')
    }
    newPayload["loginNameControl$txtLoginName"] = username
    newPayload["passwordControl$txtPassword"] = password
    newPayload["login"] = ""

    #  login_soup = BeautifulSoup(login_response.content, "lxml")
    #  log.debug(login_soup)
    # Log in to get all the roaccount
    login_response = session.post(login_url, data=newPayload, headers=HEADERS)
    login_response.raise_for_status()
    accounts = parseRoAccountsFromMenuHtml(login_response.content)
    populateAccountDropdown(accounts)
    appState.roAccount = {label: siid for (label, siid) in accounts}
    return True


from urllib.parse import parse_qs


def interactiveLogin():
    captured = {}

    def onRequest(req):
        if req.method != "POST":
            return
        if "front/ro/iframe/login.aspx" not in req.url:
            return
        log.debug("on request")
        form = parse_qs(req.post_data or "")
        captured["username"] = form.get("loginNameControl$txtLoginName", [""])[0]
        captured["password"] = form.get("passwordControl$txtPassword", [""])[0]
        captured["otp"] = form.get("OTPControl$inputOTP", [""])[0]
        #  log.debug(captured)
        appState.username = captured["username"]
        appState.password = captured["password"]

    with sync_playwright() as p:
        #  width, height = 10, 10
        #  x = (SCREEN_WIDTH - width) // 2
        #  y = (SCREEN_HEIGHT - height) // 2
        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )
        context = browser.new_context()
        context.on("request", onRequest)
        page = context.new_page()
        page.goto("https://member.gungho.jp/front/ro/iframe/login.aspx")
        page.wait_for_url("https://ragnarokonline.gungho.jp/**", timeout=180_000)

        cookies = context.cookies("https://member.gungho.jp")
        log.debug(cookies)
        authCookie = next(
            (
                c
                for c in cookies
                if c.get("domain") == ".gungho.jp"
                and c.get("name", "").startswith("GHLI")
            ),
            None,
        )
        log.debug(authCookie)
        appState.authName = authCookie["name"]
        appState.authValue = authCookie["value"]
        return True


def launchGame(siid):
    killAll()

    menuUrl = f"https://member.gungho.jp/front/ro/iframe/menu.aspx?SIID={siid}"

    launch_response = appState.session.post(menuUrl, headers=HEADERS)
    match = re.search(r"GameStartAsync\('(\w+)'\)", launch_response.text)
    #  log.debug(launch_response.text)
    # Added trailing equal sign to complete the base64
    s = match.group(1) + "="
    data = binascii.unhexlify(binascii.a2b_base64(s))
    chunks = [data[i : i + 4] for i in range(0, len(data), 4)]
    onetime_key = ""
    for i in chunks:
        result = int.from_bytes(i, byteorder="big") ^ 0x12345678
        onetime_key += result.to_bytes(4, byteorder="big").decode("ascii")
    log.debug(f"one time key: {onetime_key}")

    passwd = re.search(r"-p:(\w+)", onetime_key).group(1)
    log.debug(passwd)

    log.debug("Taking out the trash before game start")
    # TODO: pass ragnarko online path
    delete_gg_files(args.g)

    # Launch game
    commandline = r"Ragexe.exe 1rag1 -w {}".format(onetime_key).rstrip("\x00")
    commandline = shlex.split(commandline)
    log.debug(commandline)
    # TODO: locate game installation dir
    os.chdir(args.g)
    # Popen to non block
    ragproc = subprocess.Popen(
        commandline, creationflags=subprocess.HIGH_PRIORITY_CLASS
    )

    # Inject npgg
    # TODO: Assume openkore is in cwd?
    os.chdir(cwd)
    waitForGameMon()
    inject_antigg = "Manualmap.exe -target GameMon.des -dll AntiGG.dll"
    ret = subprocess.run(inject_antigg, capture_output=True, text=True)
    log.debug(ret.stdout)
    log.debug(ret.stderr)

    # Launch openkore
    # TODO: Read arguments
    arguments = r"-interface=Wx --config=control\config-shadowCross.txt"
    openkore = "perl openkore.pl " + arguments
    log.debug("Launching openkore: " + openkore)
    subprocess.Popen(
        openkore, close_fds=True, creationflags=subprocess.DETACHED_PROCESS
    )
    time.sleep(1)

    # Inject client
    inject_raven = "Manualmap.exe -target Ragexe.exe -dll Raven.dll"
    ret = subprocess.run(inject_raven, capture_output=True, text=True)
    log.debug(ret.stdout)
    log.debug(ret.stderr)


def teardownCallback():
    killAll()


def loginCallback():
    # 1) Try to get a launch URL without interactive login
    try:
        ok = getLaunchUrl(
            appState.username, appState.password, appState.authName, appState.authValue
        )
    except Exception as e:
        ok = False

    # 2) Only fall back to interactive login if URL is missing/empty (or an exception happened)
    if not ok:
        dpg.configure_item("loginBtn", enabled=False)
        try:
            ok = interactiveLogin()
        except Exception as e:
            log.error("Interactive login failed")
            log.error(e)
            return
        finally:
            dpg.configure_item("loginBtn", enabled=True)

        if not ok:
            log.error("Interactive login failed with false")
            return

        # 3) Retry launch URL after interactive login (in case appState creds changed)
        try:
            ok = getLaunchUrl(
                appState.username,
                appState.password,
                appState.authName,
                appState.authValue,
            )
        except Exception as e:
            log.error("Login failed")
            log.error(e)
            return
        if not ok:
            log.error("Login failed with false")
            return

    appState.save()
    log.info("Succesfully loged in")
    dpg.configure_item("launchBtn", enabled=True)


def launchCallback():
    try:
        account = dpg.get_value("roAccountCombo")
        siid = appState.roAccount[account]
        launchGame(siid)
    except Exception as e:
        log.error("Launch game failed, disabling launch button")
        log.error(e)
        dpg.configure_item("launchBtn", enabled=False)


dpg.create_context()

with dpg.theme() as light_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text, (30, 30, 30), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_WindowBg, (245, 245, 245), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ChildBg, (250, 250, 250), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_PopupBg, (255, 255, 255), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_FrameBg, (235, 235, 235), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_FrameBgHovered, (220, 220, 220), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_FrameBgActive, (210, 210, 210), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Button, (225, 225, 225), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonHovered, (205, 205, 205), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonActive, (190, 190, 190), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_FramePadding, 8, 6, category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_ItemSpacing, 8, 8, category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_TextDisabled, (140, 140, 140), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_DisabledAlpha, 0.35, category=dpg.mvThemeCat_Core
        )
    # fix for disabled theme see DearPyGui/issues/2068
    # fmt: off
    comps = [ dpg.mvInputText, dpg.mvButton, dpg.mvRadioButton, dpg.mvTabBar, dpg.mvTab, dpg.mvImage, dpg.mvMenuBar, dpg.mvViewportMenuBar, dpg.mvMenu, dpg.mvMenuItem, dpg.mvChildWindow, dpg.mvGroup, dpg.mvDragFloatMulti, dpg.mvSliderFloat, dpg.mvSliderInt, dpg.mvFilterSet, dpg.mvDragFloat, dpg.mvDragInt, dpg.mvInputFloat, dpg.mvInputInt, dpg.mvColorEdit, dpg.mvClipper, dpg.mvColorPicker, dpg.mvTooltip, dpg.mvCollapsingHeader, dpg.mvSeparator, dpg.mvCheckbox, dpg.mvListbox, dpg.mvText, dpg.mvCombo, dpg.mvPlot, dpg.mvSimplePlot, dpg.mvDrawlist, dpg.mvWindowAppItem, dpg.mvSelectable, dpg.mvTreeNode, dpg.mvProgressBar, dpg.mvSpacer, dpg.mvImageButton, dpg.mvTimePicker, dpg.mvDatePicker, dpg.mvColorButton, dpg.mvFileDialog, dpg.mvTabButton, dpg.mvDrawNode, dpg.mvNodeEditor, dpg.mvNode, dpg.mvNodeAttribute, dpg.mvTable, dpg.mvTableColumn, dpg.mvTableRow,
    ]
    for comp_type in comps:
        with dpg.theme_component(comp_type, enabled_state=False):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (0.50 * 255, 0.50 * 255, 0.50 * 255, 1.00 * 255)
            )
    comps = [ dpg.mvInputText, dpg.mvButton, dpg.mvRadioButton, dpg.mvTabBar, dpg.mvTab, dpg.mvImage, dpg.mvMenuBar, dpg.mvViewportMenuBar, dpg.mvMenu, dpg.mvMenuItem, dpg.mvChildWindow, dpg.mvGroup, dpg.mvDragFloatMulti, dpg.mvSliderFloat, dpg.mvSliderInt, dpg.mvFilterSet, dpg.mvDragFloat, dpg.mvDragInt, dpg.mvInputFloat, dpg.mvInputInt, dpg.mvColorEdit, dpg.mvClipper, dpg.mvColorPicker, dpg.mvTooltip, dpg.mvCollapsingHeader, dpg.mvSeparator, dpg.mvCheckbox, dpg.mvListbox, dpg.mvText, dpg.mvCombo, dpg.mvPlot, dpg.mvSimplePlot, dpg.mvDrawlist, dpg.mvWindowAppItem, dpg.mvSelectable, dpg.mvTreeNode, dpg.mvProgressBar, dpg.mvSpacer, dpg.mvImageButton, dpg.mvTimePicker, dpg.mvDatePicker, dpg.mvColorButton, dpg.mvFileDialog, dpg.mvTabButton, dpg.mvDrawNode, dpg.mvNodeEditor, dpg.mvNode, dpg.mvNodeAttribute, dpg.mvTable, dpg.mvTableColumn, dpg.mvTableRow,
    ]
    for comp_type in comps:
        with dpg.theme_component(comp_type, enabled_state=False):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (0.50 * 255, 0.50 * 255, 0.50 * 255, 1.00 * 255)
            )
            dpg.add_theme_color(dpg.mvThemeCol_Button, (45, 45, 48))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (45, 45, 48))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (45, 45, 48))
dpg.bind_theme(light_theme)
# fmt: on


class ConsoleRedirect:

    def __init__(self, tag):
        self.tag = tag

    def write(self, s):
        if not s or not dpg.does_item_exist(self.tag):
            return
        dpg.set_value(self.tag, dpg.get_value(self.tag) + s)

    def flush(self):
        pass


def load_font():
    with dpg.font_registry():
        # TODO load font in cwd
        with dpg.font(
            "C:/Users/lovemanachan/AppData/Local/Microsoft/Windows/Fonts/SarasaMonoJ-SemiBold.ttf",
            18,
        ) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
    dpg.bind_font(default_font)


with dpg.window(tag="Primary", no_scrollbar=True, no_scroll_with_mouse=True):
    # Keep the controls area a fixed height; let the console fill the rest so it
    # grows/shrinks with the window.
    with dpg.child_window(tag="mainArea", width=-1, height=240, border=False):
        dpg.add_text("Subscription email")
        dpg.add_input_text(tag="email", label="")
        dpg.add_combo(tag="roAccountCombo", label="RO account")
        with dpg.group(horizontal=True):
            dpg.add_button(
                tag="loginBtn",
                label="Login",
                callback=loginCallback,
                width=200,
                height=100,
            )
            dpg.add_button(
                tag="launchBtn",
                label="ゲーム起動",
                callback=launchCallback,
                width=200,
                height=100,
                enabled=False,
            )
            dpg.add_button(
                label="Teardown", callback=teardownCallback, width=200, height=100
            )
    with dpg.child_window(tag="consoleArea", width=-1, height=-1, border=True):
        dpg.add_input_text(
            tag="console", multiline=True, readonly=True, width=-1, height=-1
        )
dpg.set_primary_window("Primary", True)

sys.stdout = ConsoleRedirect("console")
sys.stderr = ConsoleRedirect("console")

log = logging.getLogger("autorag")
log.setLevel(logging.DEBUG)
h = logging.StreamHandler(sys.stdout)
h.setLevel(logging.DEBUG)
log.addHandler(h)

W, H = 640, 600
dpg.create_viewport(title=APP_NAME, width=W, height=H)

sw = ctypes.windll.user32.GetSystemMetrics(0)
sh = ctypes.windll.user32.GetSystemMetrics(1)
dpg.set_viewport_pos(((SCREEN_WIDTH - W) // 2, (SCREEN_HEIGHT - H) // 2))

dpg.setup_dearpygui()
dpg.set_frame_callback(1, load_font)
dpg.show_viewport()
# Load after the first frame.
# Do a splash screen first if you don't like the first ??? texts
dpg.start_dearpygui()
dpg.destroy_context()
