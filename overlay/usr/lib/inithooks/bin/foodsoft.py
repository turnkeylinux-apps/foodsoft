#!/usr/bin/python
"""Set Foodsoft admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
 
"""

import os
import sys
import glob
import getopt
import inithooks_cache
import string
import subprocess

from executil import ExecError, system
from subprocess import Popen, PIPE

from dialog_wrapper import Dialog

APPS_PATH='/var/www/'
APP_DEFAULT_PATH=os.path.join(APPS_PATH, 'foodsoft')

def quote(s):
    return "'" + s.replace("'", "\\'") + "'"

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def popen(cmd, **kwargs):
    kwargs.setdefault('shell', True)
    kwargs.setdefault('cwd', APP_DEFAULT_PATH)
    kwargs.setdefault('env', {})
    kwargs['env'].setdefault('RAILS_ENV', 'production')
    kwargs['env'].setdefault('SECRET_KEY_BASE', os.environ['SECRET_KEY_BASE'])
    kwargs['env'].setdefault('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    return Popen(cmd, **kwargs)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Foodsoft Password",
            "Enter new password for the Foodsoft 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Foodsoft Email",
            "Enter email address for the Foodsoft 'admin' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    print "Please wait ..."

    # need mysql running for these updates
    popen('service mysql status >/dev/null || service mysql start').wait()

    # initialize admin account from Rails console
 
    runner_script = """ "
       u = User.where(id: 1).first;
       u.password = '%s';
       u.email = '%s';
       u.save! " """ % (password, email)
    
    popen("bundle exec rails r %s" % runner_script).wait()

    # running as root may have cached classes
    popen('chown -R www-data:www-data tmp/').wait()

    popen('/etc/init.d/apache2 restart')


if __name__ == "__main__":
    main()

