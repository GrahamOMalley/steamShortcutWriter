#! /usr/bin/env python
import argparse

parser = argparse.ArgumentParser(description='Prints out all episodes for a given show')
parser.add_argument('-f', '--nogui', action="store_true", default=True, required=False, help='If adding ps2 game, start pcsx2 in nogui mode')
parser.add_argument('-g', '--game', type=str, required=True, help='Name of game to add')
args = parser.parse_args()


ps2exe = "C:\Program Files (x86)\PCSX2 1.0.0\pcsx2-r5350.exe"
ps2sd = "C:\Program Files (x86)\PCSX2 1.0.0"
game = args.game
isopath = "E:\Games\Emulators\PS2\\"

recList = []

def bytes_from_file(filename):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read()
            if chunk:
                for b in chunk:
                    yield b
            else:
                break

def readShortcuts():

    parseRow= True
    parseKey = False
    parseValue = False
    record = 0
    d = {}
    keybuf = ""
    valbuf = ""

    for b in bytes_from_file('shortcuts.vdf'):

        # seeking record
        if(parseRow and (b == '\b')):
            parseRow = False
            recList.append(dict(d))
            d.clear()
            continue
        
        # parsing
        if(parseKey):
            if(b == '\00'):
                parseKey = False
                parseValue = True
            else:
                keybuf += b
            continue

        if(parseValue):
            if(b == '\00'):
                parseValue = False
                # add key+val+record to dict, clear buffers, 
                if keybuf in ("AppName", "Exe", "StartDir", "0"):
                    if(keybuf == "0"): keybuf = "Category"
                    d[keybuf] = valbuf
                keybuf = ""
                valbuf = ""
            else:
                valbuf += b
            continue
                
        if (b == '\01'):
            parseKey = True
            if(parseRow == False):
                parseRow = True
                record = record+1
                print "record number: ", record

            continue

def writeNewShortcuts():
    out = ""
    r = 0
    # header
    out += "\00shortcuts\00"
    # list of shortcuts
    for s in recList:
        out += "\00" + str(r) + "\00" + "\01AppName\00" + s['AppName'] + "\00"
        out += "\01Exe\00" + s['Exe'] + "\00"
        out += "\01StartDir\00" + s['StartDir'] + "\00"
        out += "\01icon\00\00\00tags\00"
        if s.has_key('Category'):
            out += "\01" + str(0) + "\00" + s['Category'] + "\00"
        out += "\b\b"
        r+=1
    # footer
    out += "\b\b"

    outfile = open('output', 'wb')
    outfile.write(out)


def enqoute(s):
    return "\"" + s + "\""

try:
    readShortcuts()
except: # TODO catch an actual exception you dummy
    print "There was a problem reading the shortcuts file"

# add new entries
e = {}
e['AppName'] = game
e['Exe'] = enqoute(ps2exe) + " " + enqoute(isopath + game + "\\" + game + ".iso") + " --cfgpath=" + enqoute(isopath + game + "\\" + "inis") +" --nogui --fullscreen"
e['StartDir'] = enqoute(ps2sd)
e['Category'] = "Emulator"
print isopath
print e
recList.append(dict(e))

writeNewShortcuts()
