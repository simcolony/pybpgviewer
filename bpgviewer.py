#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple BPG Image viewer.

Copyright (c) 2014-2018, Alexey Simbarsky
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from sys import argv,exit,version_info
from os import listdir,access,R_OK,stat,close,remove
from os.path import exists,isfile,isdir,dirname,basename,realpath,join,abspath
from tempfile import mkstemp
from shutil import copyfile
from subprocess import Popen,PIPE,STDOUT
from math import floor
from struct import unpack
from platform import system
from threading import Thread,Lock
import locale,pickle,base64,zlib

if system()=="Windows":
    osflag=False
    from subprocess import STARTUPINFO
else:
    osflag=True
    from os import mkfifo,O_RDONLY,O_NONBLOCK
    from os import open as osopen
    from os import read as osread
    from os import close as osclose
    import errno

wxapp=False

class translator():
    def __init__(self):
        self.voc={}
        self.locale=locale.getdefaultlocale()
    def find(self,key):
        try: wxu=True if wx.VERSION[0]>3 else False
        except: wxu=False
        if key in self.voc:
            if self.locale[0] in self.voc[key]:
                if wxu: return self.voc[key][self.locale[0]]
                else:
                    return self.voc[key][self.locale[0]].encode(\
                        self.locale[1])
        return key

t=translator()

def load_voc(str):
    if version_info[0]>2:
        return pickle.loads(zlib.decompress(base64.decodestring(\
            bytes(str,'utf-8'))))
    else:
        return pickle.loads(zlib.decompress(base64.decodestring(str)))

t.voc=load_voc("\
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\
1UX/+F9G8wii\
")

def _(s):
    return t.find(s)

def __(s,codepage):
    if version_info[0]<3:
        if type(s) is unicode: s=s.encode(codepage)
    return s

def errmsg(msg):
    if osflag:
        try:
            f=Popen(['notify-send',msg],False,stdin=None,stdout=None,\
            stderr=None)
            f.wait()
        except:
            try:
                f=Popen(['xmessage',msg],False,stdin=None,stdout=None,\
                    stderr=None)
                f.wait()
            except: pass
    else:
        import ctypes
        MessageBox=ctypes.windll.user32.MessageBoxA
        MessageBox(0,msg,_('Error!'),16)

if not(osflag):
    try: import win32file,win32pipe
    except:
        msg=_("Please install")+" Python for Windows Extensions\n\
(http://sourceforge.net/projects/pywin32/)!"
        errmsg(msg)
        raise RuntimeError(msg)
    
try: import wx
except:
    msg=_("Please install")+" wxPython 2.8 ("+_("or higher")+\
        ") (http://www.wxpython.org/)!\n"+\
        _("Under Debian or Ubuntu you may try")+":\n"\
        "sudo aptitude install python-wxgtk2.8\n"+_("or")+"\n"+\
        "sudo aptitude install python-wxgtk3.0"
    errmsg(msg)
    raise RuntimeError(msg)

try:
    from PIL import Image
    from PIL.Image import core as _imaging
except:
    msg=_("Please install")+" Python Imaging Library (PIL) 1.1.7 ("+\
        _("or higher")+") (http://www.pythonware.com/products/pil/)\n"+\
        _("or")+" Pillow 3.2.0 ("+_("or higher")+\
        ") (https://pillow.readthedocs.org/en/3.2.x/)!\n"+\
        _("Under Debian or Ubuntu you may try")+":\n"\
        "sudo aptitude install python-imaging\n"+_("or")+"\n"+\
        "sudo aptitude install python-pil"
    errmsg(msg)
    raise RuntimeError(msg)

from wx.lib.embeddedimage import PyEmbeddedImage

bpglogo=PyEmbeddedImage(
    "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"
    "P7EZ5A4mdx+jAAAAAElFTkSuQmCC")

def errmsgbox(msg):
    if not(wxapp): app=wx.App(0)
    print(msg)
    wx.MessageBox(msg,_('Error!'),wx.OK|wx.ICON_ERROR)
    if not(wxapp): app.Exit()

