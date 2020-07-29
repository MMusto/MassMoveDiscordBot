import os
from os import listdir
from os.path import isfile, join
mypath = "./"
mp3files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-3:] == "mp3" and f[0] != 'Ω']

for file in mp3files:
    os.rename(file, 'Ω' + file)