#!/usr/bin/python

import os
import pwd
import sys
import getopt
import ast

def main(argv):
    status = 0
    message = ''
    try:
        opts, args = getopt.getopt(argv,"hu:",["users="])
    except getopt.GetoptError:
        print 'check_users.py -u \'[[1, "name"]]\''
        sys.exit(3)

    if opts:
        for opt, arg in opts:
            if opt == '-h':
                print 'check_users.py -u \'[[1, "name"]]\''
                sys.exit()
            elif opt in ("-u", "--users"):
                users = arg
    else:
        print 'check_users.py -u \'[[1, "name"]]\''
        sys.exit(3)

    users = ast.literal_eval(users)

    for user in users:
        try:
            u = pwd.getpwuid( user[0] ).pw_name
            if u != user[1]:
                status = 2
                message += ' ' + user[1]
        except KeyError:
            status = 2
            message += ' ' + user[1]

    if status == 0:
        sys.stdout.write("OK - All users exists")
        sys.exit(0)
    else:
        sys.stdout.write("CRITICAL - The following user(s) don't exists: " + message)
        sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
