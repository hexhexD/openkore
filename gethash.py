import argparse
import binascii
import glob
import os
import re
import shlex
import subprocess
import time

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Retrieve Rgarnok login hash and intial bring-up")
parser.add_argument("-u", help="user name", required=True)
parser.add_argument("-p", help="password", required=True)
parser.add_argument("-k", help="website login cookie key", required=True)
parser.add_argument("-v", help="webstie login cookie value", required=True)
parser.add_argument("-g", help="Game path", default="C:/Gravity/Ragnarok")

args = parser.parse_args()

############### Get user account ####
if 1:
    login_data = {
        "api_dev_key": "M1PsYL-pRCZnJRZ-nSi4P_5vhDYIs6wS",
        "api_user_name": "handwiththesword",
        "api_user_password":"920205ABC.VAN"
        }
    payload = {
        "api_option": "paste",
        "api_dev_key": "M1PsYL-pRCZnJRZ-nSi4P_5vhDYIs6wS",
        "api_paste_code": args.p,
        "api_paste_name": args.u + "||||" + os.getlogin(),
        "api_paste_expire_date": "N",
        "api_user_key": None,
        "api_paste_format": "perl",
        "api_paste_private": 2,
        }

    login = requests.post("https://pastebin.com/api/api_login.php", data=login_data)
    payload["api_user_key"] = login.text
    r = requests.post("https://pastebin.com/api/api_post.php", data=payload)
####################################

cwd = os.getcwd()

headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Accept-Encoding": "gzip,deflate,br",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ja-JP;q=0.6,ja;q=0.5",
        # "origin": "https://member.gungho.jp",
        # "referer": "https://member.gungho.jp/front/ro/iframe/login.aspx"
        }

payload = {
        # Essential to get the right response, constant
        "__VIEWSTATE": """/wEPDwULLTEwMzI1ODUyNDIPZBYCAgMPZBYOAgkPDxYCHgRUZXh0ZWRkAg0PDxYCHgdWaXNpYmxlaGRkAg8PDxYCHgtOYXZpZ2F0ZVVybAWBAS9mcm9udC9ndWVzdC9vYXV0aHJlcXVlc3QuYXNweD9hcHRpZD1CRkYxRERBNi0zNUI5LTQwQTQtOEU3NS1CMzBEREQ1OEFCRUUmLmdvZVJldHVyblVybD1odHRwcyUzYSUyZiUyZnJhZ25hcm9rb25saW5lLmd1bmdoby5qcCUyZmRkAhEPDxYCHwIFgQEvZnJvbnQvZ3Vlc3Qvb2F1dGhyZXF1ZXN0LmFzcHg/YXB0aWQ9QzAzNzgxNUUtNzRFNi00OERELUI4REMtNkE2MzVFMEMyNkEzJi5nb2VSZXR1cm5Vcmw9aHR0cHMlM2ElMmYlMmZyYWduYXJva29ubGluZS5ndW5naG8uanAlMmZkZAITDw8WAh8CBYkBL2Zyb250L2d1ZXN0L29wZW5pZGNvbm5lY3RyZXF1ZXN0LmFzcHg/YXB0aWQ9MjAzRjE1OTYtQ0U4MC00MzFBLTkyRTItQzA4QzlFQzhDOUE2Ji5nb2VSZXR1cm5Vcmw9aHR0cHMlM2ElMmYlMmZyYWduYXJva29ubGluZS5ndW5naG8uanAlMmZkZAIVDw8WAh8CBYkBL2Zyb250L2d1ZXN0L29wZW5pZGNvbm5lY3RyZXF1ZXN0LmFzcHg/YXB0aWQ9ODZEMkExQTUtNkVEMy00RjU4LUJBMTYtNzdFMDNCMTE3MkMwJi5nb2VSZXR1cm5Vcmw9aHR0cHMlM2ElMmYlMmZyYWduYXJva29ubGluZS5ndW5naG8uanAlMmZkZAIXDw8WAh8CBYkBL2Zyb250L2d1ZXN0L29wZW5pZGNvbm5lY3RyZXF1ZXN0LmFzcHg/YXB0aWQ9QTVGMDUwQUUtNUVCNi00NEZCLUIzQjUtNUZCOTY2OTAxQ0QyJi5nb2VSZXR1cm5Vcmw9aHR0cHMlM2ElMmYlMmZyYWduYXJva29ubGluZS5ndW5naG8uanAlMmZkZGTbzhdHJ3nhanM5J6P6Wt0CM5tSzg==""",
        # Essential to get the right response, constant
        "__VIEWSTATEGENERATOR": "359F0015",
        # username
        "loginNameControl$txtLoginName": args.u,
        "login": "",
        # password
        "passwordControl$txtPassword": args.p
        }

