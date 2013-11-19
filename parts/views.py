import vanilla 
from parts.models import (Assignment, Publisher, Part, Congregation, Category, GENDER_FEMALE, 
  CounselPoint, Setting)
from parts.forms import AssignmentForm, PublisherForm, AssistantForm, CounselForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
import datetime
import slick
from django.http import Http404
from xhtml2pdf import pisa
import cStringIO as StringIO


import os
from django.conf import settings
from django.template import Context
from django.template.loader import get_template

class CreateNewAssignments(slick.LoginRequiredMixin, vanilla.TemplateView):
  template_name = "parts/new_assignments.html"
  def get(self, request, *args, **kwargs):
    parts = Part.objects.filter(date__gte=datetime.date.today()).exclude(assignments__isnull=False).order_by('date')
    congregations = Congregation.objects.all()
    assistants = Category.objects.get(pk=17)
    for part in parts:
      for cong in congregations:
        pub = part.category.suggestions[0]
        if pub.gender == GENDER_FEMALE or part.category_id == 12: ass = assistants.assistant_suggestions(pub.pk)[0]
        else: ass=None
        Assignment.objects.create(
          part=part, 
          congregation=cong, 
          date=part.date+datetime.timedelta(days=cong.weekday),
          publisher=part.category.suggestions[0],
          assistant=ass, 
          # category = part.category,
        )
    context = self.get_context_data(parts=parts, assignments=Assignment.objects.filter(part__in=parts))
    return self.render_to_response(context)

class CreateCongregation(slick.LoginRequiredMixin, vanilla.View):pass
class ChangeCongregation(slick.LoginRequiredMixin, vanilla.View):pass

