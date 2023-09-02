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
import requests

from subprocess import Popen

from dotenv import dotenv_values

d_level = { "debug": 10, "info": 20, "warning": 30, 
            "error": 40, "critical": 50 }
MSGDIR = "/tmp"

def handler(signum, frame):
    if signum == signal.SIGINT:
        res = input("Ctrl-C is pressed. Do you want to exit? (y/n) ")
        if res == 'y':
            logging.debug(f"clean up diskpatrol temp files")
            try:
                for f in glob.glob(f"{MSGDIR}/diskpatrol-*"):
                    os.unlink(f)
            except Exception as e:
                logging.exception(e)
            sys.exit(0)
    if signum == signal.SIGHUP:
        logging.info("Received SIGHUP. Reload config file.")
        pass

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)

def send_telegram(msg: str, token: str, chatid: str) -> None:
    s_url = f"https://api.telegram.org/bot{token}/sendMessage"
    logging.debug(s_url)
    try:
        response = requests.post(s_url, json={'chat_id': chatid, 'text': msg})
        logging.debug(response.text)
        logging.debug("Sent telegram alert.")
    except Exception as e:
        logging.error(e)

def humanize(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def app(d_vars: dict, parser, config: dict) -> None:
    """diskpatrol application"""
    s_prog = parser.prog
    s_fqdn = socket.getaddrinfo(socket.gethostname(), 0, 
            flags=socket.AI_CANONNAME)[0][3]
    s_sender = f'diskpatrol@{s_fqdn}'
    l_recipients = config['RECIPIENT_EMAILS'].split(',')

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
            s_msgfile_prefix = MSGDIR + '/' + s_prog
            if os.path.basename(s_path):
                s_msgfile_prefix += s_path.replace('/', '-')
            else:
                s_msgfile_prefix += '-root'
            o_stat = shutil.disk_usage(s_path)
            i_used_percent = int(math.ceil(o_stat.used/o_stat.total*100))
            if i_used_percent >= d_thresholds['warning']:
                if i_used_percent >= d_thresholds['critical']:
                    s_level = 'critical'
                elif i_used_percent >= d_thresholds['error']:
                    s_level = 'error'
                else:
                    s_level = 'warning'
                s_msgfile = s_msgfile_prefix + '_' + s_level
                s_msg = f"The used space of {s_path} is above {s_level} " + \
                        f"level ({d_thresholds[s_level]}%).\n" + \
                        "used/total: " + \
                        f"{humanize(o_stat.used)}/{humanize(o_stat.total)}" + \
                        f" ({i_used_percent}% used)" + \
                        "\n\n" + \
                        f"Please delete some files in {s_path}."
                s_subject = f"DiskPatrol: {s_path} is above {s_level} level."
                s_log = s_msg.replace('\n', ' ')
                if s_level == 'critical':
                    logging.critical(s_log)
                elif s_level == 'error':
                    logging.error(s_log)
                else:
                    logging.warning(s_log)
                with open(s_msgfile, 'w') as f:
                    f.write(f"{s_subject}\n\n{s_msg}")
                if config['ENABLE_WALL'] == '1' and \
                    d_level[s_level] >= d_level[config['WALL_ALERT_LEVEL']]:
                    logging.debug("Send wall alert.")
                    s_wall_cmd = f"cat {s_msgfile} | wall -n"
                    o_proc = Popen(s_wall_cmd, shell=True)
                if config['ENABLE_EMAIL'] == '1' and \
                    d_level[s_level] >= d_level[config['EMAIL_ALERT_LEVEL']]:
                    s_emailcount = f"{s_msgfile_prefix}_{s_level}_emailcount"
                    if os.path.isfile(s_emailcount):
                        with open(s_emailcount, 'r') as f:
                            i_emailcount = int(f.read())
                    else:
                        # remove other level count files when level is changed.
                        logging.debug(f"Alert level is changed tp {s_level}")
                        logging.debug("Remove other level count files.")
                        if s_level == 'critical':
                            l_countfile = [
                                f"{s_msgfile_prefix}_warn_emailcount",
                                f"{s_msgfile_prefix}_error_emailcount"
                            ]
                        elif s_level == 'error':
                            l_countfile = [
                                f"{s_msgfile_prefix}_warn_emailcount",
                                f"{s_msgfile_prefix}_critical_emailcount"
                            ]
                        else:
                            l_countfile = [
                                f"{s_msgfile_prefix}_error_emailcount",
                                f"{s_msgfile_prefix}_critical_emailcount"
                            ]
                        for f in l_countfile:
                            os.unlink(f)
                        logging.debug(f"Create {s_emailcount}.")
                        with open(s_emailcount, 'w') as f:
                            f.write('1')
                        i_emailcount = 1
                    if i_emailcount > \
                        int(config['EMAIL_ALERT_COUNT']) + \
                        int(config['EMAIL_ALERT_SKIP']):
                        logging.debug("Reset the email alert count.")
                        with open(s_emailcount, 'w') as f:
                            f.write('1')
                        i_emailcount = 1
                    logging.debug(f"Email alert {i_emailcount} " + \
                                    f"out of {config['EMAIL_ALERT_COUNT']}")
                    if i_emailcount <= int(config['EMAIL_ALERT_COUNT']):
                        logging.debug("Send email alert.")
                        s_mail = f"From: {s_sender}\n" + \
                                f"To: {config['RECIPIENT_EMAILS']}\n" + \
                                f"Subject: {s_subject}\n\n" + \
                                s_msg
                        with smtplib.SMTP(host=config['SMTP_SERVER'],
                                port=int(config['SMTP_PORT'])) as smtp:
                            smtp.sendmail(s_sender, l_recipients, s_mail)
                    with open(s_emailcount, 'w') as f:
                        f.write(str(i_emailcount+1))
                if config['ENABLE_TELEGRAM'] == '1' and \
                    d_level[s_level]>=d_level[config['TELEGRAM_ALERT_LEVEL']]:
                    s_telegramcount = f"{s_msgfile_prefix}_{s_level}_" + \
                                        "telegramcount"
                    if os.path.isfile(s_telegramcount):
                        with open(s_telegramcount, 'r') as f:
                            i_telegramcount = int(f.read())
                    else:
                        # remove other level count files when level is changed.
                        logging.debug(f"Alert level is changed tp {s_level}")
                        logging.debug("Remove other level count files.")
                        if s_level == 'critical':
                            l_countfile = [
                                f"{s_msgfile_prefix}_warn_telegramcount",
                                f"{s_msgfile_prefix}_error_telegramcount"
                            ]
                        elif s_level == 'error':
                            l_countfile = [
                                f"{s_msgfile_prefix}_warn_telegramcount",
                                f"{s_msgfile_prefix}_critical_telegramcount"
                            ]
                        else:
                            l_countfile = [
                                f"{s_msgfile_prefix}_error_telegramcount",
                                f"{s_msgfile_prefix}_critical_telegramcount"
                            ]
                        for f in l_countfile:
                            os.unlink(f)
                        logging.debug(f"Create {s_telegramcount}.")
                        with open(s_telegramcount, 'w') as f:
                            f.write('1')
                        i_telegramcount = 1
                    if i_telegramcount > \
                        int(config['TELEGRAM_ALERT_COUNT']) + \
                        int(config['TELEGRAM_ALERT_SKIP']):
                        logging.debug("Reset the telegram alert count.")
                        with open(s_telegramcount, 'w') as f:
                            f.write('1')
                        i_telegramcount = 1
                    logging.debug(f"Telegram alert: {i_telegramcount} " + \
                                  f"out of {config['TELEGRAM_ALERT_COUNT']}")
                    if i_telegramcount <= int(config['TELEGRAM_ALERT_COUNT']):
                        logging.debug("Send telegram alert.")
                        if config['APITOKEN'] and config['CHATID']:
                            s_telegram = f"{s_sender}\n{s_subject}\n\n{s_msg}"
                            send_telegram(s_telegram, config['APITOKEN'],
                                config['CHATID'])
                        else:
                            logging.warning("APITOKEN and/or CHATID not set")
                    with open(s_telegramcount, 'w') as f:
                        f.write(str(i_telegramcount+1))
            else:
                s_log = f"The used space of {s_path} ({i_used_percent}%) " + \
                        f"is below warning level ({d_thresholds['warning']}%)"
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
    level = logging.DEBUG if d_vars['debug'] else d_level[config['LOGLEVEL']]
    logfile = d_vars['logfile'] if d_vars['logfile'] else config['LOGFILE']
    try:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=logfile,
            level=level)
    except Exception as e:
        logging.exception(e)
        parser.exit(1, message=str(e))
    app(d_vars, parser, config)

if __name__ == '__main__':
    main()
