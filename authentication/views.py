from authentication.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from authentication.forms import UserForm, SimpleUserCreationFormWithFullName
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django.utils.http import urlquote, base36_to_int
from django.contrib.sites.models import Site
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
# from vanilla import FormView
import vanilla
from django.views.decorators.csrf import csrf_protect

class SignUp(vanilla.CreateView):
  model = User
  template_name = 'authentication/signup_form.html'
  email_template_name = 'authentication/signup_email.html'
  token_generator = default_token_generator
  form_class = SimpleUserCreationFormWithFullName
  def form_valid(self, form):
    opts = {}
    opts['use_https'] = self.request.is_secure()
    opts['token_generator'] = self.token_generator
    opts['email_template_name'] = self.email_template_name
    if not Site._meta.installed:
        opts['domain_override'] = RequestSite(request).domain
    form.save(**opts)
    messages.success(self.request, 'Congratulations! You accounts as been created successfully.')
    return HttpResponseRedirect(reverse('signup_done'))

class SignUpDone(vanilla.TemplateView):
  template_name = 'authentication/signup_done.html'

class SignUpConfirm(vanilla.View):
  token_generator = default_token_generator
  def get(self, request, token, uidb36):
    assert uidb36 is not None and token is not None #checked par url
    try:
      uid_int = base36_to_int(uidb36)
    except ValueError:
      raise Http404
    user = get_object_or_404(User, id=uid_int)
    context = RequestContext(request)
    if self.token_generator.check_token(user, token):
      context['validlink'] = True
      user.is_active = True
      user.save()
    else:
      context['validlink'] = False
    return HttpResponseRedirect(reverse('signup_complete'))

class SignUpComplete(vanilla.TemplateView):
  template_name = 'authentication/signup_complete.html'

class UserUpdateView(UpdateView):
  model=User
  form_class = UserForm
  template_name = "authentication/user_form.html"
  # url = reverse('tags')
  def get_object(self, queryset=None):
        return self.request.user
  # def get_context_data(self, **kwargs):
  #   kwargs.update({
  #     'user_profile_form':UserProfileForm(instance=self.object.get_profile()),
  #   })
  #   return super(UserUpdateView, self).get_context_data(**kwargs)
  def form_invalid(self, form):
    return self.render_to_response(self.get_context_data(form=form))
  def form_valid(self, form):
    # user_profile_form.save()
    self.object = form.save()
    messages.success(self.request, 'The changes to your profile have been made successfully.')
    return self.render_to_response(self.get_context_data(form=form))
    # return super(UserUpdateView, self).form_valid(form)
  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    # user_profile_form = UserProfileForm(self.request.POST, instance=self.object.get_profile())
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)