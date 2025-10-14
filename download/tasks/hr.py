from django.conf import settings
from django.utils import timezone
from download.models import Download
from core.models import ProfileHR
from openpyxl import load_workbook
import json
from os.path import join, abspath, dirname
from download import utils
import logging
from django.db.models import Q, Count

logger = logging.getLogger('background')

def get_queryset(params, user):

  role = user.profile_hr.role
  qs = ProfileHR.objects.exclude(status=1) # Inactive
  if role == 'U':
    qs = qs.filter(user=user)
#   elif role == 'M':
#     qs = qs.filter(user__ =user.profile.department)
  return qs.select_related('department', 'direct_manager', 'title', 'position')


def filter_queryset(params, qs):
  if 'departments' in params:
    qs = qs.filter(department__in=params.get('departments').split(','))
  if 'direct_managers' in params:
    qs = qs.filter(direct_manager__in=params.get('direct_managers').split(','))
  if 'search' in params:
    fields = ['full_name__icontains', 'profile_code__icontains', 'employee_code__icontains', 'department__name__icontains']
    _q = Q()
    for field in fields:
      _q = _q | Q(**{field: params.get('search')})
    qs = qs.filter(_q)
  
  filter = utils.clone_exclude(params, ['page_size', 'page', 'departments', 'direct_managers', 'search'])
  return qs.filter(**filter)


def hr_download(download):
    
    try:
      query = json.loads(download.query)
      qs = get_queryset(query, download.created_by)
      qs = filter_queryset(query, qs)
      template = join(abspath(dirname(__file__)), '..', 'templates', 'hr_template.xlsx')
      wb = load_workbook(filename = template)
      ws = wb.worksheets[0]
          
      index = 0
      for obj in qs:
        index += 1
        data = [index]
        data.append(obj.join_date.replace(tzinfo=None))
        data.append(obj.actual_sign_date.replace(tzinfo=None))
        data.append(obj.full_name)
        data.append(obj.employee_code)
        data.append(obj.timekeeping_id)
        data.append(obj.dob)
        data.append(obj.pob)
        data.append(obj.place_of_origin)
        data.append(obj.gender)
        data.append(obj.nationality)
        data.append(obj.religion)
        data.append(obj.ethnicity)
        data.append(obj.educaional_level)
        data.append(obj.years_of_experience)
        data.append(obj.highest_qualification)
        data.append(obj.direct_manager)
        data.append(obj.current_address)
        data.append(obj.permanent_address)
        data.append(obj.email)
        data.append(obj.personal_email)
        data.append(obj.phone)
        ws.append(data)

      file_path = join('downloads', 'danh_sach_nhan_su_{}.xlsx'.format( utils.get_random_string(6)))  
      wb.save(join(settings.MEDIA_ROOT, file_path))
      wb.close()
    except Exception as e:
      logger.error("danh_sach_nhan_su_download Exception")
      logger.error(e)

      download.status = 3
      download.save()
      return False
      
    download.status = 2
    download.finished_at = timezone.now()
    download.filename.name = file_path
    download.filesize = utils.sizeof_fmt(download.filename.size)
    download.save()