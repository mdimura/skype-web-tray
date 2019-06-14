#!/usr/bin/python3
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator, GObject
import signal
import subprocess
from subprocess import Popen
from threading import Thread
import time

class Indicator():
    def __init__(self):
        self.trayonly=False
        self.profilePath=os.getenv("HOME")+"/.web-skype"
        
        self.iconPath=self.profilePath+"/skype.svg"
        self.iconMissedPath=self.profilePath+"/skype_missed.svg"
        skypeURL='https://web.skype.com/'
        self.execCmd=["firefox","--new-instance", "--profile", self.profilePath, skypeURL]
        self.widCmd=["xdotool", "search", "--sync", "--name", "Skype - Mozilla Firefox"]
        self.minimizeCmd=['xdotool', 'windowminimize']
        self.showCmd=['xdotool', 'windowactivate']
        self.mapCmd=['xdotool', 'windowmap']
        self.unmapCmd=['xdotool', 'windowunmap']
        self.titleCmd=['xdotool', 'getwindowname']
        self.app='web skype'
        self.firefoxProc=None
        self.windowID=''
        self.updateInterval=3
        
        self.indicator = appindicator.Indicator.new(
            self.app, self.iconPath,
            appindicator.IndicatorCategory.COMMUNICATIONS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        
        Thread(target=self.checkLoop).start()
        
        self.checkRun()

    def create_menu(self):
        menu = gtk.Menu()
        
        cmdShow = gtk.MenuItem('Show skype')
        cmdShow.connect('activate', self.windowShow)
        menu.append(cmdShow)
        self.indicator.set_secondary_activate_target(cmdShow)
        
        #cmdMap = gtk.MenuItem('Map skype')
        #cmdMap.connect('activate', self.windowMap)
        #menu.append(cmdMap)
        
        #cmdUnmap = gtk.MenuItem('Unmap skype')
        #cmdUnmap.connect('activate', self.windowUnmap)
        #menu.append(cmdUnmap)
  
        exittray = gtk.MenuItem('Quit')
        exittray.connect('activate', self.stop)
        menu.append(exittray)
  
        menu.show_all()
        return menu

    def stop(self, source):
        os.killpg(os.getpgid(self.firefoxProc.pid), signal.SIGTERM)
        gtk.main_quit()
        
    def updateIcon(self, source=None):
        if self.windowID is None:
            return
        title = ' '
        try:
            title=subprocess.check_output(self.titleCmd + [self.windowID])
        except:
            pass
        if title[0]=='(':
            self.indicator.set_icon(self.iconMissedPath)
        else:
            self.indicator.set_icon(self.iconPath)

    def checkRun(self, source=None):
        isNotRunning=subprocess.call(["pgrep", "-f", ' '.join(self.execCmd)])
        if isNotRunning:
            self.firefoxProc=Popen(self.execCmd, shell=False, stdin=None, stdout=None, stderr=None)
            self.windowID=subprocess.check_output(self.widCmd)
            self.windowMinimize()
            if self.trayonly:
                self.windowUnmap()
    
    def checkLoop(self):
        while True:
            time.sleep(self.updateInterval)
            GObject.idle_add(self.checkRun,priority=GObject.PRIORITY_DEFAULT)
            GObject.idle_add(self.updateIcon, priority=GObject.PRIORITY_DEFAULT)
            if self.trayonly and self.isMinimized():
                self.windowUnmap()
    
    def windowShow(self, source=None):
        self.windowMap().wait()
        return Popen(self.showCmd + [self.windowID], shell=False, stdin=None, stdout=None, stderr=None)

    def windowMinimize(self, source=None):
        return Popen(self.minimizeCmd + [self.windowID], shell=False, stdin=None, stdout=None, stderr=None)
    
    def windowMap(self, source=None):
        return Popen(self.mapCmd + [self.windowID], shell=False, stdin=None, stdout=None, stderr=None)
    
    def windowUnmap(self, source=None):
        if self.isMinimized():
            self.windowShow().wait()
        return Popen(self.unmapCmd + [self.windowID], shell=False, stdin=None, stdout=None, stderr=None)
    
    def isMinimized(self):
        out=''
        try:
            out=subprocess.check_output(['xprop', '-id', self.windowID,'_NET_WM_STATE']).decode('utf-8')
        except:
            pass
        if '_NET_WM_STATE_HIDDEN' in out:
            return True
        return False

Indicator()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
gtk.main()
  