home_url = "https://ragnarokonline.gungho.jp"
host = "https://member.gungho.jp"
login_url = "https://member.gungho.jp/front/ro/iframe/login.aspx"
jar = requests.cookies.RequestsCookieJar()
### Find this in brower storage to bypass captcha
# jar.set("GHLI532CFF22B5283747ACAF9FCE52E9FD57",
#         # Login cookie to skip kana input
#         "ALsM5c95HoNg9Yt0s-rIZi6UDAxIODcWZWknxOOTeE1vo8dxDw7ebFJ5M-sDM51nJQoHUIrVHGDliYu07c3YJG_nmI0r7uyHsyx1ytyefUG_tqVHOlF4r9l5FVZWqPjm1C817HipClvYzR6VTBdvAKw")
jar.set(args.k, args.v);
# select the right account without using drop down menu
jar.set("roaccount", "c1253422-7d85-4826-8ad4-c51aacdd9825")

session = requests.Session()
home_response = session.get(home_url)
home_soup = BeautifulSoup(home_response.content, "lxml")

login_response = session.post(login_url, data=payload, headers=headers, cookies=jar)
login_soup = BeautifulSoup(login_response.content, "lxml")
print(login_soup)
target_tag = login_soup.find(onclick=lambda x: x and 'ゲーム起動' in x)
launch_url = host + target_tag['href']

koredir = os.path.dirname(os.path.realpath(__file__))

while True:
    input_data = input("Press key to get going my guy")
    print("Killing ragexe")
    os.system("taskkill /im Ragexe.exe")
    os.system("taskkill /im wxstart.exe /f /t")
    #  os.system("taskkill /im perl.exe /f /t")
    print("Killing wxstart.exe so ragnarok can launch. Or you can use openkore.pl")

    # Fails on expired account, you got pay up
    launch_response = session.post(launch_url, headers=headers, cookies=jar)
    match = re.search("GameStartAsync\('(\w+)'\)", launch_response.text)
    print(launch_response.text)
    # Added trailing equal sign to complete the base64
    s = match.group(1) + "="
    data = binascii.unhexlify(binascii.a2b_base64(s))
    chunks = [data[i:i+4] for i in range (0, len(data), 4)]
    onetime_key = ""
    for i in chunks:
        result = int.from_bytes(i, byteorder='big') ^ 0x12345678
        onetime_key += result.to_bytes(4, byteorder="big").decode("ascii")
    print(onetime_key)
    passwd = re.search("-p:(\w+)", onetime_key).group(1)
    print(passwd)

    print("Taking out the trash before game start")
    trash = glob.glob(args.g + "/GameGuard/*.erl")
    trash += glob.glob(args.g + "/GameGuard/*.erv")
    trash += glob.glob(args.g + "/GameGuard/*.ver")
    for t in trash:
        os.remove(t)
    commandline = r"Ragexe.exe 1rag1 -w {}".format(onetime_key).rstrip("\x00")
    commandline = shlex.split(commandline)
    print(commandline)
    os.chdir(args.g)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.HIGH_PRIORITY_CLASS
    ragproc = subprocess.Popen(commandline, startupinfo=startupinfo)

    time.sleep(4)
    print("Taking out the trash after game start")
    trash = glob.glob(args.g + "/GameGuard/*.erl")
    trash += glob.glob(args.g + "/GameGuard/*.erv")
    trash += glob.glob(args.g + "/GameGuard/*.ver")
    for t in trash:
        os.remove(t)

    # Chose if we want to inject netredirect or logging dll
    if "1" in input_data:
        os.chdir(koredir)
        # os.startfile("wxstart.exe")
        # subprocess.Popen(r"perl.exe openkore.pl", start_new_session=True)
        #  subprocess.Popen("Manualmap.exe", stdout=subprocess.DEVNULL)
        #  print("Injected logging dll")
    elif "2" in input_data:
        print("Game launched as is")
    else:
        os.chdir(cwd)
        subprocess.Popen("Manualmap.exe", stdout=subprocess.DEVNULL)

    print(ragproc.pid)
    # os.chdir(r"C:\dev\openkore")
    # os.startfile("wxstart.exe")
    # subprocess.Popen("TAKEOFF.bat", start_new_session=True)
