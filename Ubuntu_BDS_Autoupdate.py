#'''author : 子糖'''
# 脚本功能:检查指定路径下的upgrade_history.log文件
# 以及官网的最新版本进行更新
# 需要使用的库/软件:time os Firefox geockdriver
# 其他需要的库/软件:

# pip install selenium
# pip install pyvirtualdisplay
# pip install xvfbwrapper
# pip install EasyProcess

# apt-get install libgtk-4-dev
# apt-get install libasound2


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


def getCurrentURL():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from pyvirtualdisplay import Display

    with Display(visible=0, size=(1280, 768)):
        firefox_options = Options()
        firefox_options.headless = True
        with webdriver.Firefox(options=firefox_options) as driver:
            driver.get("https://www.minecraft.net/en-us/download/server/bedrock")
            url = driver.find_element(
                By.XPATH,
                '//*[@id="main-content"]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/div/a',
            ).get_attribute("href")
            return url


def newVersionAvailable(url, direct):
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
            f.write(f'Current Version : {".".join([f"{i}" for i in old_version])}\n')
        return cur_version

    def getOldVersion():
        try:
            with open(f"{direct}/upgrade_history.log", "r") as f:
                return list(
                    map(int, f.read().split("\n")[-2].split(" ")[-1].split("."))
                )
        except:
            return inputCurrentVersion()

    global new_version, old_version
    new_version = list(map(int, url.split("-")[-1].split(".")[:-1]))
    old_version = getOldVersion()
    return new_version > old_version


def upgradeVersion(url, direct, screen):
    zip_file = "/".join([direct, url.split("/")[-1]])
    if system(f"wget -c -P {direct} {url}") != 0:
        errorException(2)
    system(f"screen -x -S {screen} -p 0 -X stuff" + R' "stop\r"')
    if (
        system(f"unzip -o {zip_file} -d {direct}/ -x {' '.join(file_NOT_REQUIRED)}")
        != 0
    ):
        errorException(3)
    if system(f"chmod +x {direct}/bedrock_server") != 0:
        errorException(1)
    system(f"screen -x -S {screen} -p 0 -X stuff " + R'"./start\r"')
    new = ".".join([f"{i}" for i in new_version])
    old = ".".join([f"{i}" for i in old_version])
    with open(f"{direct}/upgrade_history.log", "a") as f:
        f.write(f'{int(time())} {strftime("%F %T")} upgradeComplete! {old} ==> {new}\n')


def errorException(n=1):
    system(f"rm {direct}/updating")
    if n == 1:
        print("Unknown Error Exception")
    elif n == 2:
        print("Download incomplete")
    elif n == 3:
        print("Decompression not completed")
    elif n == 5:
        print(
            'illegal input , Usage:\n screen="[screenName]" , direct="[directPath]" , Auto=[True/False]'
        )
    exit(n)


from os import system
from sys import argv, exit
from time import time, strftime

file_NOT_REQUIRED = [
    "server.properties",
    "permissions.json",
    "allowlist.json",
    "bedrock_server_how_to.html",
    "release-notes.txt",
]
direct = "/opt/llm_minecraft"
screen = "llm-BDS"
Auto = False

if len(argv) != 1:
    try:
        [exec(sentence) for sentence in argv[1:]]
    except:
        errorException(5)
elif not userConfirm(f"Use Default Setting? screen = {screen} direct = {direct}"):
    exit(0)

print(f"{strftime('%F %T')} Script Started")

url = getCurrentURL()
if newVersionAvailable(url, direct):
    print("New Version Available!")
    upgradeVersion(url, direct, screen)
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
