import codecs
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import os
import subprocess
import tempfile

from main.models import CodeBlock

class cd:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class Command(BaseCommand):
    args = '<repo_dir>'
    help = 'Imports all missing codeblocks into <repo_dir> repository'

    def handle(self, *args, **options):
        checkout_dir = tempfile.mkdtemp()
        with cd(checkout_dir):
            subprocess.call(['git', 'clone', settings.AKCODE_GIT_REPO, '.'])
        
            for block in CodeBlock.objects.all():
                filename = os.path.join(checkout_dir, block.filename)
                if os.path.exists(filename):
                    continue
                dir = os.path.dirname(filename)
                try:
                    os.makedirs(dir)
                except:
                    pass
                fp = codecs.open(filename, 'w', encoding='utf8')
                fp.write(block.code)
                fp.close()
                subprocess.call(['git', 'add', block.filename])
            subprocess.call(['git', 'commit', '-m', 'importing missing codeblocks'])
            subprocess.call(['git', 'push'])

