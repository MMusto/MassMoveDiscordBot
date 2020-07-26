import os
from os import listdir
from os.path import isfile, join
mypath = "./"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-3:] == "mp3"]

for file in onlyfiles:
    os.rename(file, 'Ω' + file)