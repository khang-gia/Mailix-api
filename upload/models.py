from django.db import models
from os.path import join, basename
from urllib.parse import urlsplit
import filetype
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

UPLOAD_TYPES = (
    (1, 'Profile HR'),
    (2, 'System User'),
    (3, 'Insurance'),
    (4, 'Contract'),
    (5, 'Timekeeping'),
    (6, 'Salary'),
    (7 , 'Contacts'),
    (8 , 'Customers'),
    (9 , 'Works')
)
UPLOAD_FODLERS = {
   0: 'unknowns',
   1: 'profile_hrs',
   2: 'system_users',
   3: 'insurances',
   4: 'contracts',
   5: 'timekeepings',
   6: 'salaries',
}
IMPORT_STATUSES = (
  (0, 'Not Process'),
  (1, 'Processed'),
  (3, 'Processing'),
  (2, 'Finished'),
  (9, 'Cancelled'),
)

def fc_upload_to(instance, filename):
    _folder = 'unknowns'
    try:
       _folder = UPLOAD_FODLERS[instance.upload_type]
    except KeyError:
       pass
    
    return join('uploads', _folder, filename)

class Upload(models.Model):
    file = models.FileField(upload_to=fc_upload_to)
    file_name = models.CharField("File Name", max_length=100, blank=True, null=True)
    file_type = models.CharField("File Type", max_length=100, blank=True, null=True)
    file_size = models.PositiveIntegerField("File Size", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploads')
    status = models.IntegerField('Status', choices=IMPORT_STATUSES, default=0)
    total = models.IntegerField('Total', default=0)
    success = models.IntegerField('Success Amt', default=0)
    failure = models.IntegerField('Failure Amt', default=0)
    errors_log = models.TextField('Error Log', null=True, blank=True)
    upload_type = models.IntegerField('Upload Type', default=1, choices=UPLOAD_TYPES)
  
    def __str__(self) -> str:
        return "Upload <{}> {}: {}".format(self.pk, self.upload_type, self.get_status_display())

    def save(self, *args, **kwargs):
        self.file_size = self.file.size
        self.file_name = self.file.name
        if '/' in self.file_name:
            self.file_name = basename(urlsplit(self.file_name).path)

        kind = filetype.guess(self.file.file)
        if kind:
            self.file_type = kind.mime
            return super(Upload, self).save(*args, **kwargs)

@receiver(signal=post_save, sender=Upload)
def upload_save_signal(sender, instance, created, *kargs, **kwargs):
    from upload.tasks import process_import_hr, process_import_timekeeping, process_import_contact, process_import_customer, process_import_work
    if created: # new
        instance.status = 3
        instance.save()
        try:
            if instance.upload_type == 1:
                process_import_hr.delay(instance.id)
            elif instance.upload_type == 5:
                process_import_timekeeping.delay(instance.id)
            elif instance.upload_type == 7:
                process_import_contact.delay(instance.id)
            elif instance.upload_type == 8:
                process_import_customer.delay(instance.id)
            elif instance.upload_type == 9:
                process_import_work.delay(instance.id)
        except Exception as e:
            print('Upload Exception', e)
            instance.status = 1
            instance.save()