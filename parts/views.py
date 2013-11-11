import vanilla 
from parts.models import (Assignment, Publisher, Part, Congregation, Category, GENDER_FEMALE, 
  CounselPoint, Setting)
from parts.forms import AssignmentForm, PublisherForm, AssistantForm, CounselForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
import datetime
import slick

from django.http import Http404
class CreateNewAssignments(vanilla.TemplateView):
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

class CreateCongregation(vanilla.View):pass
class ChangeCongregation(vanilla.View):pass

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

class Overview(BaseDateView):
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

class ListAssignments(BaseDateView):
  pass

class EditAssignments(BaseDateView):
  extra_context = {
    'enable_edit':True,
    'assistants':Category.objects.get(pk=17).suggestions,
  }

class AssignPart(vanilla.UpdateView):
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

class AssignAssistant(FormWithUserMixin, vanilla.UpdateView):
  model = Assignment
  form_class = AssistantForm
  template_name = "parts/assign_assistant.html"
  def form_valid(self, form):
    self.object = form.save()
    context = self.get_context_data(form=form)
    return self.render_to_response(context)

class ListPublishers(vanilla.ListView):
  model = Publisher
  def get_queryset(self):
    return Publisher.objects.filter(congregation = self.request.user.congregation).order_by('last_name')

class ShowPublisher(vanilla.DetailView):
  model = Publisher

class UpdatePublisher(vanilla.UpdateView):
  model = Publisher
  form_class = PublisherForm
  success_url = reverse_lazy('list_publishers')

class DeletePublisher(vanilla.DeleteView):
  model = Publisher
  success_url = reverse_lazy('list_publishers')

class CreatePublisher(vanilla.CreateView):
  model = Publisher
  form_class = PublisherForm

  def form_valid(self, form):
    self.object = form.save(commit=False)
    self.object.congregation = self.request.user.congregation
    self.object = form.save()
    return HttpResponseRedirect(reverse('show_publisher', kwargs={'pk':self.object.pk}))

class UpdateCounsel(slick.ExtraContextMixin, vanilla.UpdateView):
  model = Assignment
  form_class = CounselForm
  template_name = "parts/counsel_form.html"
  extra_context = {
    'counsel_point_list':CounselPoint.objects.all(),
    'my_setting_list':Setting.objects.all(),
  }


class SetForeignKey(vanilla.UpdateView):
  display_attribute = None
  def form_valid(self, form):
    self.object = form.save()
    print "self.object.next_counsel_point = %s" % str(self.object.next_counsel_point)
    try: msg = getattr(form.cleaned_data[self.fields[0]],self.display_attribute)
    except: msg = form.cleaned_data[self.fields[0]]
    return HttpResponse(msg)

class SetNextCounselPoint(SetForeignKey):
  model = Assignment
  fields = ['next_counsel_point']
  display_attribute = 'name'

class SetSetting(SetForeignKey):
  model = Assignment
  fields = ['setting']
  display_attribute = 'name'
# class Overview(TemplateView):
#   template_name = "overview.html"
#   pass

# class PublisherView(UpdateView):
#     model = Publisher
#     success_url = reverse_lazy('publisher')

# class AssignmentsView(CreateView):
#     model = Assignment
#     success_url = reverse_lazy('assignments')

