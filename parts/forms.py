from django import forms
from parts.models import Assignment, Publisher, CounselPoint, Category, GENDERS

class FormWithUserMixin(object):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(FormWithUserMixin, self).__init__(*args, **kwargs)

class AssignmentForm(forms.ModelForm):
  class Meta:
    model = Assignment
    fields = ('publisher',)

class CounselForm(forms.ModelForm):
  class Meta:
    model = Assignment
    fields = ('counsel_point', 'counsel', 'timing')
  counsel_point = forms.ModelChoiceField(queryset=CounselPoint.objects.all(), initial="", widget=forms.Select(attrs={'placeholder':'Counsel Point','class':'form-control'}), required=False)
  next_counsel_point = forms.ModelChoiceField(queryset=CounselPoint.objects.all(), initial="", widget=forms.Select(attrs={'placeholder':'Counsel Point','class':'form-control'}), required=False)
  setting = forms.CharField(initial="", widget=forms.TextInput(attrs={'placeholder':'Setting','class':'form-control'}), required=False)
  counsel = forms.CharField(initial="", widget=forms.Textarea(attrs={'placeholder':'Notes','class':'form-control'}), required=False)
  timing = forms.CharField(initial="", widget=forms.TextInput(attrs={'placeholder':'Timing','class':'form-control'}), required=False)
  exercises_done = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'form-control'}))

class AssistantForm(forms.ModelForm):
  class Meta:
    model = Assignment
    fields = ('assistant',)
  assistant = forms.ModelChoiceField(queryset=Publisher.objects.all(), initial="", widget=forms.Select(attrs={'placeholder':'Counsel Point','class':'form-control'}), required=False)
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user')
    super(AssistantForm, self).__init__(*args, **kwargs)
    self.fields['assistant'].queryset = Publisher.objects.filter(congregation=self.user.congregation, categories=17)

class PublisherForm(forms.ModelForm):
  class Meta:
    model = Publisher
    fields = ('last_name', 'first_name', 'gender','counsel_point', 'categories')
  last_name = forms.CharField(initial="", widget=forms.TextInput(attrs={'placeholder':'Last','class':'form-control'}), required=False)
  first_name = forms.CharField(initial="", widget=forms.TextInput(attrs={'placeholder':'First','class':'form-control'}), required=False)
  gender = forms.ChoiceField(choices=GENDERS, initial="", widget=forms.Select(attrs={'placeholder':'Counsel Point','class':'form-control'}), required=False)
  counsel_point = forms.ModelChoiceField(queryset=CounselPoint.objects.all(), initial="", widget=forms.Select(attrs={'placeholder':'Counsel Point','class':'form-control'}), required=False)
  categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), initial="", widget=forms.SelectMultiple(attrs={'placeholder':'Counsel Point','class':'form-control multi-drop'}), required=False)
