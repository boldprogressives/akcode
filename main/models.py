import codecs
from django.db import models
from django.conf import settings
import os
import re
import subprocess
import tempfile

class Templateset(models.Model):
    class Meta:
        managed = False
        db_table = "cms_templateset"

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    name = models.CharField(max_length=255)
    description = models.TextField()

    #lang = models.ForeignKey(Language, null=True, blank=True)

    editable = models.BooleanField()
    hidden = models.BooleanField()
    is_default = models.NullBooleanField(null=True, blank=True)

class Template(models.Model):
    class Meta:
        managed = False
        db_table = "cms_template"

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    templateset = models.ForeignKey(Templateset)
    filename = models.CharField(max_length=255)
    code_hash = models.CharField(max_length=64)
    code = models.TextField()

class TemplateHistory(models.Model):
    class Meta:
        managed = False
        db_table = "cms_templatehistory"

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    templateset = models.ForeignKey(Templateset)
    filename = models.CharField(max_length=255)
    code_hash = models.CharField(max_length=64)
    user_name = models.CharField(max_length=64, null=True, blank=True)
    edit_type = models.CharField(max_length=64, null=True, blank=True)

class TemplateCode(models.Model):
    class Meta:
        managed = False
        db_table = "cms_templatecode"

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    code_hash = models.CharField(max_length=64)
    code = models.TextField()

class cd:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class CodeBlock(models.Model):

    class Meta:
        db_table = "akcode_codeblock"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    filename = models.CharField(max_length=80, unique=True)
    code = models.TextField(default='', blank=True)

    PATTERN = r'<include file="(?P<filename>[\d\w\-/_\.;=]+)" />'

    @models.permalink
    def get_edit_url(self):
        return ("codeblock_edit", [self.filename])

    def save_version(self, msg=None):
        if settings.AKCODE_GIT_REPO is None:
            return

        msg = msg or 'edits'
        checkout_dir = tempfile.mkdtemp()
        with cd(checkout_dir):
            subprocess.call(['git', 'clone', 
                             settings.AKCODE_GIT_REPO, '.'])
            filename = os.path.join(checkout_dir, self.filename)
            dir = os.path.dirname(filename)
            try:
                os.makedirs(dir)
            except:
                pass
            fp = codecs.open(filename, 'w', encoding='utf8')
            fp.write(self.code)
            fp.close()
            subprocess.call(['git', 'add', self.filename])
            subprocess.call(['git', 'commit', '-m', msg])
            subprocess.call(['git', 'push'])

    def resolve(self):
        return re.sub(self.PATTERN, self._do_include, self.code)

    def _do_include(self, inclusion):
        inclusion = inclusion.groupdict()['filename']
        inclusion = inclusion.strip()
        indent = None
        if ";indent=" in inclusion:
            inclusion, indent = inclusion.split(";indent=")
        inclusion = inclusion.strip()
        try:
            indent = int(indent)
        except (ValueError, TypeError):
            indent = 0
        try:
            block = CodeBlock.objects.get(filename=inclusion)
        except CodeBlock.DoesNotExist:
            block = ''
        else:
            block = block.code
        lines = block.splitlines()
        lines = ["{# BEGIN snippet %s #}" % inclusion] + lines + [
            "{# END snippet %s #}" % inclusion]
        block = '\n'.join(((indent * ' ') + x if x else x) for x in lines)
        return re.sub(self.PATTERN, self._do_include, block)

class CodeMap(models.Model):
    templateset = models.IntegerField()
    template = models.CharField(max_length=100)

    slug = models.CharField(max_length=100)

    local_file = models.ForeignKey(CodeBlock)

