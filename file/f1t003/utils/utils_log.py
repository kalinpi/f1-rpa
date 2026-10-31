import os
import json
import socket
import platform
from datetime import datetime, timezone
from config import config as cfg

def start_log():
    """Initialize the JSON log file for the current process run and save the initial values."""
    with open(cfg.JSON_LOG_PATH,"w") as file:
        json.dump({}, file)
    with open(cfg.JSON_LOG_PATH,"r+") as file:
        y = {
            "name": cfg.JSON_LOG_PATH,
            "description":"",
            "product_id":cfg.CFN,
            "status": "error",
            "stage":0,
            "mode": cfg.MODE,
            "start": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), 
            "stop":  datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), 
            "type": cfg.TYPE,
            "all_count": 0,
            "done": 0,
            "done_name":"",
            "done_tag": "",
            "host":socket.gethostname(),
            "ip" : socket.gethostbyname(socket.gethostname()), 
            "os" : platform.system()+" "+platform.release(), 
            "version": cfg.VERSION,
            "framework": cfg.FRAMEWORK,
        } 
        file.seek(0)
        json.dump(y, file)
        file.truncate()

def stage_to_log(stage):
    """Update the current stage """
    with open(cfg.JSON_LOG_PATH, "r+") as file:
        data = json.load(file)
        data["stage"] = str(stage)
        data["stop"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

def end_sucess_to_log():
    """ Mark the completion of the process as a success """
    with open(cfg.JSON_LOG_PATH, "r+") as file:
        data = json.load(file)
        data["stage"] = 5
        data["status"] = "success"
        data["stop"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

def end_error_to_log(desc):
    """ Log process error """
    with open(cfg.JSON_LOG_PATH, "r+") as file:
        data = json.load(file)
        data["status"] = "error"
        #if len(data["description"])>0:
        #   data["description"] = data["description"]+"|"+desc
        #else: 
        data["description"] = desc
        data["stop"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

def done_to_log(all_count="",done="",done_name="",done_tag=""):
    """Updates the progress of the process"""
    with open(cfg.JSON_LOG_PATH, "r+") as file:
        data = json.load(file)
        data["all_count"] = str(all_count)
        data["done"] = str(done)
        data["done_name"] = str(done_name)
        data["done_tag"] = str(done_tag)
        data["stop"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

def clean_log():
    """ Deletes an empty log file """
    with open(cfg.JSON_LOG_PATH, "r+") as file:
        data = json.load(file)
        if data["stop"] == data["start"]:
            file.close()  
            os.remove(cfg.JSON_LOG_PATH) 