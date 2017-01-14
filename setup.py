from distutils.core import setup
from urllib.request import urlopen
from xml.dom.minidom import parse
from distutils.command.sdist import sdist
from distutils.command.build_scripts import build_scripts
from distutils.cmd import Command
from distutils.util import get_platform

class sdistx(sdist):
    def run(self):

        archive_files = []
        
        base = 'https://chromedriver.storage.googleapis.com/?delimiter=/'
        page = parse(urlopen(base))
        versions = page.getElementsByTagName('CommonPrefixes')
        for version in [v.firstChild.firstChild.nodeValue for v in versions]:
            if version == 'icons/': continue
            self.distribution.metadata.version=version[:-1]
            sdist.run(self)
            archive_files.extend(self.archive_files)
                #print()

        self.archive_files = archive_files
    def get_file_list(self):
        self.filelist.append("VERSION")
        sdist.get_file_list(self)
         
class build_scriptsx(build_scripts):
    def run(self):
        build_scripts.run(self)
        print(self.distribution.metadata.version)
        platform = get_platform()
        if platform[:3] == "win":
            platform = 'win32'
        else:
            raise Exception('Unrecognized platform: "%s"' % platform)
        base = 'https://chromedriver.storage.googleapis.com/%s/chromedriver_%s' % (
            self.distribution.metadata.version, platform)
        
        
        urlopen(base).read()
        ##    urlopen(base)


        
        


setup(
    name="chromedrvr",
    py_modules=["chromedrvr"],
    version='__version__',
    
    cmdclass={'sdist':sdistx, 'build_scripts':build_scriptsx}
    )

