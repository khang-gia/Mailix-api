from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

DOWNLOAD_STATUS = (
    (0, 'Not started'),
    (1, 'Processing'),
    (2, 'Finished'),
    (3, 'Error'),
)
EXPORT_TYPES = (
    ('hrm', 'HRM'),
    ('contact', 'Contact'),
    ('customer', 'Customer'),
    ('work', 'Work'),
)
class Download(models.Model):
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='downloads')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    query = models.TextField('Query', null=True, blank=True)
    filename = models.FileField('File Name', null=True, blank=True)
    filesize = models.CharField('File Size', max_length=20, default="", blank=True)
    status = models.IntegerField('Status', default=0, choices=DOWNLOAD_STATUS)
    export_type = models.CharField('Export Type', max_length=20, choices=EXPORT_TYPES)
    
    def __str__(self) -> str:
        return "Download - {}".format(self.created_by)
    
@receiver(signal=post_save, sender=Download)
def download_postsave(sender, instance, created, *kargs, **kwargs):
  if created: # process save new action
    from download.tasks import process_download
    process_download.delay(instance.id)