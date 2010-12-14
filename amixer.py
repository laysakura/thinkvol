import os
import popen2

def togglemute():
    def _ismute():        
        cmd = 'amixer get Master'
        (stdout, stdin, stderr) = popen2.popen3( cmd  )
        for line in stdout:
            if line.find('[on]') != -1:
                return False
            elif line.find('[off]') != -1:
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


    print('mute')

def voldown():
    print('down')

def volup():
    print('up')
