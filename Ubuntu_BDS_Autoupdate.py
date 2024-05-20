#'''author : 子糖'''
# 脚本功能:检查指定路径下的upgrade_history.log文件并更新该路径下的Bedrock server
#参数
#--screen=[BDS所运行的screen]
#--dir=[BDS安装目录]
#--auto 使用at命令每天重复执行此脚本，实现自动更新


import logging
import argparse
import subprocess
import os,sys
from pathlib import Path
from packaging import version
from time import time, strftime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
url=""#下载地址
installed_version = ""#已安装版本
latest_version = ""#最新版本
upgrade_history = Path(".")#更新日志


def get_latest_version() -> str:
    global url
    with Display(visible=0, size=(800, 600)):
        firefox_options = Options()
        firefox_options.headless = True
        with webdriver.Firefox(options=firefox_options) as driver:
            driver.get("https://www.minecraft.net/en-us/download/server/bedrock")
            url = driver.find_element(
                By.XPATH,
                '//*[@id="main-content"]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[3]/div/a',
            ).get_attribute("href")
            return url.split("-")[-1].strip(".zip")


def new_version_available() -> bool:
    global installed_version
    try:
        installed_version = upgrade_history.read_text().split("\n")[-2].split(" ")[-1]
    except FileNotFoundError:
        upgrade_history.write_text("TimeStamp Date Time Upgrade_Condition Old_Version ==> New_Version\nCurrent Version : 0.0.0.0\n")
        installed_version = "0.0.0.0"
    return version.parse(latest_version) > version.parse(installed_version)


def upgrade_version(dir: str, screen: str) -> None:
    file_not_required = [
        "server.properties",
        "permissions.json",
        "allowlist.json",
        "bedrock_server_how_to.html",
        "release-notes.txt",
    ]
    try:
        screen_cmd=['screen','-x','-S',screen,'-p','0','-X','stuff']
        subprocess.run(['wget','-c','-P',dir,url],check=True)
        subprocess.run(screen_cmd+['stop\r'],check=True)
        subprocess.run(['unzip','-o',f"{dir}/{url.split('/')[-1]}",'-d',dir,'-x'] +file_not_required, check=True)
        subprocess.run(['chmod','+x',f'{dir}/bedrock_server'], check=True)
        subprocess.run(screen_cmd+['./start.sh\r'], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Upgrade Fail") from e

    with upgrade_history.open("a") as f:
        f.write(f'{int(time())} {strftime("%F %T")} upgradeComplete! {installed_version} ==> {latest_version}\n')


def check_and_update(dir: str, screen: str) -> None:
    global upgrade_history, latest_version
    upgrade_history = Path(dir) / "upgrade_history.log"
    logging.info(f"Upgrade BDS in screen = {screen} dir = {dir}")
    logging.info(f"Checking for new version......")
    try:
        latest_version = get_latest_version()
    except:
        raise Exception("Failed to retrieve the latest version.")
    else:
        logging.info(f"Successfully obtain the latest version : {latest_version}")

    if new_version_available():
        logging.info("New Version Available!\tPrepare to upgrade")
        upgrade_version(dir, screen)
        logging.info("Upgrade Success!")
    else:
        logging.info("Already the latest version")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto upgrade script for minecraft bedrock server.")
    parser.add_argument("--screen", default="mcBDS", help="Screen name where Bedrock server is running.")
    parser.add_argument("--dir",default="/opt/bedrock-server",help="Where Bedrock server is installed.")
    parser.add_argument("--auto", action="store_true", help="Enable automatic updates per day.")
    args = parser.parse_args()

    check_and_update(args.dir, args.screen)

    if args.auto:
        command = f"{os.path.realpath(sys.argv[0])} --screen {args.screen} --dir {args.dir} --auto"
        subprocess.run(f"echo {command} | at now +1days", check=True, shell=True, text=True)
        logging.info("Auto update Enabled")

    logging.info(f"Script Finished Correctly")

main()
