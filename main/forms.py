from actionkit.utils import get_client
from django import forms
from django.core.urlresolvers import reverse
from main.models import CodeBlock

class CheckoutForm(forms.Form):

    slug = forms.SlugField()

class CodeBlockCreateForm(forms.ModelForm):

    commit_message = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CodeBlock

    # This needs to be deferred to avoid circular imports into main.views within the urlresolver
    @property
    def action(self):
        return reverse("codeblock_create")

class RemoteTemplateEditForm(object):

    def __init__(self, template_id, new_code):
        self.template_id = template_id
        self.new_code = new_code

    def save(self):
        ak = get_client()
        resp = ak.Template.save({'id': self.template_id, 'code': self.new_code})

        return resp

        # @@TODO: currently ak template edit history is poorly preserved -- 
        # edit_type=None and no user name for the author.  
        # Should file a feature request with WAWD to make this settable directly on the 
        # initial save (I can't figure out how to do this w/the rest api either) 
        # because doing it w/additional requests is really inefficient.  
        # And also doesn't actually work as written here, because the templatehistory object
        # doesn't seem to make it to the replica db in time for it to be found here...
        hist_obj = None
        try:
            hist_obj = TemplateHistory.objects.using("ak").get(
                templateset__id=id, filename=filename,
                code_hash=resp['code_hash'])
        except TemplateHistory.DoesNotExist:
            pass
        if hist_obj is None:
            return redirect("..")

        api = rest_client(safety_net=False)
        data = api.templatehistory.get(hist_obj.id)
        data.pop('id')
        data['user_name'] = request.user.username
        data['edit_type'] = "api_edit"
        api.templatehistory.put(hist_obj.id, data)
