#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

             _____ _____ _____    __    _           _
            |   __|  _  |     |__|  |  | |_ ___ ___| |_ _ _ ___
            |__   |   __|  |  |  |  |  | . | .'|  _| '_| | | . |
            |_____|__|  |_____|_____|  |___|__,|___|_,_|___|  _|
                                                           |_|

Keywords: python, tools, algorithms, spoj

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
# Dependencies:
# mechanize => http://pypi.python.org/pypi/mechanize/0.1.7b

import os
import sys
import glob
import getpass
import optparse
import time
import datetime

try:
    from mechanize import Browser
except ImportError:
    print "mechanize required but missing"
    sys.exit(1)
    

def getSolutions (path_prefix, path_proxy):
    global br, username, password

    # create a browser object
    br = Browser()

    # add proxy support to browser
    if len(path_proxy) != 0: 
        protocol,proxy = options.proxy.split("://")
        br.set_proxies({protocol:proxy})
    
    # let browser fool robots.txt
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; \
              rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)

    print "Enter yout SPOJ username :",
    username = raw_input()
    password = getpass.getpass()

    # authenticate the user
    print "Authenticating " + username
    br.open ("https://spoj.com/login")
    #br.select_form (name="login")
    #the form no longer is named "login" therefore to access it by id:
    formcount=0
    for frm in br.forms():  
    	if str(frm.attrs["id"])=="login-form":
    		break
  	formcount=formcount+1
    br.select_form(nr=formcount)
    
    br["login_user"] = username
    br["password"] = password

    # sign in for a day to avoid timeouts
    #br.find_control(name="autologin").items[0].selected = True
    #this attribute is missing in the new spoj format
    br.form.action = "https://www.spoj.com/login"
    response = br.submit()

    verify = response.read()
    if (verify.find("Authentication failed!") != -1):
        print "Error authenticating - " + username
        exit(0)

    # grab the signed submissions list
    print "Grabbing siglist for " + username
    siglist = br.open("https://www.spoj.com/status/" + username + "/signedlist")

    # dump first nine useless lines in signed list for formatting
    for i in xrange(9):
        siglist.readline()

    # make a list of all AC's and challenges
    print "Filtering siglist for AC/Challenge solutions..."
    mysublist = list()

    while True:
        temp = siglist.readline()

        if temp=='\------------------------------------------------------------------------------/\n':
            # reached end of siglist
            break

        if not len(temp) :
            print "Reached EOF, siglist format has probably changed," + \
                    " contact author."
            exit(1)

        entry = [x.strip() for x in temp.split('|')]

        if entry[4] == 'AC' or entry[4].isdigit():
            mysublist.append (entry)

    print "Done !!!"
    return mysublist

def downloadSolutions(mysublist):
    totalsubmissions = len(mysublist)
    
    print "Fetching sources into " + path_prefix
    progress = 0
    
    for entry in mysublist:
        existing_files = glob.glob(os.path.join(path_prefix, "%s-%s*" % \
                                                           (entry[3],entry[1])))

        progress += 1
        if len(existing_files) == 1:
            print "%d/%d - %s skipped." % (progress, totalsubmissions, entry[3])
        else:
            source_code = br.open("https://www.spoj.com/files/src/save/" + \
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
            timestamp = time.mktime(datetime.datetime.strptime(entry[2], "%Y-%m-%d %H:%M:%S").timetuple())
            os.utime(os.path.join(path_prefix, filename),(timestamp, timestamp))
            print "%d/%d - %s done." % (progress, totalsubmissions, filename)

    print "Created a backup of %d submission for %s" % \
                                                    (totalsubmissions, username)


if __name__=="__main__":

    parser = optparse.OptionParser()
    parser.add_option("-o", "--outputpath", default="./", type=str, help="Destination directory to store solutions")
    parser.add_option("-p", "--proxy", default = "", type = str, help = "Proxy , ex- http://username:password@proxy:port")

    (options, args) = parser.parse_args()
    path_prefix = options.outputpath 
    path_proxy = options.proxy   
    
    downloadSolutions(getSolutions(path_prefix, path_proxy))
