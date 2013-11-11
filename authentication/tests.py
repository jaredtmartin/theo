from vanilla.tests import BaseTestCase as VanillaBaseTestCase
from vanilla.tests import InstanceOf
from django.conf import settings
from django.test.client import Client
from authentication.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from authentication.forms import (UserForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, 
  SimpleUserCreationFormWithFullName)
from authentication.views import UserUpdateView, SignUp, SignUpDone, SignUpComplete
from django.core import mail

class BaseTestCase(VanillaBaseTestCase):
  def login(self, username='jaredtmartin@gmail.com', password='t1bur0n'):
    response = self.c.post(reverse('login'), {'username': username, 'password': password})
    self.assertEqual(response.status_code, 302)
  def setUp(self):
    settings.DEBUG = True
    self.c = Client()
    self.login()
    self.me = User.objects.get(pk=1)
  def assertMessages(self, response, expected):
    messages = [str(msg) for msg in response.context['messages']]
    for msg in messages: 
      self.assertTrue(msg in expected, "context contains unexpected message: '%s'" % msg)
    for msg in expected: 
      self.assertTrue(msg in messages, "context missing message: '%s'" % msg)

class BaseTestCaseAsGuest(BaseTestCase):
  def setUp(self):
    settings.DEBUG = True
    self.c = Client()
    self.me = User.objects.get(pk=1)

class TestAuth(BaseTestCase):
  fixtures = ['fixtures/test_fixture.json']
  def test_logging_in(self):
    pass
  def test_logout(self):
    response = self.c.get(reverse('logout'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/logged_out.html')
    self.assertContext(response, {
      'site_name': u'example.com',
      'site': InstanceOf(Site),
      'title': u'Logged out'
      })
    self.assertMessages(response,[])
  def test_user_update_view(self):
    response = self.c.get(reverse('user_profile'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, ['authentication/user_form.html'])
    self.assertContext(response, {
      'form':InstanceOf(UserForm),
      'object':User.objects.get(pk=1),
      'user':User.objects.get(pk=1),
      'view':InstanceOf(UserUpdateView),
      })
    self.assertMessages(response,[])
    response = self.c.post(reverse('user_profile'), {
      'city':'Richmond', 
      'state':'VA', 
      'email':'fredflintstone@home.com',
      'first_name':'Fred',
      'last_name':'Flintstone',
      'phone':'987-654-3210',
      'street':'3712 Echoway Rd.'
    })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, ['authentication/user_form.html'])
    u=User.objects.get(pk=1)
    self.assertContext(response, {
      'form':InstanceOf(UserForm),
      'object':u,
      'user':u,
      'view':InstanceOf(UserUpdateView),
      })
    self.assertEqual(u.city,'Richmond')
    self.assertEqual(u.state,'VA')
    self.assertEqual(u.email,'fredflintstone@home.com')
    self.assertEqual(u.first_name,'Fred')
    self.assertEqual(u.last_name,'Flintstone')
    self.assertEqual(u.phone,'987-654-3210')
    self.assertEqual(u.street,'3712 Echoway Rd.')
    self.assertMessages(response,['The changes to your profile have been made successfully.'])
  def test_password_change(self):
    response = self.c.get(reverse('change_password'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_change_form.html')
    self.assertContext(response, {
      'form':InstanceOf(PasswordChangeForm),
      })
    response = self.c.post(reverse('change_password'), 
      {'old_password':'t1bur0n','new_password1':'pass','new_password2':'pass'})
    self.assertEqual(response.status_code, 302)
  def test_password_change_with_bad_password(self):
    response = self.c.post(reverse('change_password'), 
      {'old_password':'wrong','new_password1':'pass','new_password2':'pass'})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_change_form.html')
    self.assertContext(response, {
      'form':InstanceOf(PasswordChangeForm),
      })
    self.assertMessages(response,[])
  def test_password_change_with_nonmatching_passwords(self):
    response = self.c.post(reverse('change_password'), 
      {'old_password':'t1bur0n','new_password1':'pass','new_password2':'PASS'})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_change_form.html')
    self.assertContext(response, {
      'form':InstanceOf(PasswordChangeForm),
      })
    self.assertMessages(response,[])
  def test_password_change_done(self):
    response = self.c.get(reverse('password_change_done'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_change_done.html')
    self.assertContext(response, {})
  def test_password_reset(self):
    response = self.c.get(reverse('password_reset'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_reset_form.html')
    self.assertContext(response, {
      'form':InstanceOf(PasswordResetForm)
    })
    response = self.c.post(reverse('password_reset'),{'email':'jaredtmartin@gmail.com'})
    # print "response.__dict__ = %s" % str(response.__dict__)
    # print "response.context = %s" % str(response.context)
    # print "response.context[0]['token'] = %s" % str(response.context[0]['token'])
    self.assertEqual(response.status_code, 302)
    # Asserts that we got the email
    self.assertEqual(len(mail.outbox), 1)
    # Verify that the subject of the first message is correct.
    # print "mail.outbox[0].__dict__ = %s" % str(mail.outbox[0].__dict__)
    self.assertEqual(mail.outbox[0].subject, 'Password reset on example.com')
    token = response.context[0]['token']
    uid = response.context[0]['uid']
    response = self.c.get(reverse('password_reset_confirm', kwargs={'token':token,'uidb36':uid}))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_reset_confirm.html')
    self.assertContext(response, {
      'form': InstanceOf(SetPasswordForm),
      'validlink':True,
      })
    response = self.c.post(reverse('password_reset_confirm', 
      kwargs={'token':token,'uidb36':uid}), {'new_password1':'pass','new_password2':'pass'})
    # print "response.context = %s" % str(response.context)
    self.assertEqual(response.status_code, 302)

  def test_password_reset_complete(self):
    response = self.c.get(reverse('password_reset_complete'))
    # print "type(response) = %s" % str(type(response))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, 'authentication/password_reset_complete.html')
    self.assertContext(response, {'login_url': '/auth/login/'})

  def test_signup(self):
    response = self.c.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, ['authentication/signup_form.html'])
    self.assertContext(response, {
      'form':InstanceOf(SimpleUserCreationFormWithFullName),
      'view':InstanceOf(SignUp),
    })
    response = self.c.post(reverse('signup'),
      {'email':'fred@home.com','first_name':'Fred','last_name':'Flintstone',
      'password1':'pass','password2':'pass'})
    self.assertEqual(response.status_code, 302)
    token = response.context['token']
    uid = response.context['uid']

    response = self.c.get(reverse('signup_done'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, ['authentication/signup_done.html'])
    self.assertContext(response, {'view': InstanceOf(SignUpDone)})
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].subject, 'Confirmation link sent on example.com')
    response = self.c.get(reverse('signup_confirm', kwargs={'token':token,'uidb36':uid}))
    self.assertEqual(response.status_code, 302)
    response = self.c.get(reverse('signup_complete'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.template_name, ['authentication/signup_complete.html'])
