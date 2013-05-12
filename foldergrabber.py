#!/usr/bin/env python

from bs4 import BeautifulSoup
from commands import getstatusoutput
import sys
import os
import yaml
import urllib

OK = 0
BASE_FOLDER_NAME = 'C:\\Documents and Settings\\Owner\\My Documents\\'
BASE_URL = 'https://my.mypcbackup.com/browse?did=0&crid=&vtype=device&path=%s&sroot=undefined&gdeep=0&showdeleted=0&sortby=name&share_key='
HOME_DIR = os.path.expanduser("~")

def get_location_from_header_file():
    header = open(os.path.join(HOME_DIR, "header.txt")).read()
    cleaned_up_lines = header.split('\r\n')[1:]
    cleaned_up_text = '\n'.join(cleaned_up_lines)
    location = yaml.load(cleaned_up_text)['location']
    return location

def get_folder_contents(folder_name):
    encoded_folder_name = urllib.quote_plus(folder_name)
    url = BASE_URL % encoded_folder_name
    cookie_path = os.path.join(HOME_DIR, "cookie.jar")
    header_path = os.path.join(HOME_DIR, "header.txt")
    cmd = "curl --cookie %s -s --cookie-jar %s "\
          "--dump-header %s '%s'"
    cmd %= (cookie_path, cookie_path, header_path, url)
    status, output = getstatusoutput(cmd)
    assert status == OK
    return output

def download_folder(folder_name, error_list=[], depth=0):
    """
    Recursively downloads a folder from mypcbackup.com
    """
    depth += 1
    html = get_folder_contents(folder_name)

    soup = BeautifulSoup(html)
    
    links = soup.find_all('a')
    
    for link in links:
        link_classes = link.get('class', [])
        url = link.get('href')
        if 'filebrowser-file' in link_classes:
            file_name = link.contents[0].strip()
	    file_name = file_name.replace("'", "")
            if not file_name:
                continue
            if os.path.isfile(file_name):
                continue
            print "file found:", file_name
            cookie_path = os.path.join(HOME_DIR, "cookie.jar")
            header_path = os.path.join(HOME_DIR, "header.txt")
            cmd = "curl -s --cookie %s --cookie-jar %s "\
                  "--dump-header %s 'https://my.mypcbackup.com/%s'"
            cmd %= (cookie_path, cookie_path, header_path, url)
            status = os.system(cmd)
            if status != OK:
                error_list.append([folder_name, file_name])
                continue

            assert status == OK
            location = get_location_from_header_file()
            cmd = "curl -s --cookie %s --cookie-jar %s '%s' > '%s'"
            cmd %= (cookie_path, cookie_path, location, file_name)
            try:
                status = os.system(cmd)
                if status != OK:
                    error_list.append([folder_name, file_name])
            except:
                error_list.append([folder_name, file_name])
        if 'filebrowser-folder' in link_classes:
            sub_folder_name = link.contents[0].strip()
            if ':' in sub_folder_name:
                continue
            if not sub_folder_name:
                continue
            new_full_folder_name = folder_name + sub_folder_name + '\\'
            print "folder found:", new_full_folder_name, depth
            if os.path.isdir(sub_folder_name):
                continue
            os.mkdir(sub_folder_name)
            os.chdir(sub_folder_name)
            try:
                error_list += download_folder(new_full_folder_name, error_list, depth)
            except:
                error_list.append([folder_name, 'could not download folder'])
                continue
            os.chdir('..')
    return error_list

def main():
    if not os.path.isdir("ROOT"):
        os.mkdir('ROOT')
    os.chdir('ROOT')
    error_list = download_folder(BASE_FOLDER_NAME)
    from pprint import pprint
    pprint(error_list)
    os.chdir('..')

if __name__ == "__main__":
    main()
