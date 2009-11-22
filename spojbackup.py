#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

             _____ _____ _____    __    _           _
            |   __|  _  |     |__|  |  | |_ ___ ___| |_ _ _ ___
            |__   |   __|  |  |  |  |  | . | .'|  _| '_| | | . |
            |_____|__|  |_____|_____|  |___|__,|___|_,_|___|  _|
                                                        |_|
                                    by Abhishek Mishra <ideamonk >< gmail.com >


Copyright (c) 2009, Abhishek Mishra
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the Secret Labs AB nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

try:
    import argparse
except ImportError:
    print "argparse required but missing"
    sys.exit(1)

try:
    from mechanize import Browser
except ImportError:
    print "mechanize is required but missing"
    sys.exit(1)
    
import getpass, os, glob


def getSolutions (path_prefix):
    br = Browser()
    
    # make me a browser that makes ass of robots.txt
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)

    print "Enter yout SPOJ username :",
    username = raw_input()
    password = getpass.getpass()

    # Authenticate the user
    print "Authenticating " + username
    br.open ("http://spoj.pl")
    br.select_form (name="login")
    br["login_user"] = username
    br["password"] = password
    # sign em up for a day for avoiding timeouts
    br.find_control(name="autologin").items[0].selected = True
    response = br.submit()

    verify = response.read()
    if (verify.find("Authentication failed!") != -1):
        print "Error authenticating - " + username
        exit(0)

    # grab the signed list of submissions
    print "Grabbing siglist for " + username
    siglist = br.open("https://www.spoj.pl/status/" + username + "/signedlist")

    # dump first 9 lines
    for i in xrange(9):
        crap = siglist.readline()

    # make a list of all AC's and challenges
    print "Filtering siglist for AC/Challenge solutions..."
    mysublist = list()

    while (1):
        temp = siglist.readline()
        
        if temp=='\------------------------------------------------------------------------------/\n':
            # reached end of siglist
            break

        if (len(temp)==0):
            print "Reached EOF, siglist format has probably changed," + \
                    " contact author."
            exit(1)
            
        entry = [x.strip() for x in temp.split('|')]
        
        if (entry[4] == 'AC' or entry[4].isdigit()):
            mysublist.append (entry)

    totalsubmissions = len(mysublist)

    print "Fetching sources into " + path_prefix
    progress = 0
    
    for entry in mysublist:
        existing_files = glob.glob(os.path.join(path_prefix, "%s-%s*" % \
                                                           (entry[3],entry[1])))

        progress += 1
        if (len(existing_files)>0):
            print "%d/%d - %s skipped." % (progress, totalsubmissions, entry[3])
        else:
            source_code = br.open("https://www.spoj.pl/files/src/save/" + \
                                                                       entry[1])
            header = dict(source_code.info())
            filename = ""
            try:
                filename = header['content-disposition'].split('=')[1]
                filename = entry[3] + "-" + filename
            except:
                filename = entry[3] + "-" + entry[1]
                
            fp = open( os.path.join(path_prefix, filename), "w")
            fp.write (source_code.read())
            fp.close
            print "%d/%d - %s done." % (progress, totalsubmissions, filename)

    print "Created a backup of %d submission for %s" % \
                                                    (totalsubmissions, username)


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="spojbackup",
            description = "Creates a backup of all your Submissions on SPOJ " +\
            "(Sphere Online Judge) http://spoj.pl in a desired place")

    parser.add_argument("-o", "--outputpath",default="./", type=str,
                              help="Directory to store all fetched solutions")

    args = parser.parse_args()

    getSolutions (args.outputpath)
    