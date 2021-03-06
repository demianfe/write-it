from django.db import models
from django.db.models.signals import post_save
from nuntium.models import WriteItInstance, OutboundMessage, Answer, read_template_as_string
from django.utils.translation import ugettext_lazy as _


default_content_template = read_template_as_string(
    'templates/mailit/mails/content_template.txt',
    file_source_path=__file__,
    )


class MailItTemplate(models.Model):
    subject_template = models.CharField(
        max_length=255,
        default="{subject}",
        help_text=_('You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}'),
        )
    content_template = models.TextField(
        help_text=_('You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}'),
        blank=True,
        )
    content_html_template = models.TextField(
        blank=True,
        help_text=_('You can use {subject}, {content}, {person}, {author}, {site_url}, {site_name}, and {owner_email}'),
        )
    writeitinstance = models.OneToOneField(WriteItInstance, related_name='mailit_template')

    def get_content_template(self):
        return self.content_template or default_content_template


def new_write_it_instance(sender, instance, created, **kwargs):
    if created:
        MailItTemplate.objects.create(writeitinstance=instance)
post_save.connect(new_write_it_instance, sender=WriteItInstance)


class BouncedMessageRecord(models.Model):
    outbound_message = models.OneToOneField(OutboundMessage)
    bounce_text = models.TextField()
    date = models.DateTimeField(auto_now=True)


class RawIncomingEmail(models.Model):
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance, related_name='raw_emails', null=True)
    answer = models.OneToOneField(Answer, related_name='raw_email', null=True)
    problem = models.BooleanField(default=False)
    message_id = models.CharField(max_length=2048, default="")
