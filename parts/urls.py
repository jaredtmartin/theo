from django.conf.urls import patterns, url

from parts.views import (CreateNewAssignments, CreateCongregation, ChangeCongregation, 
  ListAssignments, Overview, EditAssignments, AssignPart, ShowPublisher, 
  UpdatePublisher, DeletePublisher, ListPublishers, CreatePublisher, AssignAssistant, 
  UpdateCounsel, SetNextCounselPoint, SetSetting)
#  For this project view and url names will follow verb_noun naming pattern.

urlpatterns = patterns('',
  url(r'^update_schedule/$',CreateNewAssignments.as_view(), name='create_assignments'),
  url(r'^congregation/create/$',CreateCongregation.as_view(), name='create_congregation'),
  url(r'^congregation/change/$',ChangeCongregation.as_view(), name='change_congregation'),
  url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', ListAssignments.as_view(), name="list_assignments"),
  url(r'^$',Overview.as_view(), name='overview'),
  url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/edit/$', EditAssignments.as_view(), name="edit_assignments"),

  url(r'^(?P<pk>\d+)/assign/$',AssignPart.as_view(), name='assign_part'),
  url(r'^(?P<pk>\d+)/assign-assistant/$',AssignAssistant.as_view(), name='assign_assistant_to_part'),
  
  url(r'^publishers/$',ListPublishers.as_view(), name='list_publishers'),
  url(r'^publisher/(?P<pk>\d+)/show/$',ShowPublisher.as_view(), name='show_publisher'),
  url(r'^publisher/(?P<pk>\d+)/edit/$',UpdatePublisher.as_view(), name='edit_publisher'),
  url(r'^publisher/(?P<pk>\d+)/delete/$',DeletePublisher.as_view(), name='delete_publisher'),
  url(r'^publisher/create/$',CreatePublisher.as_view(), name='create_publisher'),

  url(r'^part/(?P<pk>\d+)/counsel/$',UpdateCounsel.as_view(), name='update_counsel'),
  url(r'^part/(?P<pk>\d+)/next-counsel-point/', SetNextCounselPoint.as_view(), name='set_next_counsel_point'),
  url(r'^part/(?P<pk>\d+)/setting/', SetSetting.as_view(), name='set_setting'),
    



  # Example: /2012/nov/10/
  # url(r'^meeting/(?P<year>\d{4})/(?P<month>[-\w]+)/(?P<day>\d+)/$', ShowMeeting.as_view(), name='show_meeting'),
  # url(r'^meeting/(?P<year>\d{4})/(?P<month>[-\w]+)/(?P<day>\d+)/edit/$', ShowMeeting.as_view(), name='show_meeting'),
  # # url(r'^meeting/edit/$', EditMeeting.as_view(), name='edit_meeting'),
  # url(r'^(?P<pk>\d+)/$', EditTag.as_view(), name='edit_tag'),
 )