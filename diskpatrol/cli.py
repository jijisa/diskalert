import os
import sys
import math
import time
import shutil
import signal
import logging
import argparse

from subprocess import Popen

from dotenv import dotenv_values

def handler(signum, frame):
    res = input("Ctrl-C is pressed. Do you want to exit? (y/n) ")
    if res == 'y':
        sys.exit(0)

signal.signal(signal.SIGINT, handler)

def app(d_vars: dict) -> None:
    """diskalert application"""
    try:
        o_level = logging.DEBUG if d_vars['debug'] else logging.INFO
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=d_vars['logfile'],
            level=o_level)
    except Exception as e:
        logging.exception(e)
        parser.exit(1, message=str(e))

    if not os.path.isfile(d_vars['envfile']):
        s_msg = f"Error: cannot find the env file {d_vars['envfile']}\n"
        logging.error(s_msg)
        parser.exit(1, s_msg)

    config = {
        **dotenv_values(d_vars['envfile']),
    }
    
    d_thresholds = {
        'warn': int(config['WARN']),
        'error': int(config['ERROR']),
        'critical': int(config['CRITICAL']),
    }
    
    while True:
        o_stat = shutil.disk_usage(config['PARTITION'])
        i_used_percent = int(math.ceil(o_stat.used/o_stat.total*100))
        if i_used_percent > d_thresholds['warn']:
            if i_used_percent > d_thresholds['critical']:
                s_level = 'critical'
            elif i_used_percent > d_thresholds['error']:
                s_level = 'error'
            else:
                s_level = 'warn'
            s_msg_file = config['MSGDIR'] + '/diskalert_' + s_level
            s_msg = f'''
            The used space of root FS is above {s_level} threshold 
            ({d_thresholds[s_level]}%).
            Please delete some files in root FS.
            '''
            with open(s_msg_file, 'w') as f:
                f.write(s_msg)
            s_wall_cmd = f'cat {s_msg_file} | wall'
            o_proc = Popen(s_wall_cmd, shell=True)
        else:
            # remove a message file
            if os.path.isfile(s_msg_file):
                os.unlink(s_msg_file)
        time.sleep(int(config['SLEEP']))

if __name__ == '__main__':
    """Diskalert main program"""
    parser = argparse.ArgumentParser(
            prog='diskalert',
            allow_abbrev=False,
            description='Alert when disk used space is higher than thresholds',
            epilog='Thanks for using %(prog)s! :)',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug mode')
    parser.add_argument('-l', '--logfile', default='/var/log/diskalert.log',
            help='path to logfile')
    parser.add_argument('envfile', help='environment file location')
    args = parser.parse_args()
    d_vars = vars(args)
    print(d_vars)
    app(d_vars)
