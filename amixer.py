import os
import popen2
import re

amixer_volline = re.compile('^  Front (Left|Right): Playback [0-9]{1,3} \[([0-9]{1,3})%\] \[.+dB\] \[(on|off)\]$')

def togglemute():
    def _ismute():        
        cmd = 'amixer get Master'
        (stdout, stdin, stderr) = popen2.popen3(cmd)
        for line in stdout:
            m = amixer_volline.match(line)
            if m is not None:
                if m.group(3) == 'on':
                    return False
                elif m.group(3) == 'off':
                    return True

    def _mute():
        cmd = 'amixer set Master mute'
        os.system(cmd)

    def _unmute():
        cmd = 'amixer set Master unmute'
        os.system(cmd)

    if _ismute():
        _unmute()
    else:
        _mute()

def voldown():
    def _curvol():
        cmd = 'amixer get Master'
        (stdout, stdin, stderr) = popen2.popen3(cmd)
        for line in stdout:
            m = amixer_volline.match(line)
            if m is not None:
                return int(m.group(2))

    def _newvol(curvol):
        newvol = curvol - 3
        if newvol < 0:
            newvol = 0
        return newvol

    def _set(newvol):
        cmd = 'amixer set Master ' + str(newvol) + '%'
        os.system(cmd)

    curvol = _curvol()
    newvol = _newvol(curvol)
    _set(newvol)

def volup():
    def _curvol():
        cmd = 'amixer get Master'
        (stdout, stdin, stderr) = popen2.popen3(cmd)
        for line in stdout:
            m = amixer_volline.match(line)
            if m is not None:
                return int(m.group(2))

    def _newvol(curvol):
        newvol = curvol + 3
        if newvol > 100:
            newvol = 100
        return newvol

    def _set(newvol):
        cmd = 'amixer set Master ' + str(newvol) + '%'
        os.system(cmd)

    curvol = _curvol()
    newvol = _newvol(curvol)
    _set(newvol)
