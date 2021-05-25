import sys
import json
import libtmux
import re
from pathlib import Path

# need to install libtmux 
# Usage: tmux_afl_screens.py <config.json> <log_path>

names = []
master_name = re.compile(r'(?<=-M )\w+')
slave_name = re.compile(r'(?<=-S )\w+')

def main():
    if len(sys.argv) < 3:
        print ("Usage: tmux_afl_screens.py <config.json> <log_path>")
        exit()

    conf = ''
    with open(sys.argv[1]) as f:
        conf = json.load(f)
    
    for command in conf['instances']:          
        instance_name = ''
        if '-M ' in command:
            instance_name = master_name.search(command).group(0)
        if '-S ' in command:
            instance_name = slave_name.search(command).group(0)
        names.append(instance_name)
    
    tmux = libtmux.Server(colors=256)
    fuzz_session = tmux.find_where({ "session_name": conf['name'] })
    
    log_path = Path(sys.argv[2])
    logfile = log_path
    for name in names:
        if log_path.is_dir():
            logfile = log_path / Path(name + ".log")
            
        window = fuzz_session.find_where({ "window_name": name })
        pane = window.list_panes()[0]
        screenshot = pane.cmd('capture-pane', '-J', '-p', '-e').stdout
        with open(logfile, 'a') as f:
            for line in screenshot:
                line = line.replace('[1m[90m', ')0[1;90m') # magic escape-sequence before "process timing" in afl
                f.write(line + '\n')
                print(line)
            f.write('\n')

    
if __name__ == "__main__":
    main()
