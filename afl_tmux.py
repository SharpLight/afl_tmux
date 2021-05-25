import sys
import json
import libtmux
import re

# need to install libtmux
# Usage: tmux_afl.py <config.json> <start.log>

commands = []
names = []

master_name = re.compile(r'(?<=-M )\w+')
slave_name = re.compile(r'(?<=-S )\w+')

def main():
    if len(sys.argv) < 2:
        print ("Usage: afl_tmux.py <config.json> <log_path>")
        exit()
    
    conf = ''
    with open(sys.argv[1]) as f:
        conf = json.load(f)
    for command in conf['instances']:
        if '-- ' not in command:
            command += ' -- ' + conf["commandline"]
        
        if '-i ' not in command:
            temp = command.split('-- ')
            command = temp[0] + '-i ' + conf["in"] + ' -- ' + temp[1]
        if '-o ' not in command:
            temp = command.split('-- ')
            command = temp[0] + '-o ' + conf["out"] + ' -- ' + temp[1]
            
        instance_name = ''
        if '-M ' in command:
            instance_name = master_name.search(command).group(0)
        if '-S ' in command:
            instance_name = slave_name.search(command).group(0)
        
        commands.append(command)
        names.append(instance_name)
        
    # "debug"
    for command in commands:
        print(command)
    print(names)
    
    tmux = libtmux.Server(colors=256)
    fuzz_session = tmux.new_session(session_name=conf['name'])

    i = 0
    for name in names:
        window = fuzz_session.new_window(attach=False, window_name=name)
        pane = window.list_panes()[0]
        pane.send_keys(commands[i], enter=True)
        
        if len(sys.argv) > 2:
            screenshot = pane.cmd('capture-pane', '-J', '-p', '-e').stdout
            with open(sys.argv[2], 'a') as f:
                for line in screenshot:
                    line = line.replace('[1m[90m', ')0[1;90m') # magic escape-sequence before "process timing" in afl
                    f.write(line + '\n')
                f.write('\n')
        
        i += 1

    
if __name__ == "__main__":
    main()
