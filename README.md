mypcbackup-pull
===============

A friend of mine subscribed to a windows-based backup service at
www.mypcbackup.com. After upgrading her computer from Windows XP to Ubuntu
Ringtail, I found that there was no way to retrieve her files from the service!
My son and I dashed off this Python script to recursively fetch all the files.
It's not any huge reverse-engineering project, but might save someone an hour.

Note that it is first necessary to log in to mypcbackup.com using curl to
create the cookie.jar file in the user's home directory before this script will
work.
