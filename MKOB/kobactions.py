"""

kobactions.py

Defines actions for MKOB

"""

##import tkinter as tk
import tkinter.messagebox as mb
from pykob import kob, internet, morse
from pykob import log  # TEMP
import kobconfig as kc
import stationlist as sl
import time

import pykob  # for version number
print('PyKOB ' + pykob.VERSION)

kw = None  # initialized by KOBWindow
mySender = None
myReader = None
myInternet = None
##running = True
connected = False

def internetCallback(code):
    if connected:
        myKOB.sounder(code)
        myReader.decode(code)

nChars = 0
def readerCallback(char, spacing):
    global nChars  # TEMP
##    if spacing > 50:
##        print('\n>', end='')
##    elif spacing > 0.5:
##        print(' ', end='')
##    print(char, end='', flush=True)
    if spacing > 0.5:
        kw.txtReader.insert('end', ' ')
    kw.txtReader.insert('end', char)
    nChars += 1
    if nChars >= 5:
##        print(kw.txtReader['height'])
##        kw.txtReader.see('end-1c')
        kw.txtReader.see('end')
        kw.txtReader.update_idletasks()
        nChars = 0

myKOB = kob.KOB(port=kc.Port, audio=kc.Audio, callback=None)
myInternet = internet.Internet(officeID=kc.OfficeID, callback=internetCallback)

# File menu

def doFileNew():
    kw.txtKeyboard.delete('1.0', tk.END)

def doFileOpen():
##    newFile()
    kw.txtKeyboard.insert(tk.END, '~  Now is the time for all good men to come to the aid of their country.  +')
    kw.txtKeyboard.mark_set('mark', '0.0')
    kw.txtKeyboard.mark_gravity('mark', tk.LEFT)
    kw.txtKeyboard.tag_config('highlight', underline=1)
    kw.txtKeyboard.tag_add('highlight', 'mark')

def doFileExit():
    kw.root.destroy()
    kw.root.quit()

# Help menu

def doHelpAbout():
    mb.showinfo(title='About', message=kw.VERSION)

def doWPM(event=None):
    global mySender, myReader
##    print('doWPM')  # TEMP
    try:
        wpm = int(kw.spnWPM.get())
        mySender = morse.Sender(wpm=wpm, cwpm=kc.CWPM,
                codeType=kc.CodeType, spacing=kc.Spacing)
        myReader = morse.Reader(wpm=wpm, codeType=kc.CodeType,
                callback=readerCallback)
    except:
        log.err('doWPM')  # TEMP
        pass

def doConnect():
    global connected
    connected = not connected
    color = 'red' if connected else 'white'
    kw.cvsConnect.create_rectangle(0, 0, 20, 20, fill=color)
    if connected:
        myInternet.connect(int(kw.spnWireNo.get()))
    else:
        myInternet.disconnect()

##def codeSender():
##    while running:
##        if kw.txtKeyboard.compare('mark', '<', tk.END) and \
##                kw.varCodeSenderOn.get():
##            c = kw.txtKeyboard.get('mark')
##            code = mySender.encode(c)
##            myKOB.sounder(code)
##            kw.txtKeyboard.tag_remove('highlight', 'mark')
##            kw.txtKeyboard.mark_set('mark', 'mark+1c')
##            kw.txtKeyboard.mark_gravity('mark', tk.LEFT)
##            kw.txtKeyboard.tag_add('highlight', 'mark')
##        else:
##            time.sleep(0.1)

def note(txt):
    kw.txtReader.insert(tk.END, '\n<' + txt + '>')
