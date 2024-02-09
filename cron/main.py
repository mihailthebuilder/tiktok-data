from fabric import Connection
import logging
from dotenv import load_dotenv
import os
from pathlib import Path


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )

    load_dotenv()

    log("connecting")
    c = Connection(host=os.environ["SERVER_IP"], user="root")

    log("copying files")
    copy_files(c)

    log("clearing containers and images")
    c.run("/root/cron/docker-clear.sh")

    log("building image")
    c.run("/root/cron/build-image.sh")

    log("setting up cron")
    c.run("/root/cron-setup.sh")


def copy_files(c: Connection):
    script_path = Path.cwd().parent
    log(script_path)

    script_path_dirs = [
        # "chrome_profile",
        ".env",
        "build-image.sh",
        # "docker-clear.sh",
        "Dockerfile",
        "main.py",
        "requirements.txt",
        "run-container.sh",
        "cron-setup.sh",
    ]

    c.run("mkdir -p /root/cron")

    for dir in script_path_dirs:
        c.put(script_path / dir, "/root/cron")


def log(log: object):
    logging.info(log)


if __name__ == "__main__":
    main()
