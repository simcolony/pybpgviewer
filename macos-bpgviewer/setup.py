"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['bpgviewer.py']
APP_NAME = 'Simple BPG Image viewer'
DATA_FILES = ['bpgdec']
OPTIONS = {
    'argv_emulation': True,
    'iconfile':'bpg.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': 'Viewer for BPG images',
        'CFBundleIdentifier': "org.asimbarsky.osx.bpgviewer",
        'CFBundleVersion': "1.24.0",
        'CFBundleShortVersionString': "1.24.0",
        'NSHumanReadableCopyright': u"Copyright (c) 2018, Alexey Simbarsky, All Rights Reserved",
        'NSQuitAlwaysKeepsWindows': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'BPG image file',
                'CFBundleTypeExtensions':['bpg'],
                'CFBundleTypeIconFile': 'bpg.icns',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Default',
            },
        ]
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    name='Simple BPG Image viewer',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
