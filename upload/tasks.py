from datetime import datetime, date, timedelta
from django.utils import timezone
import openpyxl
import os.path
import logging
from celery import shared_task
from django.db.models import Sum
from django.conf import settings
from upload.models import Upload
from core.serializers import ProfileHRSerializer
@shared_task
def process_import_hr(import_id):
    print('===================== Process Upload: {}'.format(import_id))
    from core.models import ProfileHR
    from django.contrib.auth.models import User
    logger = logging.getLogger('upload')
    logger.info('===================== Process Upload: {}'.format(import_id))
    obj = Upload.objects.filter(id=import_id).first()
    if not obj:
        logger.error('Upload {} Not found'.format(import_id))
        return False

    if not os.path.isfile(obj.file.path):
        logger.error('Upload {} has no file : {}'.format(import_id, obj.file.path))
        obj.status = 1
        obj.save()
        return False

    wb = openpyxl.load_workbook(obj.file.path, data_only=True, read_only = True, keep_vba = False)
    sheet = wb.worksheets[0]
    success = 0
    total = 0
    COLS = ['join_date', 'actual_sign_date', 'full_name', 'employee_code', 'timekeeping_id', \
      'dob', 'pob', 'place_of_origin', 'gender','nationality', 'religion', 'ethnicity', 'educaional_level', \
      'years_of_experience', 'highest_qualification', 'direct_manager', 'current_address', 'permanent_address', 'email', 'phone','phone_other']

    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=2, values_only=True):
        import_obj = {}
        for j in range(0, len(COLS)):
            value = row[j]
            import_obj[COLS[j]] = None
            if not value or value=='':
                continue
            if isinstance(value, str):
                value = value.strip()
            import_obj[COLS[j]] = value
            if isinstance(value, datetime):
                import_obj[COLS[j]] = value.date()
        total += 1    
        serializer = None
        if import_obj['direct_manager']:
            _direct_manager = User.objects.filter(username=import_obj['direct_manager']).first()
            if _direct_manager:
                import_obj['direct_manager'] = _direct_manager.id
            else:
                import_obj['direct_manager'] = None
        try:
            profile = ProfileHR.objects.get(employee_code=import_obj['employee_code'])
            serializer = ProfileHRSerializer(profile, data=import_obj)
        except ProfileHR.DoesNotExist:
            serializer = ProfileHRSerializer(data=import_obj)
        except Exception as e:
            print(e)
        if serializer and serializer.is_valid():
            profileHr = serializer.save()
            success += 1
        else:
            if serializer:
                print(serializer.errors)
            failure += 1

    obj.success = success
    obj.failure = 0
    obj.total = total
    obj.status = 1
    obj.save()
    # logger.info('Import {} has total {} update'.format(import_id, total_updated))
    wb.close()


@shared_task
def process_import_timekeeping(import_id):
    import calendar
    from datetime import datetime
    print('===================== Process Upload TimeRecord: {}'.format(import_id))
    logger = logging.getLogger('upload')
    logger.info('===================== Process Upload: {}'.format(import_id))
    obj = Upload.objects.filter(id=import_id).first()
    if not obj:
        logger.error('Upload {} Not found'.format(import_id))
        return False

    if not os.path.isfile(obj.file.path):
        logger.error('Upload {} has no file : {}'.format(import_id, obj.file.path))
        obj.status = 1
        obj.save()
        return False

    wb = openpyxl.load_workbook(obj.file.path, data_only=True, read_only = True, keep_vba = False)
    sheet = wb.worksheets[0]
    success = 0
    total = 0
    year = datetime.now().year
    month = datetime.now().month

    days_in_month = calendar.monthrange(year, month)[1]

    print('days_in_month',days_in_month)
    COLS = ['employee_code','full_name']
    max_column = len(COLS)

    # for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=True):
    #     import_obj = {}
    #     for j in range(0, days_in_month + 2):
    #         value = row[j]
    #         import_obj[COLS[j]] = None
    #         if not value or value=='':
    #             continue
    #         if j <= max_column: 
    #             import_obj[COLS[j]] = value
    #             if isinstance(import_obj[COLS[j]], str):
    #                 import_obj[COLS[j]] = import_obj[COLS[j]].strip()
                
    #             if isinstance(import_obj[COLS[j]], datetime):
    #                 import_obj[COLS[j]] = import_obj[COLS[j]].date()
    #         else:
    #             if cell.value is None:
    #                 # end of row
    #                 break
    #             else:
    #                 phones.append(cell.value)
    #     total += 1    
    #     serializer = None
    #     try:
    #         profile = ProfileHR.objects.get(employee_code=import_obj['employee_code'])
    #         serializer = ProfileHRSerializer(profile, data=import_obj)
    #     except ProfileHR.DoesNotExist:
    #         serializer = ProfileHRSerializer(data=import_obj)
    #     except Exception as e:
    #         print(e)
    #     if serializer and serializer.is_valid():
    #         profileHr = serializer.save()
    #         success += 1
    #     else:
    #         if serializer:
    #             print(serializer.errors)
    #         failure += 1

    obj.success = success
    obj.failure = 0
    obj.total = total
    obj.status = 1
    obj.save()
    # logger.info('Import {} has total {} update'.format(import_id, total_updated))
    wb.close()