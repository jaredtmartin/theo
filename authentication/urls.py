from django.conf.urls import *
from views import UserUpdateView, SignUp, SignUpDone, SignUpConfirm, SignUpComplete
from forms import LoginForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm

urlpatterns = patterns('',
  url(r'^settings/$', UserUpdateView.as_view(), name="user_profile"),
  url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'authentication/login.html','authentication_form':LoginForm}, name='login'),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'authentication/logged_out.html'}, name='logout'),
  url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'authentication/password_change_form.html', 'password_change_form':PasswordChangeForm}, name='change_password'),
  url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'authentication/password_change_done.html'}, name='password_change_done'),
  url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', 
      {'template_name': 'authentication/password_reset_form.html', 'email_template_name': 'authentication/password_reset_email.html', 'password_reset_form':PasswordResetForm}, 
      name='password_reset'),
  url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'authentication/password_reset_done.html'}, name='password_reset_done'),
  url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'authentication/password_reset_confirm.html', 'set_password_form':SetPasswordForm}, name='password_reset_confirm'),
  url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'authentication/password_reset_complete.html'}, name='password_reset_complete'),
  # url(r'^signup/$', 'authentication.views.signup', 
      # {'template_name': 'authentication/signup_form.html', 'email_template_name': 'authentication/signup_email.html'}, name='signup'),
  url(r'^signup/$',SignUp.as_view(), name='signup'),
  url(r'^signup/done/$', SignUpDone.as_view(), name='signup_done'),
  # url(r'^signup/done/$', 'authentication.views.signup_done', {'template_name': 'authentication/signup_done.html'}, name='signup_done'),
  url(r'^signup/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', SignUpConfirm.as_view(), name='signup_confirm'),
  # url(r'^signup/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'authentication.views.signup_confirm', name='signup_confirm'),
  url(r'^signup/complete/$', SignUpComplete.as_view(), name='signup_complete'),
)