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
            self.distribution.metadata.version=version[:-1] +'.post'+inst_ver
            with open('VERSION','w') as f:
                f.write(version[:-1])
            sdist.run(self)
            archive_files.extend(self.archive_files)

        self.archive_files = archive_files


class build_scriptsx(build_scripts):
    def run(self):
        build_scripts.run(self)
        with open('VERSION','r') as f:
            ver = f.read().strip()

        platform = get_platform()
        if platform[:3] == "win":
            platform = 'win32'
        elif platform[:6] == 'macosx':
            platform = 'mac32'
        else:
            platform = 'linux64' if sys.maxsize == 9223372036854775807 else 'linux32'
        base = 'https://chromedriver.storage.googleapis.com/%s/chromedriver_%s.zip'
        base = base % (ver, platform)

        with ZipFile(urlretrieve(base)[0]) as archive:
            archive.extract(archive.namelist()[0], path=self.build_dir)



if os.path.isfile('VERSION'):
    with open('VERSION','r') as f:
        ver = f.read().strip()
else:
    ver = urlopen('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').read().strip()
    with open('VERSION','w') as f:
        f.write(ver)

inst_ver = '2'
ver = ver +'.post'+inst_ver


setup(
    name="chromedrvr",
    version=ver,
    scripts=['chromedriver'],
    cmdclass={'sdist':sdistx, 'build_scripts':build_scriptsx}
    )
