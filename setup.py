from distutils.core import setup
from urllib.request import urlopen, urlretrieve
from xml.dom.minidom import parse
from distutils.command.sdist import sdist
from distutils.command.build_scripts import build_scripts
from distutils.cmd import Command
from distutils.util import get_platform
from zipfile import ZipFile
from contextlib import suppress
import re
import os

class sdistx(sdist):
    def run(self):

        archive_files = []

        base = 'https://chromedriver.storage.googleapis.com/?delimiter=/'
        page = parse(urlopen(base))
        versions = page.getElementsByTagName('CommonPrefixes')
        versions = [v.firstChild.firstChild.nodeValue for v in versions]
        versions = sorted(versions,
            key=lambda x:[int(re.search(r'\d+','0'+key).group()) for key in x.split('.')])
        for version in versions:
            if version == 'icons/': continue
            self.distribution.metadata.version=version[:-1]
            sdist.run(self)
            archive_files.extend(self.archive_files)
                #print()

        self.archive_files = archive_files
        os.remove('VERSION')

    def get_file_list(self):
        self.filelist.append("VERSION")
        with open('VERSION','w') as f:
            f.write(self.distribution.metadata.version)
        sdist.get_file_list(self)


class build_scriptsx(build_scripts):
    def run(self):
        build_scripts.run(self)
        
        platform = get_platform()
        if platform[:3] == "win":
            platform = 'win32'
        else:
            raise Exception('Unrecognized platform: "%s"' % platform)
        base = 'https://chromedriver.storage.googleapis.com/%s/chromedriver_%s.zip' % (
            self.distribution.metadata.version, platform)

        with ZipFile(urlretrieve(base)[0]) as archive:
            archive.extract(archive.namelist()[0], path=self.build_dir)
        ##    urlopen(base)


ver = '2.27'
with suppress(FileNotFoundError):
    with open('VERSION','r') as f:
        ver = f.read()

setup(
    name="chromedrvr",
#    py_modules=["chromedrvr"],
    version=ver,
    cmdclass={'sdist':sdistx, 'build_scripts':build_scriptsx}
    )