def bpggetcmd():
    binname='bpgdec'
    if not osflag: binname+='.exe'
    bpgpath=join(dirname(realpath(argv[0])),binname)
    if not(isfile(bpgpath)):
        msg=_('BPG decoder not found!\n')
        errmsgbox(msg)
        exit()
    return bpgpath

class GenBitmap(wx.Panel):
    def __init__(self,parent,ID,bitmap,pos=wx.DefaultPosition,
            size=wx.DefaultSize,style=0):
        if not style & wx.BORDER_MASK: style=style|wx.BORDER_NONE
        wx.Panel.__init__(self,parent,ID,pos,size,style)
        self._bitmap=bitmap
        self._clear=False
        self.SetInitialSize(size)
        self.Bind(wx.EVT_ERASE_BACKGROUND,lambda e: None)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
    def SetBitmap(self,bitmap):
        self._bitmap=bitmap
        self.SetInitialSize((bitmap.GetWidth(),bitmap.GetHeight()))
        self.Refresh()
    def GetBitmap(self): return self._bitmap
    def OnPaint(self, event):
        dc=wx.PaintDC(self)
        if self._clear: dc.Clear()
        if self._bitmap:
            dc.DrawBitmap(self._bitmap,0,0,True)
        self._clear=False

class DecodeThread(Thread):
    def __init__(self,parent,func):
        Thread.__init__(self)
        self.parent=parent
        self.func=func
    def run(self):
        if self.parent.dlock.acquire(False):
            self.func()
            self.parent.dlock.release()

SE_EVT_TYPE=wx.NewEventType()
SE_EVT_BNDR=wx.PyEventBinder(SE_EVT_TYPE,1)
class ShowEvent(wx.PyCommandEvent):
    def __init__(self,etype,eid,value=None):
        wx.PyCommandEvent.__init__(self,etype,eid)
        self.value=value

class FileDropTarget(wx.FileDropTarget):
    def __init__(self,obj):
        wx.FileDropTarget.__init__(self)
        self.obj=obj
    def OnDropFiles(self,x,y,filenames):
        self.obj.showempty()
        self.obj.index=0
        self.obj.filelist=[]
        self.obj.showimage(self.obj.checkpath(filenames[0]))
        return True

