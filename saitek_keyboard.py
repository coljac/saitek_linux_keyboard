import argparse
from collections import defaultdict
import subprocess
from subprocess import Popen, PIPE, CalledProcessError

names = "battery alternator avionics fuel deice pitot cowl panel beacon nav strobe taxi landing engine_off engine_l engine_r engine_both engine_start gear_up gear_down"

names_map = {}
config = {"verbose": False}


def log(s):
    if config["verbose"]:
        print(str(s))

for i, n in enumerate(names.split()):
    names_map[n] = 256 + i
    names_map[256+i] = n

def read_mapping(filename, skip_comments=True):
    with open(filename, "r") as f:
        lines = f.readlines()
    mapping = defaultdict(dict)

    if skip_comments:
        lines = [l.strip() for l in lines if not l.startswith("#")]
    for l in lines:
        x = l.split(",")
        if x[1] not in ["0", "1"]:
            print(f"Warning: state value {x[1]} may not be correct in line '{l}'")
        mapping[names_map[x[0]]][x[1]] = x[2]
    return mapping


def typestring(string):
    subprocess.call(["xdotool", "type", "--clearmodifiers", string])


def keystroke(key):
    subprocess.call(["xdotool", "key", "--clearmodifiers", key])


def handle_event(line, mapping):
    log(f"Raw event string: {line}")
    if (not "EV_KEY" in line) and ("time" in line):
        return
    toks = line.strip().split(" ")
    try:
        button = int(toks[7])
        state = toks[-1]
        log(f"Button code = {button}, with name '{names_map[button]}', set to state: {state}")
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
    parser = argparse.ArgumentParser(description="Saitek Flight Panel events to keystrokes")
    parser.add_argument('--verbose', action="store_true", help="Verbose logging of events")
    parser.add_argument('--show-mapping', action="store_true", help="Show mapping and quit")
    parser.add_argument('--device', type=str, default="/dev/input/event4", help="Device file: run evtest to find.")
    parser.add_argument('--mapping', type=str, default="mapping.csv", help="Mapping file")
    args = parser.parse_args()
    config['verbose'] = args.verbose

    cmd = f"evtest {args.device}"
    mapping = read_mapping(args.mapping)
    if args.show_mapping:
        for k, v in mapping.items():
            print(f"{names_map[k]}  --> {v}")
        return

    p = Popen(cmd, shell=True, stdout=PIPE, bufsize=1, universal_newlines=True)
    while True:
        line = p.stdout.readline()
        if not line: 
            break
        handle_event(line, mapping)


if __name__=="__main__":
    main()