class BaseDateView(slick.ListView):
  model = Assignment
  filter_on = ['date']
  extra_context = {
  'date':'get_self_date',
  'next_date':'get_next_date',
  'previous_date':'get_previous_date',
  }
  year=None
  month=None
  day=None
  year_format = "%Y"
  month_format = "%m"
  day_format = "%d"
  date_delim = "__"
  def get_queryset(self):
    return super(BaseDateView, self).get_queryset().order_by('part__order')
  def _date_from_string(self, year, month, day,
    year_format="", month_format="", 
    day_format="", delim=""):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and possibly day; raise a 404 for an invalid date.
    """
    if not year_format: year_format=self.year_format
    if not month_format: month_format=self.month_format
    if not day_format: day_format=self.day_format
    if not delim: delim=self.date_delim
    format = delim.join((year_format, month_format, day_format))
    datestr = delim.join((year, month, day))
    try:
        return datetime.datetime.strptime(datestr, format).date()
    except ValueError:
        raise Http404(u"Invalid date string '%(datestr)s' given format '%(format)s'" % {
            'datestr': datestr,
            'format': format,
        })
  def filter_congregation(self, qs, value):
    return qs.filter(congregation=self.request.user.congregation)
  def get_year(self):
    "Return the year for which this view should display data"
    year = self.year
    if year is None:
      try:
        year = self.kwargs['year']
      except KeyError:
        try:
          year = self.request.GET['year']
        except KeyError:
          raise Http404(u"No year specified")
    return year
  def get_month(self):
    "Return the month for which this view should display data"
    month = self.month
    if month is None:
      try:
        month = self.kwargs['month']
      except KeyError:
        try:
          month = self.request.GET['month']
        except KeyError:
          raise Http404(_(u"No month specified"))
    return month
  def get_day(self):
    "Return the day for which this view should display data"
    day = self.day
    if day is None:
      try:
        day = self.kwargs['day']
      except KeyError:
        try:
          day = self.request.GET['day']
        except KeyError:
          raise Http404(_(u"No day specified"))
    return day
  def get_next_date(self): 
    try: return self.model.objects.filter(congregation=self.request.user.congregation, date__gt=self.date).order_by('date')[0].date
    except IndexError: return None
  def get_previous_date(self): 
    try: return self.model.objects.filter(congregation=self.request.user.congregation, date__lt=self.date).order_by('-date')[0].date
    except IndexError: return None
  def get_self_date(self):
    return self.date
  def get_date(self):
    return self._date_from_string(year=self.get_year(), month=self.get_month(), day=self.get_day())
  def filter_date(self, qs, value):
    self.date = self.get_date()
    # print "self.date = %s" % str(self.date)
    # print "type(self.get_date()) = %s" % str(type(self.get_date()))
    # print "Assignment.objects.get(pk=1).date==self.date = %s" % str(Assignment.objects.get(pk=1).date==self.date)
    # print "qs = %s" % str(qs)
    # print "qs.filter(date=self.date) = %s" % str(qs.filter(date=self.date))
    return qs.filter(date = self.date)

class Overview(slick.LoginRequiredMixin, BaseDateView):
  def get_date(self):
    # First we get the date for monday
    today = datetime.date.today()
    monday = today + datetime.timedelta(days=-today.weekday())
    print "today = %s" % str(today)
    print "monday = %s" % str(monday)
    # Then add congregations weekday to get date of meeting
    # try: 
    date = monday + datetime.timedelta(days=self.request.user.congregation.weekday)
    print "type(date) = %s" % str(type(date))
    print "date = %s" % str(date)
    return date
    # except: return monday
class PublicSchedule(Overview):
  template_name = "parts/public_schedule.html"

class ListAssignments(slick.LoginRequiredMixin, BaseDateView):
  pass

class EditAssignments(slick.LoginRequiredMixin, BaseDateView):
  extra_context = {
    'enable_edit':True,
    'assistants':Category.objects.get(pk=17).suggestions,
  }

class AssignPart(slick.LoginRequiredMixin, vanilla.UpdateView):
  model = Assignment
  form_class = AssignmentForm
  template_name = "parts/assign_part.html"
  def form_valid(self, form):
    self.object = form.save()
    context = self.get_context_data(form=form)
    return self.render_to_response(context)

class FormWithUserMixin(object):
  def get_form(self, data=None, files=None, **kwargs):
    cls = self.get_form_class()
    kwargs['user'] = self.request.user
    return cls(data=data, files=files, **kwargs)

class AssignAssistant(slick.LoginRequiredMixin, FormWithUserMixin, vanilla.UpdateView):
  model = Assignment
  form_class = AssistantForm
  template_name = "parts/assign_assistant.html"
  def form_valid(self, form):
    self.object = form.save()
    context = self.get_context_data(form=form)
    return self.render_to_response(context)

class ListPublishers(slick.LoginRequiredMixin, vanilla.ListView):
  model = Publisher
  def get_queryset(self):
    return Publisher.objects.filter(congregation = self.request.user.congregation).order_by('last_name')

class ShowPublisher(slick.LoginRequiredMixin, vanilla.DetailView):
  model = Publisher

class UpdatePublisher(slick.LoginRequiredMixin, vanilla.UpdateView):
  model = Publisher
  form_class = PublisherForm
  success_url = reverse_lazy('list_publishers')

class DeletePublisher(slick.LoginRequiredMixin, vanilla.DeleteView):
  model = Publisher
  success_url = reverse_lazy('list_publishers')

class CreatePublisher(slick.LoginRequiredMixin, vanilla.CreateView):
  model = Publisher
  form_class = PublisherForm

  def form_valid(self, form):
    self.object = form.save(commit=False)
    self.object.congregation = self.request.user.congregation
    self.object = form.save()
    return HttpResponseRedirect(reverse('show_publisher', kwargs={'pk':self.object.pk}))

class UpdateCounsel(slick.LoginRequiredMixin, slick.ExtraContextMixin, vanilla.UpdateView):
  model = Assignment
  form_class = CounselForm
  template_name = "parts/counsel_form.html"
  extra_context = {
    'counsel_point_list':CounselPoint.objects.all(),
    'my_setting_list':Setting.objects.all(),
  }
  def form_valid(self, form):
    self.object = form.save()
    if self.object.next_counsel_point and self.object.publisher:
      self.object.publisher.counsel_point = self.object.next_counsel_point
      self.object.publisher.save()
    if self.request.is_ajax(): return HttpResponse("AOK")
    return HttpResponseRedirect(self.get_success_url())


class SetForeignKey(slick.LoginRequiredMixin, vanilla.UpdateView):
  display_attribute = None
  def form_valid(self, form):
    self.object = form.save()
    try: msg = getattr(form.cleaned_data[self.fields[0]],self.display_attribute)
    except: msg = form.cleaned_data[self.fields[0]]
    return HttpResponse(msg)

class SetNextCounselPoint(SetForeignKey):
  model = Assignment
  fields = ['next_counsel_point']
  display_attribute = 'name'
  def form_valid(self, form):
    response = super(SetNextCounselPoint, self).form_valid(form)
    print "self.object.publisher = %s" % str(self.object.publisher)
    if self.object.publisher: 
      self.object.publisher.counsel_point = self.object.next_counsel_point
      self.object.publisher.save()
    return response

class SetSetting(SetForeignKey):
  model = Assignment
  fields = ['setting']
  display_attribute = 'name'




# Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
def link_callback(uri, rel):
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                    'media URI must start with %s or %s' % \
                    (sUrl, mUrl))
    return path


class PisaMixin(object):
  def render_to_pdf(self, context_dict):
    template = get_template(self.get_template_names()[0])
    context = Context(context_dict)
    html  = template.render(context)
    # result = StringIO.StringIO()
    # pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), dest=result, link_callback=fetch_resources)
    # if not pdf.err:
    #   return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    # return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
    f=open('/tmp/workfile', 'w')
    file = open(os.path.join(settings.MEDIA_ROOT, 'test.pdf'), "w+b")
    pisaStatus = pisa.CreatePDF(html, dest=file, link_callback = link_callback)

    # Return PDF document through a Django HTTP response
    file.seek(0)
    pdf = file.read()
    file.close()            # Don't forget to close the file handle
    return HttpResponse(pdf, mimetype='application/pdf')


    # Prepare context
    # data = {}
    # data['today'] = datetime.date.today()
    # data['farmer'] = 'Old MacDonald'
    # data['animals'] = [('Cow', 'Moo'), ('Goat', 'Baa'), ('Pig', 'Oink')]

    # # Render html content through html template with context
    # template = get_template('lyrics/oldmacdonald.html')
    # html  = template.render(Context(data))

    # # Write PDF to file
    # file = open(os.join(settings.MEDIA_ROOT, 'test.pdf'), "w+b")
    # pisaStatus = pisa.CreatePDF(html, dest=file,
    #         link_callback = link_callback)

    # # Return PDF document through a Django HTTP response
    # file.seek(0)
    # pdf = file.read()
    # file.close()            # Don't forget to close the file handle
    # return HttpResponse(pdf, mimetype='application/pdf')

class PisaList(PisaMixin, vanilla.ListView):
  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    paginate_by = self.get_paginate_by()

    if not self.allow_empty and not queryset.exists():
        raise Http404
    self.object_list = queryset
    context = self.get_context_data(
        page_obj=None,
        is_paginated=False,
        paginator=None,
    )
    return self.render_to_pdf(context)

class PrintSchedule(vanilla.ListView):
  # model = Assignment
  template_name = "parts/print_schedule.html"
  def get_queryset(self):
    return Assignment.objects.filter(date__gte=datetime.date.today(), congregation=self.request.user.congregation).order_by('date','part__order')