class DFrame(wx.Frame):
    def bpgdecode(self,filename):
        msg=None
        cmd=self.bpgpath+' -o '
        if self.img:
            del self.img
            self.img=None
        if len(filename)>4 and filename[-4:].lower()=='.bpg':
            try:
                if not(isfile(filename) and access(filename,R_OK)):
                    msg=_('Unable to open')+'\"%s\"!'%filename
            except: return False
            if not(msg):
                err=0
                try:
                    imbuffer=''
                    if osflag:
                        fifo=osopen(self.fifo,O_RDONLY|O_NONBLOCK)
                        cmd+=self.fifo+' "'+realpath(filename)+'"'+\
                            ' >/dev/null 2>&1'
                        f=Popen(cmd,shell=True,stdin=None,stdout=None,\
                            stderr=None)
                        if fifo:
                            while True:
                                if f.poll()!=None: break;
                                try: data=osread(fifo,16777216)
                                except OSError as e:
                                    if e.errno==errno.EAGAIN or\
                                        e.errno==errno.EWOULDBLOCK: data=''
                                    else: raise
                                if len(data): imbuffer+=data
                            osclose(fifo)
                    else:
                        si=STARTUPINFO()
                        si.dwFlags|=1
                        si.wShowWindow=0
                        pname='\\\\.\\pipe\\'+basename(self.fifo)
                        tpipe=win32pipe.CreateNamedPipe(
                            pname,
                            win32pipe.PIPE_ACCESS_DUPLEX,
                            win32pipe.PIPE_TYPE_BYTE|win32pipe.PIPE_WAIT,
                            1,16777216,16777216,2000,None)
                        cmd+=pname+' "'+realpath(filename)+'"'
                        f=Popen(cmd,shell=False,stdin=None,stdout=None,\
                            stderr=None,bufsize=0,startupinfo=si)
                        win32pipe.ConnectNamedPipe(tpipe,None)
                        imbuffer=''
                        if version_info[0]<3: imbuffer=''
                        else: imbuffer=b''
                        if tpipe:
                            while True:
                                data=None
                                try: data=win32file.ReadFile(tpipe,16777216)
                                except: data=None
                                if not(data): break
                                if data[0]!=0: break
                                if len(data[1]): imbuffer+=data[1]
                        win32pipe.DisconnectNamedPipe(tpipe)
                        f.wait()
                    if len(imbuffer):
                        if imbuffer[0]==('a' if version_info[0]<3 else 97):
                           mode='RGBA'
                        else: mode='RGB'
                        x,=unpack("i",imbuffer[1:5])
                        y,=unpack("i",imbuffer[5:9])
                        try: self.img=Image.frombytes(mode,(x,y),imbuffer[9:])
                        except: err=1
                        del imbuffer
                    else: err=1
                except: err=1
                if err: msg=_('BPG decoding error!\n')
        else: msg=_('File')+' \"%s\" '%filename+_('is not a BPG-File!')
        if msg:
            wx.PostEvent(self,ShowEvent(SE_EVT_TYPE,-1,value=msg))
            if self.img:
                del self.img
                self.img=None
        else: return True
        return False
    def stitle(self,title):
        self.Title=title
        if osflag: self.Update()
        else: self.Refresh()
    def deftitle(self):
        self.stitle(_('Press Ctrl+O to open BPG file...'))
    def getcsize(self):
        cr=wx.Display().GetClientArea()
        cw=self.GetSize()
        cc=self.GetClientSize()
        return cr[2]-cr[0]-cw[0]+cc[0],cr[3]-cr[1]-cw[1]+cc[1]
    def bitmapfrompil(self,img):
        if img.mode[-1]=='A':
            if wx.VERSION[0]<4:
                return wx.BitmapFromBufferRGBA(img.size[0],\
                    img.size[1],img.convert("RGBA").tobytes())
            else:
                return wx.Bitmap.FromBufferRGBA(img.size[0],\
                    img.size[1],img.convert("RGBA").tobytes())
        else:
            if wx.VERSION[0]<4:
                return wx.BitmapFromBuffer(img.size[0],img.size[1],\
                    img.convert("RGB").tobytes())
            else:
                return wx.Bitmap.FromBuffer(img.size[0],img.size[1],\
                    img.convert("RGB").tobytes())
    def scalebitmap(self,width,height):
        if self.img:
            return self.bitmapfrompil(self.img.resize((int(width),\
                int(height)),Image.ANTIALIAS))
        else: return None
    def showbitmap(self,bitmap):
        self.bitmap._clear=True
        if bitmap==None: self.showempty()
        else:
            self.bitmap.SetBitmap(bitmap)
            self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
            if wx.VERSION[0]<4: self.bitmap.SetToolTipString(self.imginfo)
            else: self.bitmap.SetToolTip(self.imginfo)
            x,y=bitmap.GetSize()
            self.panel.SetVirtualSize((x,y))
            self.panel.SetScrollbars(1,1,x,y)
            self.panel.SetScrollRate(1,1)
            cx,cy=self.getcsize()
            if not(self.IsMaximized()) and not(self.IsFullScreen()) and\
                x<=cx and y<=cy:
                self.panel.SetInitialSize(size=(x,y))
                self.panel.SetClientSize((x,y))
                self.Layout()
                self.Fit()
                self.Center()
            else: self.Layout()
    def emptybitmap(self):
        if wx.VERSION[0]<4: buffer=wx.EmptyBitmap(400,300)
        else: buffer=wx.Bitmap(400,300)
        dc=wx.BufferedDC(None,buffer)
        dc.SetBackground(wx.Brush(self.panel.GetBackgroundColour()))
        dc.Clear()
        dc.Destroy()
        return buffer
    def showempty(self):
        if self.img:
            try: del self.img
            except: pass
            self.img=None
            self.showbitmap(self.emptybitmap())
        self.imginfo=''
    def autoscaled(self):
        if self.img:
            if self.IsFullScreen(): cx,cy=wx.DisplaySize()
            else:
                if self.IsMaximized() or self.max: cx,cy=self.GetClientSize()
                else: cx,cy=self.getcsize()
            d=0.0
            x=self.img.size[0]
            y=self.img.size[1]
            self.bitmap_text=str(x)+'x'+str(y)
            d0=float(cx)/float(x)
            d1=float(cy)/float(y)
            if d0<1.0 or d1<1.0:
                d=d0 if d0<d1 else d1
                x=floor(x*d)
                y=floor(y*d)
                self.scale=d*100.0
                self.autoscale=self.scale
                return self.scalebitmap(x,y)
            else:
                self.scale=100.0
                self.autoscale=self.scale
                return self.bitmapfrompil(self.img)
        return None
    def _showimage(self,filename):
        filename=__(filename,self.codepage)
        if len(filename) and self.bpgdecode(filename):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
        wx.PostEvent(self,ShowEvent(SE_EVT_TYPE,-1))
    def _evt_showimage(self,evt):
        if evt.value: errmsgbox(evt.value)
        else:
            self.showbitmap(self.autoscaled())
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
            else: self.deftitle()
    def showimage(self,filename):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        self.dthread=DecodeThread(self,lambda: self._showimage(filename))
        self.dthread.start()
    def getfilelist(self,dirname):
        filelist=[]
        for f in sorted(listdir(dirname)):
            fname=realpath(join(dirname,f))
            try:
                if access(fname,R_OK) and isfile(fname) and\
                    fname[-4:].lower()=='.bpg':
                    fname=__(fname,self.codepage)
                    filelist.append(fname)
            except: pass
        return filelist
    def checkpath(self,path):
        if isdir(path):
            self.filelist=self.getfilelist(realpath(path))
            if len(self.filelist): path=self.filelist[0]
        return path
    def __init__(self,parent,title):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        self.dt=FileDropTarget(self)
        self.SetDropTarget(self.dt)
        self.max=False
        self.codepage=locale.getdefaultlocale()[1]
        self.bpgpath=bpggetcmd()
        self.scale=100.0
        self.autoscale=100.0
        self.bitmap_text=''
        self.img=None
        self.imginfo=''
        self.fifo=''
        self.dlock=Lock()
        self.mpos=None
        t,self.fifo=mkstemp(suffix='.rgb',prefix='')
        close(t)
        remove(self.fifo)
        if osflag:
            try: mkfifo(self.fifo,0o700)
            except:
                msg=_('Unable to create FIFO file!')
                errmsgbox(msg)
                exit()
        self.filelist=[]
        self.index=0
        self.SetDoubleBuffered(True)
        self.SetInitialSize(size=(400,300))
        self.panel=wx.ScrolledWindow(self,-1,style=wx.WANTS_CHARS)
        self.psizer=wx.FlexGridSizer(1,1,0,0)
        self.psizer.AddGrowableCol(0)
        self.psizer.AddGrowableRow(0)
        self.bitmap=GenBitmap(self.panel,-1,style=wx.WANTS_CHARS,
            bitmap=self.emptybitmap())
        self.psizer.Add(self.bitmap,1,wx.ALIGN_CENTER,0)
        self.panel.SetSizer(self.psizer)
        self.sizer=wx.FlexGridSizer(1,1,0,0)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.sizer.Add(self.panel,1,wx.ALIGN_CENTER,0)
        self.SetSizer(self.sizer)
        title=self.checkpath(title)
        self.showimage(title)
        self.bitmap.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.bitmap.Bind(wx.EVT_MOTION,self.drag)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.bitmap.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.Bind(wx.EVT_SIZE,self.fresize)
        self.Bind(wx.EVT_ERASE_BACKGROUND,lambda e: None)
        if osflag: self._icon=bpglogo.GetIcon()
        else:
            tmp_icon=bpglogo.GetImage()
            tmp_icon.Rescale(32,32,wx.IMAGE_QUALITY_HIGH)
            self._icon=wx.Icon()
            self._icon.CopyFromBitmap(wx.Bitmap(tmp_icon))
        try: self.SetIcon(self._icon)
        except: pass
        self.Bind(SE_EVT_BNDR,self._evt_showimage)
        self.Layout()
        self.Center()
        self.panel.SetFocus()
    def loadindex(self,old):
        if self.index!=old:
            self.stitle(_('Loading...'))
            self.showimage(self.filelist[self.index])
    def previous(self):
        if len(self.filelist):
            old=self.index
            if self.index: self.index-=1
            else: self.index=len(self.filelist)-1
            self.loadindex(old)
    def next(self):
        if len(self.filelist):
            old=self.index
            if self.index<len(self.filelist)-1: self.index+=1
            else: self.index=0
            self.loadindex(old)
    def first(self):
        if len(self.filelist) and self.index:
            self.index=0
            self.loadindex(1)
    def last(self):
        if len(self.filelist) and self.index!=len(self.filelist)-1:
            self.index=len(self.filelist)-1
            self.loadindex(0)
    def drag(self,event):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        if self.img:
            if event.Dragging():
                pos=event.GetPosition()
                if self.mpos!=None:
                    px,py=self.panel.GetScrollPixelsPerUnit()
                    dx=self.mpos[0]-pos[0]
                    dy=self.mpos[1]-pos[1]
                    self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+\
                        dx/px,self.panel.GetScrollPos(wx.VERTICAL)+dy/py)
                return
            if event.LeftDown():
                self.mpos=event.GetPosition()
                return
            if event.LeftUp():
                self.mpos=None
                return
        if event.ButtonDClick():
            self.mpos=None
            self.maximize()
    def rotate(self,dir):
        if self.img:
            self.bitmap._clear=True
            self.stitle(_('Rotating...'))
            if dir: self.img=self.img.rotate(-90,expand=1)
            else: self.img=self.img.rotate(90,expand=1)
            if self.img:
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(self.bitmapfrompil(self.img))
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
    def fresize(self,event):
        x,y=self.GetClientSize()
        self.panel.SetInitialSize(size=(x,y))
        self.panel.SetClientSize((x,y))
        if not(self.IsFullScreen()):
            fx,fy=self.GetSize()
            cr=wx.Display().GetClientArea()
            cx=cr[2]-cr[0]
            cy=cr[3]-cr[1]
            if fx==cx and fy==cy or self.IsMaximized():
                self.max=True
                self.autoimg()
            else: self.max=False
        self.Layout()
    def autoimg(self):
        if self.scale==self.autoscale:
            self.showbitmap(self.autoscaled())
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
            else: self.deftitle()
    def maximize(self):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        if not(self.IsFullScreen()):
            if self.IsMaximized() or self.max:
                self.max=False
                self.Maximize(False)
            else:
                self.max=True
                self.Maximize()
    def keydown(self,event):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        keycode=event.GetKeyCode()
        if event.ControlDown():
            if keycode==ord('F'):
                if self.IsFullScreen():
                    self.ShowFullScreen(False,style=wx.DEFAULT_FRAME_STYLE)
                else:
                    self.ShowFullScreen(True,style=wx.FULLSCREEN_ALL)
                    self.autoimg()
                return
            if keycode==ord('O'):
                openFileDialog = wx.FileDialog(self,_('Open BPG file'),"","",\
                    _("BPG files")+" (*.bpg)|*.bpg",\
                    wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
                status=openFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    self.stitle(_('Loading...'))
                    self.filelist=[]
                    self.showimage(openFileDialog.GetPath())
                    openFileDialog.Destroy()
                return
            if keycode==ord('S') and self.img:
                saveFileDialog=wx.FileDialog(self,_("Save BPG file as PNG file"),\
                    "",basename(self.filelist[self.index])[:-4]+'.png',\
                    _("PNG files")+" (*.png)|*.png",\
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                status=saveFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    dst=saveFileDialog.GetPath()
                    dst=__(dst,self.codepage)
                    if dst[-4:].lower()!='.png': dst+='.png'
                    ttitle=self.Title
                    self.stitle(_('Saving PNG file...'))
                    try:
                        if exists(dst): remove(dst)
                        self.img.save(dst,'PNG',optimize=True)
                    except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                    self.stitle(ttitle)
                    return
            if keycode==ord('C') and self.img:
                saveFileDialog=wx.FileDialog(self,_("Save a copy..."),"",\
                    basename(self.filelist[self.index])[:-4],\
                    _("BPG files")+" (*.bpg)|*.bpg",\
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                status=saveFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    dst=saveFileDialog.GetPath()
                    try:
                        dst=__(dst,self.codepage)
                        if exists(dst) and\
                            abspath(self.filelist[self.index])!=dst: remove(dst)
                        copyfile(self.filelist[self.index],dst)
                    except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                    return
            if keycode==ord('R'):
                self.rotate(True)
                return
            if keycode==ord('L'):
                self.rotate(False)
                return
            if keycode in [wx.WXK_LEFT,wx.WXK_NUMPAD_LEFT]:
                self.first()
                return
            if keycode in [wx.WXK_RIGHT,wx.WXK_NUMPAD_RIGHT]:
                self.last()
                return
        else:
            if keycode==wx.WXK_HOME:
                self.first()
                return
            if keycode==wx.WXK_END:
                self.last()
                return
            if keycode==wx.WXK_ESCAPE:
                self.Close()
                return
            if keycode in [wx.WXK_PAGEUP,wx.WXK_NUMPAD_PAGEUP,wx.WXK_BACK]:
                self.previous()
                return
            if keycode in [wx.WXK_PAGEDOWN,wx.WXK_NUMPAD_PAGEDOWN,\
                wx.WXK_RETURN]:
                self.next()
                return
            if keycode in [wx.WXK_LEFT,wx.WXK_NUMPAD_LEFT]:
                self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)-5,\
                    self.panel.GetScrollPos(wx.VERTICAL))
                return
            if keycode in [wx.WXK_RIGHT,wx.WXK_NUMPAD_RIGHT]:
                self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+5,\
                    self.panel.GetScrollPos(wx.VERTICAL))
                return
            if keycode in [wx.WXK_UP,wx.WXK_NUMPAD_UP]:
                self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                    self.panel.GetScrollPos(wx.VERTICAL)-5)
                return
            if keycode in [wx.WXK_DOWN,wx.WXK_NUMPAD_DOWN]:
                self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                    self.panel.GetScrollPos(wx.VERTICAL)+5)
                return
            if keycode==wx.WXK_F1:
                wx.MessageBox(_('This is BPG image file viewer. Hot keys:\n')+\
                _('Esc - close\n')+\
                _('Ctrl+O - open BPG image file\n')+\
                _('Ctrl+S - save a copy of the opened file as a PNG file\n')+\
                _('Ctrl+C - save a copy of the opened file\n')+\
                _('Ctrl+R - rotate 90 degrees clockwise\n')+\
                _('Ctrl+L - rotate 90 degrees counterclockwise\n')+\
                _('Ctrl+F - toggle full screen mode\n')+\
                _('Ctrl+Left,Home - jump to the first image in folder\n')+\
                _('Ctrl+Right,End - jump to the last image in folder\n')+\
                _('+ - zoom in (up to 100%)\n')+\
                _('- - zoom out (down to the smallest available size)\n')+\
                _('* - zoom out to fit window area\n')+\
                _('Left,Up,Right,Down - move over the scaled image\n')+\
                _('PgUp,Backspace,A,S - view previous file\n')+\
                _('PgDown,Return,D,W - view next file\n')+\
                _('Delete - delete current file\n'),_('Help'),\
                wx.OK|wx.ICON_INFORMATION)
                return
            if keycode in [wx.WXK_DELETE,wx.WXK_NUMPAD_DELETE]:
                if len(self.filelist) and self.img:
                    if wx.MessageBox(_('Delete file')+' "'+\
                        self.filelist[self.index]+'"?',_('File deletion!'),\
                        wx.YES_NO|wx.ICON_WARNING|wx.NO_DEFAULT)==wx.YES:
                        index=self.index
                        try: remove(self.filelist[index])
                        except:
                            msg=_('Unable to delete:')+\
                                ' \"%s\"!'%self.filelist[self.index]
                            errmsgbox(msg)
                            return
                        self.filelist.pop(index)
                        if len(self.filelist):
                            if index>=len(self.filelist): self.index=0
                            self.loadindex(None)
                        else:
                            self.showempty()
                            self.deftitle()
                return
            if keycode in [wx.WXK_RETURN,ord('D'),ord('W')]:
                self.next()
                return
            if keycode in [ord('A'),ord('S')]:
                self.previous()
                return
            if keycode in [wx.WXK_NUMPAD_ADD,ord('=')]:
                if self.img and self.scale<100.0:
                    self.stitle(_('Zooming in...'))
                    self.scale+=5.0
                    if self.scale>100.0: self.scale=100.0
                    if self.scale!=100.0:
                        x=self.img.size[0]*(self.scale/100.0)
                        y=self.img.size[1]*(self.scale/100.0)
                        self.showbitmap(self.scalebitmap(x,y))
                    else: self.showbitmap(self.bitmapfrompil(self.img))
                    if len(self.imginfo): self.stitle(\
                        self.filelist[self.index]+' ('+self.imginfo+')')
                    else: self.deftitle()
                return
            if keycode in [wx.WXK_NUMPAD_SUBTRACT,ord('-')]:
                if self.img and self.scale>self.autoscale:
                    self.stitle(_('Zooming out...'))
                    self.scale-=5.0
                    if self.scale<self.autoscale: self.scale=self.autoscale
                    if self.scale!=100.0:
                        x=self.img.size[0]*(self.scale/100.0)
                        y=self.img.size[1]*(self.scale/100.0)
                        self.showbitmap(self.scalebitmap(x,y))
                    else: self.showbitmap(self.bitmapfrompil(self.img))
                    if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                        ' ('+self.imginfo+')')
                    else: self.deftitle()
                return
            if keycode in [wx.WXK_NUMPAD_MULTIPLY,ord('8')]:
                if self.img:
                    cx,cy=self.GetClientSize()
                    x,y=self.bitmap.GetSize()
                    if cx<x or cy<y:
                        x=self.img.size[0]
                        y=self.img.size[1]
                        d0=float(cx)/float(x)
                        d1=float(cy)/float(y)
                        self.scale=d0 if d0<d1 else d1
                        x=floor(x*self.scale)
                        y=floor(y*self.scale)
                        self.scale*=100.0
                        self.autoscale=self.scale
                        self.showbitmap(self.scalebitmap(x,y))
                        if len(self.imginfo):
                            self.stitle(self.filelist[self.index]+\
                            ' ('+self.imginfo+')')
                        else: self.deftitle()
                return
        event.Skip()
    def __del__(self):
        if osflag and exists(self.fifo):
            try: remove(self.fifo)
            except: pass

class bpgframe(wx.App):
    def __init__(self,parent,filename):
        super(bpgframe,self).__init__(parent)
        frame=DFrame(None,filename)
        self.SetTopWindow(frame)
        frame.Show()

if __name__=='__main__':
    wxapp=True
    if len(argv)==1: app=bpgframe(None,'')
    else: app=bpgframe(None,realpath(argv[1]))
    app.MainLoop()
