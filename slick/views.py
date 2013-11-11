import vanilla
from django.db.models import Q
from django.contrib import messages
from django.http import Http404
# For LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
class LoginRequiredMixin(object):
  u"""Ensures that user must be authenticated in order to access view."""
  @method_decorator(login_required)
  def dispatch(self, *args, **kwargs):
    return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class ExtraContextMixin(object):
  extra_context = {}
  def collect_bases(self, classType):
    bases = [classType]
    for baseClassType in classType.__bases__:
      bases += self.collect_bases(baseClassType)
    return bases
  def get_context_data(self, **kwargs):
    # Get the bases and remove duplicates
    bases = self.collect_bases(self.__class__)
    # for b in bases: print b
    bases.reverse()
    # print "======= Printing Bases ========"
    for base in bases:
      if hasattr(base, 'extra_context'):
        for key, value in base.extra_context.items():
          # print "key: %s value: %s" % (key, value)
          # First check to see if it's the name of a function
          if isinstance(value, basestring) and value[:4] == "get_": kwargs[key] = getattr(self,value)()
          # Otherwise, just add it to the context
          else: kwargs[key] = value
        # print "Base: %s Template: %s" % (base, kwargs.get('row_template_name',""))
        # for k,v in kwargs.items(): print "%s: %s" % (k,v)
    # print "==============================="
    # for key, value in kwargs.items(): print key+":"+str(value)
    return super(ExtraContextMixin, self).get_context_data(**kwargs)

class MessageMixin(object):
  # Sends messages when form is valid or invalid
  success_message = None
  error_message = None
  def get_error_message(self, form):return self.error_message
  def get_success_message(self, form):return self.success_message
  def form_valid(self, form):
    msg=self.get_success_message(form)
    if msg: messages.success(self.request, msg)
    return super(MessageMixin, self).form_valid(form)

  def form_invalid(self, form):
    error_msg=self.get_error_message(form)
    if error_msg: messages.error(self.request, error_msg)
    return super(MessageMixin, self).form_invalid(form)

class AjaxPostMixin(object):
  template_name = 'design/ajax_row.html'
  # Renders a response when form_valid
  def form_valid(self, form):
    self.object = form.save()
    context = self.get_context_data(form=form)
    return self.render_to_response(context)

class FormWithUserMixin(object):
  def get_form(self, data=None, files=None, **kwargs):
    cls = self.get_form_class()
    kwargs['user'] = self.request.user
    return cls(data=data, files=files, **kwargs)

class NonModelFormMixin(object):
  def get_form(self, data=None, files=None, **kwargs):
    del kwargs['instance']
    return super(NonModelFormMixin, self).get_form(data=data, files=files, **kwargs)
class CheckOwnerMixin(object):
  owner_field_name = None
  def get_queryset(self):
    qs= super(CheckOwnerMixin, self).get_queryset()
    if self.owner_field_name: qs = qs.filter(**{owner_field_name:self.request.user})
    return qs
  def get_object(self):
    obj = super(CheckOwnerMixin, self).get_object()
    if self.owner_field_name and not getattr(obj,self.owner_field_name)==self.request.user: return Http404
    return obj
class CreateView(ExtraContextMixin, MessageMixin, vanilla.CreateView): pass
class DetailView(CheckOwnerMixin, ExtraContextMixin, MessageMixin, vanilla.DetailView): pass
class UpdateView(CheckOwnerMixin, ExtraContextMixin, MessageMixin, vanilla.UpdateView): pass
class DeleteView(CheckOwnerMixin, ExtraContextMixin, vanilla.DeleteView): pass
class FormView(ExtraContextMixin, MessageMixin, vanilla.FormView): pass
class GenericModelView(CheckOwnerMixin, ExtraContextMixin, MessageMixin, vanilla.GenericModelView):pass
class TemplateView(ExtraContextMixin, MessageMixin, vanilla.TemplateView):pass
class GenericAjaxModelView(AjaxPostMixin, GenericModelView): pass
#   def post(self, request, *args, **kwargs):
#     self.object = self.get_object()
#     self.do_task()
#     context = self.get_context_data()
#     return self.render_to_response(context)
class AjaxCreateView(AjaxPostMixin, CreateView): pass 
class AjaxUpdateView(AjaxPostMixin, UpdateView): pass 
class AjaxDeleteView(DeleteView):
  success_message = ""
  template_name = 'design/ajax_row.html'
  def post(self, request, *args, **kwargs):
    # We save the pk so the js will know which row to replace
    self.object = self.get_object()
    old_pk=self.object.pk
    self.object.delete()
    if self.success_message: messages.success(self.request, self.success_message)
    context = self.get_context_data()
    context['object'].pk=old_pk
    return self.render_to_response(context)

class ListView(ExtraContextMixin, vanilla.ListView):
  search_key = 'q'
  search_on = []
  filter_on = []
  def return_pipe(self, x,y=None):
    if x and y: return x | y
    elif x: return x
    elif y: return y
  def filter(self, queryset):
    # Takes a queryset and returns the queryset filtered
    # If you want to do a custom filter for a certain field,
    # Declare a function: filter_{{fieldname}} that takes a queryset and the value, 
    # does the filter and returns the queryset
    # print "=queryset = %s" % str(queryset)
    for f in self.filter_on:
      if hasattr(self,'filter_'+f): queryset = getattr(self,'filter_'+f)(queryset, self.request.GET.getlist(f,[]))
      elif f in self.request.GET: queryset = queryset.filter(**{f:self.request.GET[f]})
      # print "==queryset = %s" % str(queryset)
    # print "===queryset = %s" % str(queryset)
    return queryset
  def search(self, queryset):
    # Takes a queryset and returns the queryset filtered based on search
    # The default search is "field = icontains"
    # If you want to do a custom search on a certain field, there are two ways:
    # 1) Declare a function: search_{{fieldname}} that takes a value and returns a Q()
    #    Example: def search_field(self, value): return Q(field = value)
    # 2) Set search_{{fieldname}} to a string to use as the filter name. 
    #    Example: search_field = "field__icontains"
    if self.search_key in self.request.GET:
      value = self.request.GET[self.search_key]
      query=None
      for field in self.search_on: 
        if hasattr(self,'search_'+field): 
          search=getattr(self,'search_'+field)
          if hasattr(search, '__call__'): query = self.return_pipe(query, search(value))
          elif type(search) == str: query = self.return_pipe(query, Q(**{search:value}))
        else: query = self.return_pipe(query, Q(**{field+"__icontains":value}))
      return queryset.filter(query)
    else: return queryset
  def get_queryset(self):
    queryset = super(ListView, self).get_queryset()
    if self.filter_on: queryset = self.filter(queryset)
    if self.search_on: queryset = self.search(queryset)
    # print "*queryset = %s" % str(queryset)
    return queryset
  def get_context_data(self, **kwargs):
    context = super(ListView, self).get_context_data(**kwargs)
    # print "context = %s" % str(context)
    if self.search_key in self.request.GET: context[self.search_key] = self.request.GET[search_key]
    # print "context = %s" % str(context)
    for filter_key in self.filter_on:
      if filter_key in self.request.GET: context[filter_key] = self.request.GET[filter_key]
    # print "context = %s" % str(context)
    return context

