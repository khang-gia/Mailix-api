
from celery import shared_task
from download.models import Download
from download.tasks.hr import hr_download
from download.tasks.contact import contact_download
from download.tasks.customer import customer_download
import logging
logger = logging.getLogger('background')

@shared_task
def process_download(id, force=False):
    logger.info('===== process_download: {}'.format(id))
    if force:
        download = Download.objects.filter(id=id).first()
    else:
        download = Download.objects.filter(id=id, status=0).first()
    if not download:
      logger.error('Error: download {} is not found.'.format(id))
      return False
    
    # start progress
    download.status = 1 # processing
    download.save()

    if download.export_type == 'hrm':        
        hr_download(download)
    elif download.export_type == 'contact':
        contact_download(download)
    elif download.export_type == 'customer':
        customer_download(download)
    else:
        logger.error('Error: report type {} is not valid.'.format(download.export_type))