from djangohelpers.lib import register_admin
from main.models import CodeBlock, CodeMap

register_admin(CodeBlock, exclude=["code"])
register_admin(CodeMap)
