from actionkit.utils import get_client
from actionkit.rest import client as rest_client
from django.conf import settings
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect, get_object_or_404
from djangohelpers import (rendered_with,
                           allow_http)
from django.views.decorators.csrf import csrf_exempt
import json

from main.diff import make_diff_snippet
from main.forms import CheckoutForm, CodeBlockCreateForm, RemoteTemplateEditForm
from main.models import Template, Templateset, TemplateCode, TemplateHistory, CodeMap, CodeBlock

@csrf_exempt
@allow_http("POST")
def changeset_added(request):
    # @@TODO conflict detection?
    body = json.loads(request.body)
    for commit in body['commits']:
        path = commit['path']
        change = commit['change']
        if change == "edit":
            try:
                block = CodeBlock.objects.get(filename=path)
            except CodeBlock.DoesNotExist:
                block = CodeBlock(filename=path)
            block.code = commit['content']
            block.save()
        elif change == "add":
            try:
                block = CodeBlock.objects.get(filename=path)
            except CodeBlock.DoesNotExist:
                block = CodeBlock(filename=path)
            block.code = commit['content']
            block.save()
        elif change == "move":
            try:
                block = CodeBlock.objects.get(filename=commit['original_path'])
            except CodeBlock.DoesNotExist:
                block = CodeBlock(filename=commit['original_path'])
            block.code = commit['content']
            block.filename = path
            block.code = commit['content']
            block.save()
        elif change == "delete":
            try:
                block = CodeBlock.objects.get(filename=path)
            except CodeBlock.DoesNotExist:
                pass
            else:
                block.delete()
    # @@TODO return something interesting
    return HttpResponse("ok")

@allow_http("GET")
@rendered_with("main/home.html")
def home(request):
    return {}

@allow_http("GET")
@rendered_with("main/templatesets.html")
def templatesets_index(request):
    templatesets = Templateset.objects.using("ak").order_by("name").all()

    return {'templatesets': templatesets}

@allow_http("GET")
@rendered_with("main/checkouts.html")
def checkout_index(request):
    codeblocks = CodeMap.objects.all().values_list("slug", flat=True).distinct()

    return {'checkouts': codeblocks}

@allow_http("GET")
@rendered_with("main/templateset_overview.html")
def templateset_overview(request, id):
    templateset = get_object_or_404(Templateset.objects.using("ak"), id=id)
    templates = Template.objects.using("ak").filter(templateset=templateset)
    history = TemplateHistory.objects.using("ak").filter(
        templateset=templateset).order_by("-created_at")[:10]
    return locals()

@allow_http("GET")
@rendered_with("main/checkout_overview.html")
def checkout_overview(request, slug):
    codeblocks = list(CodeMap.objects.filter(slug=slug).select_related("codeblock"))
    checkout = codeblocks[0].slug
    templateset_id = codeblocks[0].templateset

    return locals()

@allow_http("GET", "POST")
@rendered_with("main/templateset_checkout.html")
def templateset_checkout(request, id):

    if request.method == "GET":
        return {
            'form': CheckoutForm(),
            }

    form = CheckoutForm(data=request.POST)
    if not form.is_valid():
        return {
            'form': CheckoutForm(),
            }

    slug = form.cleaned_data['slug']

    templateset = get_object_or_404(Templateset.objects.using("ak"), id=id)

    templates = Template.objects.using("ak").filter(templateset=templateset)
    for template in templates:
        block = CodeBlock(filename="%s/%s" % (slug, template.filename))
        block.code = template.code
        block.save()

        map = CodeMap(templateset=id, template=template.filename, local_file=block,
                      slug=slug)
        map.save()
    return redirect("/checkout/%s/" % slug)

@allow_http("POST")
def templateset_checkin(request, slug):
    # @@TODO this kinda has to be async
    checkout = CodeMap.objects.filter(slug=slug).select_related("codeblock")

    for entry in checkout:
        try:
            template = Template.objects.using("ak").select_related("templateset").get(
                templateset__id=entry.templateset, filename=entry.template)
        except Template.DoesNotExist:
            continue
        try:
            RemoteTemplateEditForm(template.id, entry.local_file.resolve()).save()
        except Exception, e:
            continue

    return redirect("templateset_overview", entry.templateset)

@allow_http("GET")
@rendered_with("main/templateset_template.html")
def templateset_template(request, id, filename):
    template = get_object_or_404(Template.objects.using("ak").select_related("templateset"),
                                 templateset__id=id, filename=filename)
    _history = list(TemplateHistory.objects.using("ak").filter(
            templateset__id=id, filename=filename).order_by("-created_at"))

    history = []
    for i, entry in enumerate(_history):
        if i+1 < len(_history):
            entry.prev_hash = _history[i+1].code_hash
        else:
            entry.prev_hash = _history[0].code_hash
        history.append(entry)
    return locals()
    
@allow_http("GET")
@rendered_with("main/templateset_templatediff.html")
def templateset_templatediff(request, id, filename, hash1, hash2):
    before = get_object_or_404(TemplateHistory.objects.using("ak"),
                               templateset__id=id, filename=filename, code_hash=hash1)
    after = get_object_or_404(TemplateHistory.objects.using("ak"),
                              templateset__id=id, filename=filename, code_hash=hash2)

    before_code = TemplateCode.objects.using("ak").get(code_hash=hash1)
    after_code = TemplateCode.objects.using("ak").get(code_hash=hash2)
    
    block1 = before_code.code
    block2 = after_code.code

    diff_code = make_diff_snippet(
        block1, block2, filename, filename, hash1, hash2, None, None)
                                  
    return locals()

@allow_http("GET", "POST")
@rendered_with("main/codeblock_diff.html")
def codeblock_diff(request, filename):
    codeblock = get_object_or_404(CodeBlock, filename=filename)
    if request.method == "GET":
        return locals()

    diff_to = request.POST['diff_to']
    
    diff_code = make_diff_snippet(
        codeblock.code, diff_to, codeblock.filename, 'None', 'None', 'None', None, None)
    return locals()

@allow_http("GET", "POST")
@rendered_with("main/codeblock_edit.html")
def codeblock_edit(request, filename):
    codeblock = get_object_or_404(CodeBlock, filename=filename)
    createform = CodeBlockCreateForm()

    if request.method == "GET":
        return locals()

    codeblock.code = request.POST['code']
    codeblock.save()

    codeblock.save_version(msg=request.POST['commit_message'], user=request.user)

    return redirect(".")

@allow_http("GET", "POST")
@rendered_with("main/codeblock_create.html")
def codeblock_create(request):
    if request.method == "GET":
        createform = CodeBlockCreateForm()
        return locals()

    createform = CodeBlockCreateForm(data=request.POST)
    if not createform.is_valid():
        return locals()

    codeblock = createform.save()
    codeblock.save_version(msg=createform.cleaned_data['commit_message'], user=request.user)

    return redirect(codeblock.get_edit_url())

@allow_http("GET", "POST")
@rendered_with("main/templateset_template_edit.html")
def templateset_template_edit(request, id, filename):
    template = get_object_or_404(Template.objects.using("ak").select_related("templateset"),
                                 templateset__id=id, filename=filename)

    if request.method == "GET":
        return locals()

    RemoteTemplateEditForm(template.id, request.POST['code']).save()
    return redirect("..")
