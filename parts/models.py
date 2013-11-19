from django.db import models
# # from django.contrib.auth.models import settings.AUTH_USER_MODEL
# from django.conf import settings
from django.conf import settings


MONDAY=0
TUESDAY=1
WEDNESDAY=2
THURSDAY=3
FRIDAY=4
SATURDAY=5
SUNDAY=6
DAYS_OF_WEEK=(
  (MONDAY,'Monday'),
  (TUESDAY,'Tuesday'),
  (WEDNESDAY,'Wednesday'),
  (THURSDAY,'Thursday'),
  (FRIDAY,'Friday'),
  (SATURDAY,'Saturday'),
  (SUNDAY,'Sunday'),
)
class Meeting(models.Model):
  name = models.CharField(max_length=64)
  order = models.IntegerField()
  def __unicode__(self): return self.name

class Category(models.Model):
  name = models.CharField(max_length=64)
  meeting = models.ForeignKey(Meeting)
  def __unicode__(self): return self.name
  def assistant_suggestions(self, ex, start_date=None):
    return Publisher.objects.raw("""
      select `parts_publisher`.*
      FROM `parts_publisher`
      LEFT OUTER JOIN `parts_publisher_categories` ON (`parts_publisher`.`id` = `parts_publisher_categories`.`publisher_id`)
      
      left outer join (
        SELECT `parts_publisher`.`id` as publisher_id,  MAX(`parts_assignment`.`date`) AS `last` 
        FROM `parts_publisher` 
        LEFT OUTER JOIN `parts_assignment` ON (`parts_publisher`.`id` = `parts_assignment`.`assistant_id`) 
        group by `parts_publisher`.`id`
        ) as assignments on (`parts_publisher`.`id` = `assignments`.`publisher_id`) 
      left outer join (
        SELECT `parts_publisher`.`id` as publisher_id,  MAX(`parts_assignment`.`date`) AS `last` 
        FROM `parts_publisher` 
        LEFT OUTER JOIN `parts_assignment` ON (`parts_publisher`.`id` = `parts_assignment`.`publisher_id`) 
        ) as all_assignments on (`parts_publisher`.`id` = `assignments`.`publisher_id`) 
      where parts_publisher_categories.category_id=%s and `parts_publisher`.`id` != %s
      order by assignments.last, all_assignments.last;
      """ % (self.pk, ex)) 
  
  @property
  def suggestions(self, start_date=None):
    return Publisher.objects.raw("""
      select `parts_publisher`.*
      FROM `parts_publisher`
      LEFT OUTER JOIN `parts_publisher_categories` ON (`parts_publisher`.`id` = `parts_publisher_categories`.`publisher_id`)
      left outer join (
        SELECT `parts_publisher`.`id` as publisher_id,  MAX(`parts_assignment`.`date`) AS `last` 
        FROM `parts_publisher` 
        LEFT OUTER JOIN `parts_assignment` ON (`parts_publisher`.`id` = `parts_assignment`.`publisher_id`) 
        LEFT OUTER JOIN `parts_part` ON (`parts_part`.`id` = `parts_assignment`.`part_id`) 
        WHERE `parts_part`.`category_id` = %s
        GROUP BY `parts_publisher`.`id`
        ) as assignments on (`parts_publisher`.`id` = `assignments`.`publisher_id`) 
      left outer join (
        SELECT `parts_publisher`.`id` as publisher_id,  MAX(`parts_assignment`.`date`) AS `last` 
        FROM `parts_publisher` 
        LEFT OUTER JOIN `parts_assignment` ON (`parts_publisher`.`id` = `parts_assignment`.`publisher_id`) 
        GROUP BY `parts_publisher`.`id`
        ) as all_assignments on (`parts_publisher`.`id` = `all_assignments`.`publisher_id`) 
      where parts_publisher_categories.category_id=%s
      group by `parts_publisher`.`id`
      order by assignments.last, all_assignments.last;
      """ % (self.pk, self.pk)) 


    # You can't use order_by related model with distinct(), So I do this:
    # return Publisher.objects.filter(assignments__part__category_id=self.id).annotate(last_assignment=models.Max('assignments__date')).order_by('last_assignment')
    # last_assigned = Publisher.objects.filter(assignments__part__category_id=self.id).annotate(last_assignment=Max('assignments__date')).order_by('last_assignment')
    # never_assigned = Publisher.objects.filter(categories__id=9).exclude(assignments__part__category_id=self.id)
    # return list(never_assigned) + list(last_assigned)
    # return self.publishers.annotate(models.Max("assignments__date")).order_by('assignments__date__max')
    # return Publisher.objects.raw("select parts_publisher.*, max(parts_assignment.date) as last_date from parts_part inner join parts_assignment on part_id=parts_part.id inner join parts_publisher on publisher_id=parts_publisher.id where category_id=%s group by publisher_id order by last_date" % self.pk)
  # @property
  # def top_suggestion(self, start_date=None):
  #   return Publisher.objects.raw("select parts_publisher.*, max(parts_assignment.date) as last_date from parts_part inner join parts_assignment on part_id=parts_part.id inner join parts_publisher on publisher_id=parts_publisher.id where category_id=%s group by publisher_id order by last_date limit 1" % self.pk)[0]
