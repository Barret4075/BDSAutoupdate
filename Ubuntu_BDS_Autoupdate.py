#'''author : 子糖'''
# 脚本功能:检查指定路径下的upgrade_history.log文件并更新该路径下的Bedrock server
#参数
#--screen=[BDS所运行的screen]
#--dir=[BDS安装目录]
#--auto 使用at命令每天重复执行此脚本，实现自动更新


import argparse
import logging
import os
from pathlib import Path
import subprocess
from time import time, strftime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_latest_version():
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


def new_version_available(dir, latest_version):
    upgrade_history_path = Path(dir) / "upgrade_history.log"
    try:
        old_version = upgrade_history_path.read_text().split("\n")[-2].split(" ")[-1]
    except FileNotFoundError:
        upgrade_history_path.write_text(
            "TimeStamp Date Time Upgrade_Condition Old_Version ==> New_Version\nCurrent Version : 0\n"
        )
        old_version = "0"
    from packaging import version

    return version.parse(latest_version) > version.parse(old_version)


def upgrade_version(dir, screen, latest_version):
    file_not_required = [
        "server.properties",
        "permissions.json",
        "allowlist.json",
        "bedrock_server_how_to.html",
        "release-notes.txt",
    ]
    try:
        subprocess.run(
            ["wget","-c","-P",dir,f"https://minecraft.azureedge.net/bin-linux/bedrock-server-{latest_version}.zip",],
            check=True,
        )
        subprocess.run(
            ["screen", "-x", "-S", screen, "-p", "0", "-X", "stuff", "stop\r"],
            check=True,
        )

        subprocess.run(
            ["unzip", "-o", f"{dir}/bedrock-server-{latest_version}.zip", "-d", dir]
            + ["-x"]
            + file_not_required,
            check=True,
        )
        subprocess.run(["chmod", "+x", f"{dir}/bedrock_server"], check=True)
        subprocess.run(
            ["screen", "-x", "-S", screen, "-p", "0", "-X", "stuff", "./start.sh\r"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise Exception("An error occurred during the upgrade process") from e

    with open(f"{dir}/upgrade_history.log", "a") as f:
        f.write(
            f'{int(time())} {strftime("%F %T")} upgradeComplete! 0 ==> {latest_version}\n'
        )


def check_and_update(screen, dir, auto):
    logging.info(f"Upgrade BDS in screen = {screen} dir = {dir}")
    try:
        latest_version = get_latest_version()
    except:
        logging.error("Failed to get lasted version")
        return
    else:
        logging.info(f"Successfully obtain the latest version : {latest_version}")
    if new_version_available(dir, latest_version):
        logging.info("New Version Available!\tPrepare to upgrade")
        upgrade_version(dir, screen, latest_version)
        logging.info("Upgrade Success!")
    else:
        logging.info("Already the latest version")
    if auto:
        command=f"{__file__} --screen={screen} --dir={dir} --auto"
        subprocess.run(f"echo {command} | at now +1days", check=True, shell=True, text=True)
        logging.info("Auto update Enabled")


def main():
    parser = argparse.ArgumentParser(description="Upgrade BDS script.")
    parser.add_argument("--screen", default="mcBDS", help="Screen name where Bedrock server is running.")
    parser.add_argument(
        "--dir", default=os.getcwd(), help="Directory where Bedrock server is installed."
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Enable automatic updates without confirmation per day.",
    )
    args = parser.parse_args()

    check_and_update(args.screen, args.dir, args.auto)
    logging.info(f"Script Finished")

    return


if __name__ == "__main__":
    main()
