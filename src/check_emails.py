#!/usr/bin/python3
import subprocess
import configparser
import json
import logging.config
import os
from pathlib import Path
from datetime import datetime, timezone

from azure_client import get_or_create_credentials, get_all_emails_it

from settings import LOGGING

USER_SHARE_DIR = os.path.join(Path.home(), ".local/share/outlook-email-checker/")
USER_CONFIG_PATH = os.path.join(Path.home(), ".config/outlook-email-checker/config")

def get_recieved_emails(user_id,
                        folder_id,
                        client_id,
                        private_key,
                        scope,
                        tenant,
                        redirect_uri,
                        auth_filename,
                        additional_filter="",
                        first_download=True,
                        last_download_time=None,
                        last_emails_ids=None):
    auth = get_or_create_credentials(client_id=client_id,
                                     private_key=private_key,
                                     scope=scope,
                                     tenant=tenant,
                                     redirect_uri=redirect_uri,
                                     filename=auth_filename)
    mail_args = {"select": "id", "filter":""}
    if additional_filter != "":
        mail_args["filter"] += additional_filter + " and "
    retrieve_time = datetime.now(timezone.utc)
    if not first_download:
        mail_args["filter"] += "ReceivedDateTime ge {0}".format(str(last_download_time).replace(" ", "T"))
        if len(last_email_ids) != 0:
            mail_args["filter"] += " and id ne "
            mail_args["filter"] += " and id ne ".join(last_email_ids)
    else:
        mail_args["filter"] += "ReceivedDateTime ge {0}".format(str(retrieve_time).replace(" ", "T"))

    recieved_ids = []
    for emails in get_all_emails_it(auth, user_id, folder_id, **mail_args):
        recieved_ids += [mail["id"] for mail in emails]

    return retrieve_time, recieved_ids

def get_config():
    config = configparser.ConfigParser()
    config["config"] = {}
    config["config"]["hook"] = os.path.join(USER_SHARE_DIR, "hook/")
    config["config"]["last_data"] = os.path.join(USER_SHARE_DIR, "last_data.json")
    config["config"]["user_id"] = "me"
    config["config"]["folder_id"] = "Inbox"
    config["config"]["filter"] = ""
    if os.path.isfile(USER_CONFIG_PATH):
        config.read(USER_CONFIG_PATH)
    else:
        raise IOError("Please create a local configuration file at {0} take /etc/outlook-email-checker/config as example".format(USER_CONFIG_PATH))

    return config

if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)

    config = get_config()
    user_id = config["config"]["user_id"]
    folder_id = config["config"]["folder_id"]
    additional_filter = config["config"]["filter"]
    client_id = config["auth"]["client_id"]
    private_key = config["auth"]["private_key"]
    scope = config["auth"]["scope"]
    tenant = config["auth"]["tenant"]
    redirect_uri = config["auth"]["redirect_uri"]
    auth_filename = config["auth"]["filename"]
    last_data_path = config["config"]["last_data"]
    hook_dir = config["config"]["hook"]

    if os.path.isfile(last_data_path):
        first_download = False
        with open(last_data_path, 'r') as f:
            dat = json.load(f)
        last_download_time = datetime.strptime(dat["last_download_time"], "%Y-%m-%d %H:%M:%S.%f%z")
        last_emails_ids = dat["last_emails_ids"]
    else:
        first_download = True
        last_download_time = None
        last_emails_ids = None

    retrieve_time, recieved_ids = get_recieved_emails(user_id,
                                                      folder_id,
                                                      client_id,
                                                      private_key,
                                                      scope,
                                                      tenant,
                                                      redirect_uri,
                                                      auth_filename,
                                                      additional_filter,
                                                      first_download,
                                                      last_download_time,
                                                      last_emails_ids)
    with open(last_data_path, 'w') as f:
        f.write(json.dumps({"last_download_time": retrieve_time, "last_emails_ids": recieved_ids}))
    subprocess.run([os.path.join(hook_dir, "email_received")] + recieved_ids)
