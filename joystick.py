import argparse
from collections import defaultdict
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
import time
import datetime
from datetime import timedelta
import os

config = {"verbose": False}

def log(s):
    if config["verbose"]:
        print(str(s))

def read_mapping(filename, skip_comments=True):
    with open(filename, "r") as f:
        lines = f.readlines()
    mapping = defaultdict(dict)

    if skip_comments:
        lines = [l.strip() for l in lines if not l.startswith("#")]
    for l in lines:
        if len(l) == 0:
            continue
        x = l.split(",")
        button, value, action = x
        if value not in ["0", "1"]:
            print(f"Warning: state value {x[1]} may not be correct in line '{l}'")
        mapping[button][value] = action
    return mapping

def ismodified(config_file, last_loaded):
    ctime = datetime.datetime.fromtimestamp(os.path.getctime(config_file))
    stale = (ctime - last_loaded).total_seconds() > 0
    return stale

def typestring(string):
    subprocess.call(["xdotool", "type", "--clearmodifiers", string])


def keystroke(key, up=False, down=False):
    # subprocess.call(["xdotool", "key", "--clearmodifiers", key])
    # subprocess.call(["xdotool", "key", key])
    if down:
        subprocess.call(["xdotool", "keydown", "--clearmodifiers", key])
    if up:
        subprocess.call(["xdotool", "keyup", "--clearmodifiers", key])
    if not up and not down:
        subprocess.call(["xdotool", "key", key])



def handle_event(line, mapping):
    log(f"Raw event string: >{line.strip()}<")
    if (not "EV_KEY" in line) and (not "EV_ABS" in line): #and ("time" in line):
        return
    toks = line.strip().split(" ")
    try:
        evtype = toks[5][1:-2]
        button = toks[8][1:-2]
        state = toks[-1]
        log(f"{evtype}: Button code = {button}, set to state: {state}")
        try:
            key = mapping[button][state]
            log(f"Sending keystroke {key}")
            if not key.startswith("!"):
                keystroke(key)
            else:
                typestring(key[1:])
        except Exception as e:
            log(e)
    except Exception as e:
        log(e)

def main():
    parser = argparse.ArgumentParser(description="Joystick to xdotool mapper")
    parser.add_argument('--verbose', action="store_true", help="Verbose logging of events")
    parser.add_argument('--show-mapping', action="store_true", help="Show mapping and quit")
    parser.add_argument('--device', type=str, default="/dev/input/event4", help="Device file: run evtest to find.")
    parser.add_argument('--mapping', type=str, default="mapping.csv", help="Mapping file")
    args = parser.parse_args()
    config['verbose'] = args.verbose

    cmd = f"evtest {args.device}"
    mapping = read_mapping(args.mapping)
    last_loaded = datetime.datetime.now()

    if args.show_mapping:
        for k, v in mapping.items():
            for l, w in v.items():
                print(f"{k} - {l} --> {w}")
        return

    p = Popen(cmd, shell=True, stdout=PIPE, bufsize=1, universal_newlines=True)
    elapsed = 0
    then = time.time()
    while True:
        now = time.time() 
        line = p.stdout.readline()
        if not line: 
            break
        handle_event(line, mapping)
        if now - then > 5:
            if ismodified(args.mapping, last_loaded):
                mapping = read_mapping(args.mapping)
                last_loaded = datetime.datetime.now()
            then = now



if __name__=="__main__":
    main()
