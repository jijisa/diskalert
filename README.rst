Disk Patrol
===========

This is a program to check disk space and alert
if the used space is above the configured threshold.

Here are the alert transports.

* Wall transport: send alert message to the logged-in users.
* Email transport: send alert message to the mail recipients.
* Telegram transport: send alert message to the telegram chat id.
* Slack transport: send alert message to the slack chaneel.

Build (Optional)
-----------------

If you want to build rpm package, install docker and run run.sh script.::

    $ ./run.sh -h
    USAGE: run.sh [-h] [-b] [-r] [debian|rocky|centos7]
    
     -h                             Display this help message.
     -b [debian|rocky|centos7]      Build diskpatrol.
     -r [debian|rocky|centos7]      Run into diskpatrol build env.

To build rpm package for rocky linux::

    $ ./run.sh -b rocky

Install
--------

For RHEL-based distro
+++++++++++++++++++++++

Install diskpatrol rpm package from the internal genesis file server.::

    $ sudo dnf -y install \
        http://192.168.151.110:8000/burrito/diskpatrol-0.2.0-1.el8.x86_64.rpm

Optionally, Install postfix rpm package from the internal genesis file server
if you want to use email transport.::

    $ sudo dnf -y install \
        http://192.168.151.110:8000/burrito/postfix-3.5.8-4.el8.x86_64.rpm

For Debian-based distro
++++++++++++++++++++++++

Install diskpatrol debian package from the internal genesis file server.::

    $ curl -LO http://192.168.151.110:8000/burrito/diskpatrol_0.2.0-1_amd64.deb
    $ sudo dpkg -i diskpatrol_0.2.0-1_amd64.deb

Optionally, Install postfix rpm package if you want to use email transport.::

    $ sudo apt update && sudo apt install postfix

Choose 'No configuration' when it asks the mail server configuration type.


Configure
----------

If there is /etc/postfix/main.cf, back it up to /etc/postfix/main.cf.bak.::

    $ sudo mv /etc/postfix/main.cf /etc/postfix/main.cf.bak

Edit /etc/postfix/main.cf.::

    $ sudo vi /etc/postfix/main.cf
    inet_interfaces = loopback-only
    myorigin = <host_fqdn>
    mydestination = 
    local_transport = error: local delivery disabled
    mynetworks = 127.0.0.0/8,[::1]/128
    smtpd_relay_restrictions = permit_mynetworks,reject

Restart postfix service.::

    $ sudo systemctl restart postfix.service

Edit /etc/diskpatrol.conf.

The configuration is self-explanatory. Read the comment and set the
configuration variables for your environment.

Restart diskpatrol service.::

    $ sudo systemctl restart diskpatrol.service

Operations
-----------

Check diskpatrol service is running.::

    $ sudo systemctl status diskpatrol.service

The diskpatrol log file is /var/log/diskpatrol.log
Check the diskpatrol log file.::

    $ tail -f /var/log/diskpatrol.log
    2023-08-30 21:29:53,956 INFO:The used space of / (33%) is below warning level (60%)
    2023-08-30 21:30:54,026 INFO:The used space of / (33%) is below warning level (60%)
    2023-08-30 21:31:54,060 INFO:The used space of / (33%) is below warning level (60%)
    2023-08-30 21:32:54,122 INFO:The used space of / (33%) is below warning level (60%)

If the used space is above one of thresholds, it will alert like this.

* Wall alert::

    DiskPatrol: / is above warning level.

    The used space of / is above warning level (30%). 
    used/total: 32.6GiB/100.0GiB (33% used)
                                                                           
    Please delete some files in /.

* Email alert::

    Date: Thu, 31 Aug 2023 16:37:35
    From: diskpatrol@bbeta-controller.cluster.local
    Subject: DiskPatrol: / is above warning level.
    
    The used space of / is above warning level (30%).
    used/total: 32.6GiB/100.0GiB (33% used)
    
    Please delete some files in /.

* Telegram alert::

    diskpatrol@bbeta-controller
    DiskPatrol: / is in warning level.
    
    The used space of / is above warning level (30%).
    used/total: 32.6GiB/100.0GiB (33% used)
    
    Please delete some files in /.

To add telegram alert, create a telegram bot.
Here is the guide how to create a telegram bot.

https://core.telegram.org/bots/features#botfather

You need to set APITOKEN and CHATID in /etc/diskpatrol.conf to send
telegram message.

