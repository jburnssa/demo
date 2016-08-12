#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Date created:8/19/12
Last update: 8/17/14
version 013
Author: JB

version change in 13, invalid characters in file name.

version change from 010, trying to fix deletion bug.

This was written to rip files from a website. 

It will parse the website URL and look for the name of the file and id.
It will then use the id to build the page the video is on.
It will search the video page for the video and download to the run directory.
It will find the video size and download it to a specified location, if doesn't exist or if incomplete.

Possiblities for this version could implement: 
logger status bar (low return more just for fun)
http://stackoverflow.com/questions/3118059/how-to-write-custom-python-logging-handler

Get videos from more than the main page

Add the id to the beggining of the file name.  When searching if a file exists, search for the name without the id to support older files.

"""

import os
import sys
import csv
import urllib2
import urllib
import time #JB Need to introduce a small delay while testing, can remove this lib later
import traceback
import shutil
from log_01 import logger as log
import string

#eclipse will toggle how the progress is displayed on the screen.
eclipse = True

class get_info:
    """
    This class will 
    """
    def __init__(self, url):
        log.debug("Debug logging enabled")

    def get_ids(self, url, line_to_find = '<div class="video">'):
        """
        This method take a url, open it with urlopen, and find links to videos.
        
        return ids
        type    dictionary
        description key = id of video; value = title
        """
        line_to_find ='class="video-thumb"'
        results=urllib2.urlopen(url)
        x=0
        lines = results.readlines()
        #print lines
        ids = {}
        for l in range(0, len(lines)): 
            #print lines[l]
            if line_to_find in lines[l]:
                log.debug("The line is"+lines[l+1])
                #
                #<a href="/295750" title="Cara Swank is moist and tight" class="video-thumb" >
                #<span class="video-duration" onclick="window.location.href ='/295750'">11:02</span>
                #<img title="Cara Swank is moist and tight" id="0295750" class="te lazy " data-src="http://mimg01.redtubefiles.com/m=eGJF8f/_thumbs/0000295/0295750/0295750_009i.jpg" src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" alt="Cara Swank is moist and tight" />
                
                #Example of a line: <a href="/241128" title="this is the title" >
                temp_line = lines[l+1].split('=')
                print temp_line
                id = temp_line[1].split('/')[1].split('"')[0]
                title = temp_line[2].split('"')[1]
                log.debug("The title is %s and the id is %s"%(title,id))
                ids[id]=title.rstrip()
        return ids    

    def get_video_url(self, url, title):
        results=urllib2.urlopen(url)
        for line in results.readlines():
            if "source src=" in line:
                #print line
                #TODO:Video URL looks like it will get defined twice, 
                #the second is the correct syntax, this will work for now, but could break
                video_url = line.split('"')[1]
                #print line.split('"')[1]
        return video_url

    def download_video(self,video_url, file_name, destination_location):
        """
        video_url
            url to the video
            string
        file_name
            name of the file from the site
            string
        destination_location
            local location where to download file
            string
        """
        u = urllib2.urlopen(video_url) 
        #f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_mb = file_size/(1024*1024.0) 

        if self.check_if_full_file_downloaded(file_name,destination_location,file_size_mb ):
            print "File already exists at approriate size, skipping to next file!"
            print "************************************"
            return
        
        file_name = destination_location+ os.sep + file_name
        f = open(file_name, 'wb') 
        log.debug("Downloading: %s Bytes: %s" % (file_name, file_size))

        file_size_dl = 0 
        block_sz = 8192 
        tmp_size = 0
        while True: 
            buffer = u.read(block_sz)
            if not buffer: 
                break 
            file_size_dl += len(buffer) 
            f.write(buffer) 
            #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            #JB ++Try to convert to MB on screen
            status = r"%10d  [%3.2f%%]" % (file_size_dl/(1024*1024.0), file_size_dl * 100. / file_size)
            #JB end convert 
            status = status + chr(8)*(len(status)+1) 
            if eclipse:
                if int(file_size_dl/(1024*1024.0))> tmp_size:
                    print status +"\r"
                    tmp_size += 1
            else:                
                print status, 
        f.flush()
        f.close()
        f = None
        return

    def check_if_full_file_downloaded(self, file_name, directory, size):
        """
        file_name 
            name of file from server that we will check and see if exists
            string
        directory
            local directory where we will see if file exists
        size 
            size of file on the server
            cached_file_size/(1024*1024.0) convert to MB
            string/int?
        """
        filename = directory + os.sep+file_name
        if  os.path.exists(filename):
            print "The file %s exists"
            log.debug("File name= %s"%file_name)
            file_size = os.path.getsize(filename)
            file_size_mb =file_size/(1024*1024.0) 
            print "The current file size is %sMB and the server file size is %sMB"%(file_size_mb,size)
            if file_size_mb < size:
                print "WARNNING: It looks like we have an incomplete file."
                print "Will try to download the remaining file"
                return False
            else:
                return True
        else:
            log.debug("%s not found locally.  Will try to download."%file_name)
            return False

if __name__ == "__main__":
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    
    current_directory = os.getcwd()
    os.chdir("..")
    directory_name = "videos_2"
    destination_location = os.getcwd()+os.sep+directory_name
    if  not os.path.exists(destination_location):
        os.makedirs(destination_location, mode=0777)
    os.chdir(current_directory)    
    
    url = "http://www.redtube.com/"
    rt = get_info(url)
    ids = rt.get_ids(url)
    x = 1
    print ids
    for id in ids:
        log.info("%s of %s"%(str(x),len(ids)))
        video_url = rt.get_video_url(url+id, ids[id])
        file_name = ids[id]+".flv"
        print file_name
        ''.join(c for c in file_name if c in valid_chars)#version 13 change
        file_name = file_name.replace('/',' ')
        print file_name
        
        log.debug("FN = %s"%file_name)
        log.info("ID = %s"%id)
        log.debug("URL= %s"%video_url)
        
        rt.download_video(video_url, file_name, destination_location)
        log.info("Finished file %s of %s"%(str(x),len(ids)))
        log.debug("File %s" %file_name)
        x += 1
