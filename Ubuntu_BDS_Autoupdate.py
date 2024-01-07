#'''author : 子糖'''
# 脚本功能:检查指定路径下的upgrade_history.log文件
# 以及从cdn.jsdelivr.net获取的最新版本进行更新
# 需要使用的库:time os sys requests


def userConfirm(sen):
    if Auto:
        return True
    while True:
        s = input(sen + "[y/N]?")
        if s == "y":
            return True
        elif s == "N":
            return False
        else:
            print("please input y or N")


def getLatestVersion():
    import requests

    res = requests.get(
        "https://cdn.jsdelivr.net/gh/Bedrock-OSS/BDS-Versions/versions.json"
    )
    return res.json()["linux"]["stable"]


def newVersionAvailable(direct):
    def getCurrentVersion():
        try:
            with open(f"{direct}/upgrade_history.log", "r") as f:
                return list(
                    map(int, f.read().split("\n")[-2].split(" ")[-1].split("."))
                )
        except:
            if Auto:return [0,0,0,0]
            return inputCurrentVersion()

    def inputCurrentVersion():
        while True:
            rqst = 'UnKnown Version!use "." split enter the version:\n'
            try:
                cur_version = list(map(int, input(rqst).split(".")))
                if userConfirm(cur_version):
                    break
            except:
                continue
        with open(f"{direct}/upgrade_history.log", "w") as f:
            f.write(
                "TimeStamp Date Time Upgrade_Condition Old_Version ==> New_Version\n"
            )
            f.write(
                f'Current Version : {".".join([f"{i}" for i in current_version])}\n'
            )
        return cur_version

    global new_version, current_version
    new_version = list(map(int, latest_version.split(".")))
    current_version = getCurrentVersion()
    return new_version > current_version


def upgradeVersion(direct, screen):
    zip_file = "/".join([direct, f"bedrock-server-{latest_version}.zip"])
    if system(f"wget -c -P {direct} {url}") != 0:
        raise Exception("Download incomplete")
    system(f"screen -x -S {screen} -p 0 -X stuff" + R' "stop\r"')
    if (
        system(f"unzip -o {zip_file} -d {direct}/ -x {' '.join(file_NOT_REQUIRED)}")
        != 0
    ):
        raise Exception("Decompression not completed")
    if system(f"chmod +x {direct}/bedrock_server") != 0:
        raise Exception()
    system(f"screen -x -S {screen} -p 0 -X stuff " + R'"./start\r"')
    with open(f"{direct}/upgrade_history.log", "a") as f:
        new = ".".join([f"{i}" for i in new_version])
        old = ".".join([f"{i}" for i in current_version])
        f.write(f'{int(time())} {strftime("%F %T")} upgradeComplete! {old} ==> {new}\n')


from os import system,getcwd
from sys import argv, exit
from time import time, strftime


latest_version = getLatestVersion()
global url
url = f"https://minecraft.azureedge.net/bin-linux/bedrock-server-{latest_version}.zip"

file_NOT_REQUIRED = [
    "server.properties",
    "permissions.json",
    "allowlist.json",
    "bedrock_server_how_to.html",
    "release-notes.txt",
]
direct = getcwd()
screen = "mcBDS"
Auto = False

if len(argv) != 1:
    try:
        [exec(sentence) for sentence in argv[1:]]
    except:
        raise Exception(
            'invalid parameter, Usage: screen="[screenName]" , direct="[directPath]"'
        )
elif not userConfirm(f"Use Default Setting? screen = {screen} direct = {direct}"):
    exit(0)

print(f"{strftime('%F %T')} Script Started")

if newVersionAvailable(direct):
    print("New Version Available!")
    upgradeVersion(direct, screen)
    print("upgrade success!")
else:
    print("already the latest version")

if userConfirm("Start Automatic Updates?"):
    system(
        'echo "'
        + f"{argv[0]} Auto=True screen='{screen}' direct='{direct}'"
        + '" | at now +1 days'
    )

print(f"{strftime('%F %T')} Script Finished")

exit(0)
