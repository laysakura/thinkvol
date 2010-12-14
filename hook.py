#!/usr/bin/python
# 
# thinkVolume -- A volume controller for Lenovo ThinkPad T400s (TM)
# 
#    Copyright (C) 2010 Sho Nakatani <lay.sakura@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    This software uses most of the 'pyxhook.py' code in pykeylogger project.
#        http://sourceforge.net/projects/pykeylogger/
#    Thanks to Tim Alexander, and every developer in the project.


import sys
import re
import time
import threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

import amixer

#######################################################################
########################START CLASS DEF################################
#######################################################################

class HookManager(threading.Thread):
    """This is the main class. Instantiate it, and you can hand it KeyDown and KeyUp (functions in your own code) which execute to parse the pyxhookkeyevent class that is returned.

    This simply takes these two values for now:
    KeyDown = The function to execute when a key is pressed, if it returns anything. It hands the function an argument that is the pyxhookkeyevent class.
    KeyUp = The function to execute when a key is released, if it returns anything. It hands the function an argument that is the pyxhookkeyevent class.
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.finished = threading.Event()
        
        # Compile our regex statements.
        self.isvolume = re.compile('^\[26902504[1-3]\]$')
        
        # Assign default function actions (do nothing).
        self.KeyDown = lambda x: True
        
        self.contextEventMask = [X.KeyPress, X.ButtonPress]
        
        # Hook to our display.
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        
    def run(self):
        # Check if the extension is present
        if not self.record_dpy.has_extension("RECORD"):
            print "RECORD extension not found"
            sys.exit(1)
        r = self.record_dpy.record_get_version(0, 0)
        print "RECORD extension version %d.%d" % (r.major_version, r.minor_version)

        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
                0,
                [record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': tuple(self.contextEventMask), #(X.KeyPress, X.ButtonPress),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                }])

        # Enable the context; this only returns after a call to record_disable_context,
        # while calling the callback function in the meantime
        self.record_dpy.record_enable_context(self.ctx, self.processevents)
        # Finally free the context
        self.record_dpy.record_free_context(self.ctx)

    def cancel(self):
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
    
    def volumectl(self, keynum):
        if keynum == 269025042: # Mute/Unmute
            amixer.togglemute()
        elif keynum == 269025041: # Volume down
            amixer.voldown()
        elif keynum == 269025043: # Volume up
            amixer.volup()
    
    def HookKeyboard(self):
        pass
        # We don't need to do anything here anymore, since the default mask 
        # is now set to contain X.KeyPress
        #self.contextEventMask[0] = X.KeyPress
    
    def processevents(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print "* received swapped protocol data, cowardly ignored"
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.record_dpy.display, None, None)
            if event.type == X.KeyPress:
                keynum = self.keypressevent(event)
                self.KeyDown(keynum)

    def keypressevent(self, event):
        matchto = self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))
        if self.isvolume.match(matchto):
            keynum = self.local_dpy.keycode_to_keysym(event.detail, 0)
            return int(keynum)
        else:
            return -1           # Won't be used

    # need the following because XK.keysym_to_string() only does printable chars
    # rather than being the correct inverse of XK.string_to_keysym()
    def lookup_keysym(self, keysym):
        for name in dir(XK):
            if name.startswith("XK_") and getattr(XK, name) == keysym:
                return name.lstrip("XK_")
        return "[%d]" % keysym

    def xwindowinfo(self):
        try:
            windowvar = self.local_dpy.get_input_focus().focus
            wmname = windowvar.get_wm_name()
            wmclass = windowvar.get_wm_class()
            wmhandle = str(windowvar)[20:30]
        except:
            ## This is to keep things running smoothly. It almost never happens, but still...
            return {"name":None, "class":None, "handle":None}
        if (wmname == None) and (wmclass == None):
            try:
                windowvar = windowvar.query_tree().parent
                wmname = windowvar.get_wm_name()
                wmclass = windowvar.get_wm_class()
                wmhandle = str(windowvar)[20:30]
            except:
                ## This is to keep things running smoothly. It almost never happens, but still...
                return {"name":None, "class":None, "handle":None}
        if wmclass == None:
            return {"name":wmname, "class":wmclass, "handle":wmhandle}
        else:
            return {"name":wmname, "class":wmclass[0], "handle":wmhandle}

#######################################################################
#########################END CLASS DEF#################################
#######################################################################
    
if __name__ == '__main__':
    hm = HookManager()
    hm.HookKeyboard()
    hm.KeyDown = hm.volumectl
    hm.start()
    time.sleep(10)
    hm.cancel()
