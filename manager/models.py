import re
import datetime
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _, ugettext_noop as _noop


def validate_url(url):
    if not re.match("^[a-zA-Z0-9-_]+$", url):
        raise ValidationError(_('URL can only contain letters or numbers'))


class Image(models.Model):
    type = models.CharField(_('Type'), max_length=200)
    url = models.URLField(_noop('URL'))
    cropping = models.CharField(_('Text'), max_length=200)

    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

class Adress(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    adress = models.CharField(_('Adress'), max_length=200)
    latitude = models.FloatField(_('Latitude'), validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(_('Longitude'), validators=[MinValueValidator(-180), MaxValueValidator(180)])

    def __unicode__(self):
        return u"%s (%s-%s)" % (self.name, self.latitude, self.longitude)

    class Meta:
        ordering = ['name']


class Event(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    date = models.DateField(_('Date'), help_text=_('Date of the event'))
    limit_proposal_date = models.DateField(_('Limit Proposal Date'), help_text=_('Date Limit of Talk Proposal'))
    url = models.CharField(_('URL'), max_length=200, help_text=_('URL for the event i.e. CABA'),
                           validators=[validate_url])
    external_url = models.URLField(_('External URL'), blank=True, null=True, default=None, help_text=_(
        'If you want to use other page for your event rather than eventoL\'s one, you can put the absolute url here'))
    email = models.EmailField(verbose_name=_('Email'))
    event_information = RichTextField(verbose_name=_('Event Information'), help_text=_('Event Information HTML'),
                                      blank=True, null=True)
    schedule_confirm = models.BooleanField(_('Schedule Confirm'), default=False)
    adress = models.ForeignKey(Adress, verbose_name=_('Adress'))
    image = models.ForeignKey(Image, verbose_name=_noop('Image'), blank=True, null=True)

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url
        return "/event/" + self.url + '/'

    @property
    def talk_proposal_is_open(self):
        return self.limit_proposal_date >= datetime.date.today()

    @property
    def registration_is_open(self):
        return self.date >= datetime.date.today()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.adress.name)

    def get_geo_info(self):
        return {
            "lat": self.adress.latitude,
            "lon": self.adress.longitude,
            "name": self.adress.name
        }

    class Meta:
        ordering = ['name']


class ContactMessage(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    message = models.TextField(verbose_name=_('Message'))

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')


class ContactType(models.Model):
    """
    For example:
        Name: Facebook
        Icon Class: fa-facebook-square
    """
    name = models.CharField(_('Name'), unique=True, max_length=200)
    icon_class = models.CharField(_('Icon Class'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Contact Type')
        verbose_name_plural = _('Contact Types')


class Contact(models.Model):
    type = models.ForeignKey(ContactType, verbose_name=_('Contact Type'))
    url = models.URLField(_noop('URL'))
    text = models.CharField(_('Text'), max_length=200)
    event = models.ForeignKey(Event, verbose_name=_noop('Event'), related_name='contacts')

    def __unicode__(self):
        return u"%s - %s" % (self.type.name, self.text)

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')


class EventoLUser(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), blank=True, null=True)
    event = models.ForeignKey(Event, verbose_name=_noop('Event'), help_text=_('Event you are going to collaborate'))
    assisted = models.BooleanField(_('Assisted'), default=False)

    def __unicode__(self):
        return str(self.user)

    class Meta:
        verbose_name = _('EventoL User')
        verbose_name_plural = _('EventoL User')


class Collaborator(models.Model):
    eventolUser = models.ForeignKey(EventoLUser, verbose_name=_('EventoL User'))
    assignation = models.CharField(_('Assignation'), max_length=200, blank=True, null=True,
                                   help_text=_('Assignations given to the user (i.e. Talks, Coffee...)'))
    time_availability = models.CharField(_('Time Availability'), max_length=200, blank=True, null=True, help_text=_(
        'Time gap in which you can help during the event. i.e. "All the event", "Morning", "Afternoon"...'))
    phone = models.CharField(_('Phone'), max_length=200, blank=True, null=True)
    address = models.CharField(_('Address'), max_length=200, blank=True, null=True)
    additional_info = models.CharField(_('Additional Info'), max_length=200, blank=True, null=True,
                                       help_text=_('Any additional info you consider relevant'))

    class Meta:
        verbose_name = _('Collaborator')
        verbose_name_plural = _('Collaborators')


class Attendee(models.Model):
    eventolUser = models.ForeignKey(EventoLUser, verbose_name=_('EventoL User'),blank=True, null=True)
    additional_info = models.CharField(_('Additional Info'), max_length=200, blank=True, null=True,
                                       help_text=_('Any additional info you consider relevant'))

    class Meta:
        verbose_name = _('Attendee')
        verbose_name_plural = _('Attendees')


class InstalationAttendee(models.Model):
    eventolUser = models.ForeignKey(EventoLUser, verbose_name=_('EventoL User'))
    installarion_additional_info = models.TextField(_('Additional Info'), blank=True, null=True,
                                                    help_text=_('i.e. Wath kind of PC are you bringing'))

    class Meta:
        verbose_name = _('Instalation Attendee')
        verbose_name_plural = _('Instalation Attendees')


class Installer(models.Model):
    installer_choices = (
        ('1', _('Beginner')),
        ('2', _('Medium')),
        ('3', _('Advanced')),
        ('4', _('Super Hacker'))
    )
    eventolUser = models.ForeignKey(EventoLUser, verbose_name=_('EventoL User'))
    level = models.CharField(_('Level'), choices=installer_choices, max_length=200,
                             help_text=_('Linux Knowledge level for an installation'))

    class Meta:
        verbose_name = _('Installer')
        verbose_name_plural = _('Installers')


class Speaker(models.Model):
    eventolUser = models.ForeignKey(EventoLUser, verbose_name=_('EventoL User'))

    class Meta:
        verbose_name = _('Speaker')
        verbose_name_plural = _('Speakers')

userTypes = {
    'Collaborators': Collaborator,
    'Attendees': Attendee,
    'Instalation Attendees': InstalationAttendee,
    'Speakers': Speaker,
    'Intallers': Installer
}


class Software(models.Model):
    software_choices = (
        ('OS', _('Operative System')),
        ('AP', _('Application')),
        ('SU', _('Support and Problem Fixing')),
        ('OT', _('Other'))
    )
    name = models.CharField(_('Name'), max_length=200)
    version = models.CharField(_('Version'), max_length=200)
    type = models.CharField(_('Type'), choices=software_choices, max_length=200)

    def __unicode__(self):
        return u"%s - %s v.%s" % (self.type, self.name, self.version)


class HardwareManufacturer(models.Model):
    name = models.CharField(_('Name'), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Hardware Manufacturer')
        verbose_name_plural = _('Hardware Manufacturers')


class Hardware(models.Model):
    hardware_choices = (
        ('MOB', _('Mobile')),
        ('NOTE', _('Notebook')),
        ('NET', _('Netbook')),
        ('TAB', _('Tablet')),
        ('DES', _('Desktop')),
        ('OTH', _('Other'))
    )
    type = models.CharField(_('Type'), choices=hardware_choices, max_length=200)
    manufacturer = models.ForeignKey(HardwareManufacturer, verbose_name=_('Manufacturer'), blank=True, null=True)
    model = models.CharField(_('Model'), max_length=200, blank=True, null=True)
    serial = models.CharField(_('Serial'), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return u"%s, %s, %s" % (self.type, self.manufacturer, self.model)


class Activity(models.Model):
    event = models.ForeignKey(Event, verbose_name=_noop('Event'))
    title = models.CharField(_('Title'), max_length=50, blank=True, null=True)
    long_description = models.TextField(_('Long Description'))
    confirmed = models.BooleanField(_('Confirmed'), default=False)
    abstract = models.TextField(_('Abstract'), help_text=_('Short idea of the talk (Two or three sentences)'))

    def __unicode__(self):
        return u"%s: %s" % (self.event, self.title)

    class Meta:
        ordering = ['title']
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')


class TalkType(models.Model):
    """
    Type of talk. For example: Talk, Workshop, Debate, etc.
    """
    name = models.CharField(_('Name'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Talk Type')
        verbose_name_plural = _('Talk Types')


class TalkProposal(models.Model):
    level_choices = (
        ('1', _('Beginner')),
        ('2', _('Medium')),
        ('3', _('Advanced')),
    )
    activity = models.ForeignKey(Activity, verbose_name=_noop('Activity'))
    type = models.ForeignKey(TalkType, verbose_name=_('Type'))
    image = models.ForeignKey(Image, verbose_name=_noop('Image'), blank=True, null=True)
    speakers_names = models.CharField(_('Speakers Names'), max_length=600,
                                      help_text=_("Comma separated speaker's names"))
    speakers_email = models.CharField(_('Speakers Emails'), max_length=600,
                                      help_text=_("Comma separated speaker's emails"))
    labels = models.CharField(_('Labels'), max_length=200,
                              help_text=_('Comma separated tags. i.e. Linux, Free Software, Debian'))
    presentation = models.FileField(_('Presentation'), upload_to='talks', blank=True, null=True, help_text=_(
        'Any material you are going to use for the talk (optional, but recommended)'))
    level = models.CharField(_('Level'), choices=level_choices, max_length=100,
                             help_text=_("The talk's Technical level"))

    def get_absolute_url(self):
        return "/event/" + self.activity.event.url + '/talk/detail/proposal/' + str(self.id)

    def __unicode__(self):
        return u"%s: %s" % (self.activity.event, self.activity.title)

    class Meta:
        verbose_name = _('Talk Proposal')
        verbose_name_plural = _('Talk Proposals')


class Room(models.Model):
    event = models.ForeignKey(Event, verbose_name=_noop('Event'))
    name = models.CharField(_('Name'), max_length=200, help_text=_('i.e. Classroom 256'))
    for_type = models.ForeignKey(TalkType, verbose_name=_('For talk type'),
                                 help_text=_('The type of talk the room is going to be used for.'))

    def __unicode__(self):
        return u"%s - %s" % (self.event.name, self.name)

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ['name']


class Talk(models.Model):
    talk_proposal = models.OneToOneField(TalkProposal, verbose_name=_('TalkProposal'), blank=True, null=True)
    room = models.ForeignKey(Room, verbose_name=_('Room'))
    start_date = models.DateTimeField(_('Start Time'))
    end_date = models.DateTimeField(_('End Time'))

    def __unicode__(self):
        return u"%s - %s (%s - %s)" % (self.talk_proposal.activity.event.name, self.talk_proposal.activity.title,
                                       self.start_date.strftime("%H:%M"), self.end_date.strftime("%H:%M"))

    def __cmp__(self, other):
        return -1 if self.start_date.time() < other.start_date.time() else 1

    def get_absolute_url(self):
        return "/event/" + self.talk_proposal.activity.event.url + '/talk/detail/talk/' + str(self.id)

    def schedule(self):
        return u"%s - %s" % (self.start_date.strftime("%H:%M"), self.end_date.strftime("%H:%M"))

    def get_schedule_info(self):
        talk = {
            'room': self.room.name,
            'start_date': self.start_date.strftime('%m/%d/%Y %H:%M'),
            'end_date': self.end_date.strftime('%m/%d/%Y %H:%M'),
            'title': self.talk_proposal.activity.title,
            'speakers': self.talk_proposal.speakers_names,
            'type': self.talk_proposal.type.name
        }
        return talk

    @classmethod
    def filter_by(cls, queryset, field, value):
        if field == 'event':
            return queryset.filter(talk_proposal__activity__event__pk=value)
        return queryset

    class Meta:
        verbose_name = _('Talk')
        verbose_name_plural = _('Talks')


class Comment(models.Model):
    created = models.DateTimeField()
    body = models.TextField()
    activity = models.ForeignKey(Activity, verbose_name=_noop('Activity'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    def __unicode__(self):
        return u"%s: %s" % (self.user, self.activity)

    @classmethod
    def filter_by(cls, queryset, field, value):
        if field == 'event':
            return queryset.filter(activity__event__pk=value)
        return queryset

    def save(self, *args, **kwargs):
        """Email when a comment is added."""
        # TODO: Email when a comment is added.
        if "notify" in kwargs:
            del kwargs["notify"]
        super(Comment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class Installation(models.Model):
    hardware = models.ForeignKey(Hardware, verbose_name=_('Hardware'), blank=True, null=True)
    software = models.ForeignKey(Software, verbose_name=_('Software'), blank=True, null=True)
    attendee = models.ForeignKey(InstalationAttendee, verbose_name=_('Attendee'),
                                 help_text=_('The owner of the installed hardware'))
    installer = models.ForeignKey(Installer, verbose_name=_('Installer'), related_name='installed_by', blank=True,
                                  null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True,
                             help_text=_('Any information or trouble you found and consider relevant to document'))

    def __unicode__(self):
        return u"%s, %s, %s" % (self.attendee, self.hardware, self.software)

    @classmethod
    def filter_by(cls, queryset, field, value):
        if field == 'event':
            return queryset.filter(attendee__eventolUser__event__pk=value)
        return queryset

    class Meta:
        verbose_name = _('Installation')
        verbose_name_plural = _('Installations')


def getUserChoice():
    user_choice = []
    for key in userTypes.keys():
        user_choice.append((key, key))
    return user_choice