class Setting(models.Model):
  name = models.CharField(max_length=64)
  def __unicode__(self): return self.name

class CounselPoint(models.Model):
  name = models.CharField(max_length=64)
  def __unicode__(self): return self.name

class Congregation(models.Model):
  name = models.CharField(max_length=64)
  weekday = models.IntegerField(choices=DAYS_OF_WEEK)
  admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin')
  schedule_public = models.BooleanField(default=False)
  school_overseer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='school_overseer_for', null=True, blank=True)
  coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coordinator_for', null=True, blank=True)
  sound_scheduler = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sound_servant_for', null=True, blank=True)
  stage_scheduler = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stage_scheduler_for', null=True, blank=True)
  attendants_scheduler = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='attendants_scheduler_for', null=True, blank=True)
  auto_fill_school = models.BooleanField(default=True)
  auto_fill_service_meeting = models.BooleanField(default=True)
  # num_microphone_handlers = models.IntegerField(default=2)
  # num_attendants = models.IntegerField(default=2)
  def __unicode__(self): return self.name

GENDER_MALE=1
GENDER_FEMALE=2
GENDERS=(
  (GENDER_MALE,'Male'),
  (GENDER_FEMALE,'Female')
  )
class Publisher(models.Model):
  def __unicode__(self): return self.full_name
  last_name = models.CharField(max_length=64, default="")
  first_name = models.CharField(max_length=64, default="")
  gender = models.IntegerField(choices=GENDERS, default=GENDER_MALE)
  congregation = models.ForeignKey(Congregation, related_name='publishers')
  counsel_point = models.ForeignKey(CounselPoint, related_name='publishers', blank=True, null=True)
  categories = models.ManyToManyField(Category, related_name='publishers')
  @property
  def full_name(self): return "%s %s" % (self.first_name, self.last_name)
  @property
  def order_name(self): return "%s, %s" % (self.last_name, self.first_name)

class Part(models.Model):
  def __unicode__(self): 
    if self.theme: return self.theme
    else: return self.material
  theme = models.CharField(max_length=64, default="", blank=True)
  material = models.CharField(max_length=64, default="", blank=True)
  order = models.IntegerField()
  date = models.DateField()
  category = models.ForeignKey(Category, related_name='parts')

class Assignment(models.Model):
  @property
  def title(self): return self.__unicode__
  def __unicode__(self): return self.part.theme or self.part.material
  date = models.DateField()
  part = models.ForeignKey(Part, related_name='assignments')
  # category = models.ForeignKey(Category, related_name='assignments')
  counsel_point = models.ForeignKey(CounselPoint, related_name='assignments', null=True, blank=True)
  publisher = models.ForeignKey(Publisher, related_name='assignments', null=True, blank=True)
  setting = models.ForeignKey(Setting, related_name='assignments', null=True, blank=True)
  assistant = models.ForeignKey(Publisher, related_name='assistant_assignments', null=True, blank=True)
  counsel = models.CharField(max_length=128, default="", blank=True)
  timing = models.CharField(max_length=8, default="", blank=True)
  congregation = models.ForeignKey(Congregation, related_name='assignments')
  next_counsel_point = models.ForeignKey(CounselPoint, null=True, blank=True, related_name="next")
  exercises_done = models.NullBooleanField(blank=True)
  @property
  def category(self): return self.part.category
  @property
  def suggestions(self): 
    # l=None
    # # For Service Meeting Parts, try to use elders first
    # if self.category.pk == 9: l = Publisher.objects.filter(categories__id=11).order_by('assignments__date').distinct()[:10]
    return self.part.category.suggestions
