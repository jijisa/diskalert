import os
import sys
import glob
import math
import time
import shutil
import signal
import socket
import logging
import smtplib
import argparse

from subprocess import Popen

from dotenv import dotenv_values

def handler(signum, frame):
    if signum == signal.SIGINT:
        res = input("Ctrl-C is pressed. Do you want to exit? (y/n) ")
        if res == 'y':
            sys.exit(0)
    if signum == signal.SIGHUP:
        logging.info("Received SIGHUP. Reload config file.")
        pass

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)

def app(d_vars: dict, parser) -> None:
    """diskpatrol application"""
    s_prog = parser.prog
    s_fqdn = socket.getaddrinfo(socket.gethostname(), 0, 
            flags=socket.AI_CANONNAME)[0][3]
    s_sender = f'diskpatrol@{s_fqdn}'
    config = {
        **dotenv_values(d_vars['conffile']),
    }
    l_recipients = config['RECIPIENT_EMAILS'].split(',')
    level = logging.DEBUG if d_vars['debug'] else eval(config['LOGLEVEL'])
    logfile = d_vars['logfile'] if d_vars['logfile'] else config['LOGFILE']
    try:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=logfile,
            level=level)
    except Exception as e:
        logging.exception(e)
        parser.exit(1, message=str(e))

    if not os.path.isfile(d_vars['conffile']):
        s_msg = f"Error: cannot find the env file {d_vars['conffile']}\n"
        logging.error(s_msg)
        parser.exit(1, s_msg)

    d_thresholds = {
        'warning': int(config['WARNING']),
        'error': int(config['ERROR']),
        'critical': int(config['CRITICAL']),
    }
    
    while True:
        for s_path in config['PATHS'].split(','):
            s_msgfile_prefix = config['MSGDIR'] + '/' + s_prog
            if os.path.basename(s_path):
                s_msgfile_prefix += s_path.replace('/', '-')
            else:
                s_msgfile_prefix += '-root'
            o_stat = shutil.disk_usage(s_path)
            i_used_percent = int(math.ceil(o_stat.used/o_stat.total*100))
            if i_used_percent > d_thresholds['warning']:
                if i_used_percent > d_thresholds['critical']:
                    s_level = 'critical'
                elif i_used_percent > d_thresholds['error']:
                    s_level = 'error'
                else:
                    s_level = 'warning'
                s_msgfile = s_msgfile_prefix + '_' + s_level
                s_msg = f"The used space of {s_path} is above {s_level} " + \
                        f"level ({d_thresholds[s_level]}%).\n" + \
                        f"used%: {i_used_percent}%\n" + \
                        f"{o_stat.used}/{o_stat.total}\n\n" + \
                        f"Please delete some files in {s_path}."
                s_log = s_msg.replace('\n', ' ')
                if s_level == 'critical':
                    logging.critical(s_log)
                elif s_level == 'error':
                    logging.error(s_log)
                else:
                    logging.warning(s_log)
                with open(s_msgfile, 'w') as f:
                    f.write(s_msg)
                if config['ENABLE_WALL'] == '1':
                    s_wall_cmd = f'cat {s_msgfile} | wall'
                    o_proc = Popen(s_wall_cmd, shell=True)
                if config['ENABLE_EMAIL'] == '1':
                    s_subject = f"DiskPatrol: {s_path} is in {s_level} level."
                    s_mail = f"From: {s_sender}\n" + \
                            f"To: {config['RECIPIENT_EMAILS']}\n" + \
                            f"Subject: {s_subject}\n\n" + \
                            s_msg
                    with smtplib.SMTP(host=config['SMTP_SERVER'],
                            port=int(config['SMTP_PORT'])) as smtp:
                        smtp.sendmail(s_sender, l_recipients, s_mail)
            else:
                s_log = f"The used space of {s_path} is below warning level."
                logging.info(s_log)
                # clean up message files
                logging.debug(f"clean up {s_msgfile_prefix}_*")
                try:
                    for f in glob.glob(f"{s_msgfile_prefix}_*"):
                        os.unlink(f)
                except Exception as e:
                    logging.exception(e)
        time.sleep(int(config['SLEEP']))

def main():
    """Disk Patrol main program"""
    parser = argparse.ArgumentParser(
            prog='diskpatrol',
            allow_abbrev=False,
            description='Alert when disk used space is higher than thresholds',
            epilog='Thanks for using %(prog)s! :)',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug mode')
    parser.add_argument('-l', '--logfile', help='path to logfile')
    parser.add_argument('conffile', help='configuration file location')
    args = parser.parse_args()
    d_vars = vars(args)
    config = {
        **dotenv_values(d_vars['conffile']),
    }
    print(d_vars)
    print(config)
    app(d_vars, parser)

if __name__ == '__main__':
    main()
