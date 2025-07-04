from setuptools import setup

APP = ['main.py']
DATA_FILES = ['accounts.db']
OPTIONS = {
    'argv_emulation': False,
    'packages': [],
    'includes': ['datetime'],
    'excludes': ['platformdirs', 'jaraco', 'zipp'],


}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)