# Saitek Linux keyboard emulation

This is not the world's most sophisticated piece of softwar, but it works. It's not actually proper keyboard emulation, but it does produce keystrokes with `xdotool`. 

While looking into various USB APIs in order to capture events from the Saitek Flight Switch Panel, I discovered that `evtest` displays events from the device just fine. So, rather than dive deeper down the USB specification I'm just reading stdout from this process and doing a simple mapping, then using `xdotool` to emulate keystrokes. 

Here's how to use this for yourself.

1. Run `/usr/bin/evtest` and ensure the device is there and working; it should look something like this:

```
$ evtest
No device specified, trying to scan all of /dev/input/event*
Not running as root, no devices may be available.
Available devices:
/dev/input/event2:      Thrustmaster T.Flight Hotas X
/dev/input/event3:      CH PRODUCTS CH PRO PEDALS USB 
/dev/input/event4:      Intretech Saitek Pro Flight Switch Panel
Select the device event number [0-4]: 
```
2. Either modify the script so that the correct device is specified (in my case, `/dev/input/event4`) or pass this in as an argument with `--device`.
3. Modify the `mapping.csv` so that your preferred keystrokes are in there. The format is `switch name,state,keystroke`. The switch names are in the python file and appended below. The possible states are "0" or "1" in every case. The keystrokes are strings passed to `xdotool`, so see the xdotool docs for more information. Quick hint: "A", "F5", "ctrl+c" do what you'd expect. You can run in verbose mode to experiment with these values.
4. Run the script as `python saitek_keymap.py`. `python saitek_keymap.py --verbose` will print debug info, `python saitek_keymap.py --show-mapping` will validate and display the results of parsing `mapping.csv`.

Button names:
```
battery
alternator
avionics
fuel
deice
pitot
cowl
panel
beacon
nav
strobe
taxi
landing
engine_off
engine_l
engine_r
engine_both
engine_start
gear_up
gear_down
```
