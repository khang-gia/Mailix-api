from datetime import datetime, date, timedelta
from django.utils import timezone
import openpyxl
import os.path
import json
import logging
from celery import shared_task
from django.db.models import Sum
from django.conf import settings
from upload.models import Upload
from core.serializers import ProfileHRSerializer, CustomerImportSerializer,WorkImportSerializer
from django.db import transaction, DatabaseError

mapping_gender = {
    'nam': 'Nam', 'male': 'Nam', 'm': 'Nam',
    'nữ': 'Nữ', 'nu': 'Nữ', 'female': 'Nữ', 'f': 'Nữ',
    'khác': 'Khác', 'other': 'Khác', 'o': 'Khác'
}

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
    failure = 0
    total = 0
    errors = []
    COLS = ['join_date', 'actual_sign_date', 'full_name', 'employee_code', 'timekeeping_id', \
      'dob', 'pob', 'place_of_origin', 'gender','nationality', 'religion', 'ethnicity', 'educaional_level', \
      'years_of_experience', 'highest_qualification', 'direct_manager', 'current_address', 'permanent_address', 'email', 'personal_email','phone']

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

        if import_obj.get('gender'):
            val_lower = import_obj['gender'].strip().lower()
            if val_lower not in mapping_gender:
                errors.append({'row': total, 'type': 'invalid_choice', 'field': 'gender', 'value': import_obj['gender'], 'allowed': ['Nam', 'Nữ', 'Khác']})
                failure += 1
                continue
            import_obj['gender'] = mapping_gender[val_lower]
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
            errors.append({'row': total, 'type': 'exception', 'message': str(e)})
        if serializer and serializer.is_valid():
            profileHr = serializer.save()
            success += 1
        else:
            if serializer:
                print(serializer.errors)
                errors.append({'row': total, 'type': 'validation', 'details': serializer.errors})
            failure += 1

    obj.success = success
    obj.failure = failure
    obj.total = total
    obj.status = 1
    obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
    obj.save()
    # logger.info('Import {} has total {} update'.format(import_id, total_updated))
    wb.close()

@shared_task
def process_import_contact(import_id):
    print('===================== Process Upload: {}'.format(import_id))
    from core.models import ProfileHR, Customer
    from django.contrib.auth.models import User
    logger = logging.getLogger('upload')
    logger.info('===================== Process Upload: {}'.format(import_id))
    obj = Upload.objects.filter(id=import_id).first()
    if not obj:
        logger.error('Upload {} Not found'.format(import_id))
        return False
    mapping_group = {
        'khách hàng trung thành': 1,
        'khách hàng cũ': 2,
        'khách hàng tiềm năng':3,
        'khách hàng vãng lai': 4,
        'khách hàng tiềm năng mới': 5,
        'khách hàng đang chăm sóc': 6,
        'vip': 7,
        'vvip':8
    }
    mapping_type = {
        'cá nhân': 1,
        'tổ chức': 2
    }
    mapping_source = {
        'facebook': 1,
        'instagram': 2,
        'google': 3,
        'giới thiệu từ khách hàng cũ': 4,
        'trang web': 5,
        'tự tìm kiếm': 6,
        'tổng đài': 7,
        'môi giới': 8,
        'dữ liệu bán hàng': 9
    }
    if not os.path.isfile(obj.file.path):
        logger.error('Upload {} has no file : {}'.format(import_id, obj.file.path))
        obj.status = 1
        obj.save()
        return False

    wb = openpyxl.load_workbook(obj.file.path, data_only=True, read_only = True, keep_vba = False)
    sheet = wb.worksheets[0]
    success = 0
    failure = 0
    total = 0
    errors = []
    COLS = ['name', 'customer_code', 'title', 'dob', 'gender', \
      'curators', 'address', 'email', 'phone','tax_code', 'type_of_customer', 'customer_source', 'company_name', \
      'company_phone', 'company_email', 'company_address', 'company_tax_code']
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, max_col=len(COLS) + 1, values_only=True):
        if not any(row):  # skip empty rows
            break
        import_obj = {}
        row = row[1:]
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
        try: 
            with transaction.atomic():

                if import_obj.get('gender'):
                    val_lower = import_obj['gender'].strip().lower()
                    if val_lower not in mapping_gender:
                                errors.append({'row': total, 'type': 'invalid_choice', 'field': 'gender', 'value': import_obj['gender'], 'allowed': ['Nam', 'Nữ', 'Khác']})
                                failure += 1
                                continue
                    import_obj['gender'] = mapping_gender[val_lower]
                if import_obj['curators']:
                    curator_names = [n.strip() for n in import_obj['curators'].split(",") if n.strip()]
                    curator_objs = []
                    curator_objs = list(User.objects.filter(username__in=curator_names).values_list('id', flat=True))
                    import_obj['curators'] = curator_objs
                else:
                    import_obj['curators'] = []
                if import_obj.get('type_of_customer'):
                    val_lower = import_obj['type_of_customer'].strip().lower()
                    if val_lower not in mapping_type:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'type_of_customer', 'value': import_obj['type_of_customer'], 'allowed': list(mapping_type.keys())})
                        failure += 1
                        continue
                    import_obj['type_of_customer'] = mapping_type[val_lower]
                else:
                    import_obj['type_of_customer'] = 1

                if import_obj.get('customer_source'):
                    val_lower = import_obj['customer_source'].strip().lower()
                    if val_lower not in mapping_source:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'customer_source', 'value': import_obj['customer_source'], 'allowed': list(mapping_source.keys())})
                        failure += 1
                        continue
                    import_obj['customer_source'] = mapping_source[val_lower]
                else:
                    import_obj['customer_source'] = 1
                import_obj['stage'] = 1
                try:
                    customer = Customer._base_manager.get(customer_code=import_obj['customer_code'],stage=1)
                    if getattr(customer, 'is_deleted', False):
                        customer.deleted_at = None
                        customer.save(update_fields=['deleted_at'])
                    serializer = CustomerImportSerializer(customer, data=import_obj)
                except Customer.DoesNotExist:
                    serializer = CustomerImportSerializer(data=import_obj)
                except Exception as e:
                    print(e)
                    failure += 1
                    errors.append({'row': total, 'type': 'exception', 'message': str(e)})
                if serializer and serializer.is_valid():
                    print('serializer valid')
                    customer = serializer.save()
                    success += 1
                else:
                    if serializer:
                        print(serializer.errors)
                        errors.append({'row': total, 'type': 'validation', 'details': serializer.errors})
                    failure += 1
        except Exception as e:
            failure += 1
            logger.error('Upload contact has exception error: %s', e)
            errors.append({'row': total, 'type': 'exception', 'message': str(e)})

    obj.success = success
    obj.failure = failure
    obj.total = total
    obj.status = 1
    obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
    obj.save()
    # logger.info('Import {} has total {} update'.format(import_id, total_updated))
    wb.close()

@shared_task
def process_import_customer(import_id):
    print('===================== Process Upload: {}'.format(import_id))
    from core.models import ProfileHR, Customer
    from django.contrib.auth.models import User
    logger = logging.getLogger('upload')
    logger.info('===================== Process Upload: {}'.format(import_id))
    obj = Upload.objects.filter(id=import_id).first()
    if not obj:
        logger.error('Upload {} Not found'.format(import_id))
        return False
    mapping_group = {
        'khách hàng trung thành': 1,
        'khách hàng cũ': 2,
        'khách hàng tiềm năng':3,
        'khách hàng vãng lai': 4,
        'khách hàng tiềm năng mới': 5,
        'khách hàng đang chăm sóc': 6,
        'vip': 7,
        'vvip':8
    }
    mapping_type = {
        'cá nhân': 1,
        'tổ chức': 2
    }
    mapping_source = {
        'facebook': 1,
        'instagram': 2,
        'google': 3,
        'giới thiệu từ khách hàng cũ': 4,
        'trang web': 5,
        'tự tìm kiếm': 6,
        'tổng đài': 7,
        'môi giới': 8,
        'dữ liệu bán hàng': 9
    }
    if not os.path.isfile(obj.file.path):
        logger.error('Upload {} has no file : {}'.format(import_id, obj.file.path))
        obj.status = 1
        obj.save()
        return False

    wb = openpyxl.load_workbook(obj.file.path, data_only=True, read_only = True, keep_vba = False)
    sheet = wb.worksheets[0]
    success = 0
    failure = 0
    total = 0
    errors = []
    COLS = ['name', 'customer_code', 'title', 'dob', 'gender', \
      'curators', 'address', 'email', 'phone','tax_code', 'type_of_customer', 'customer_source', 'customer_group', 'company_name', \
      'company_phone', 'company_email', 'company_address', 'company_tax_code']
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, max_col=len(COLS) + 1, values_only=True):
        if not any(row):  # skip empty rows
            break
        import_obj = {}
        row = row[1:]
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
        try: 
            with transaction.atomic():

                if import_obj.get('gender'):
                    val_lower = import_obj['gender'].strip().lower()
                    if val_lower not in mapping_gender:
                                errors.append({'row': total, 'type': 'invalid_choice', 'field': 'gender', 'value': import_obj['gender'], 'allowed': ['Nam', 'Nữ', 'Khác']})
                                failure += 1
                                continue
                    import_obj['gender'] = mapping_gender[val_lower]
                if import_obj['curators']:
                    curator_names = [n.strip() for n in import_obj['curators'].split(",") if n.strip()]
                    curator_objs = []
                    curator_objs = list(User.objects.filter(username__in=curator_names).values_list('id', flat=True))
                    import_obj['curators'] = curator_objs
                else:
                    import_obj['curators'] = []
                if import_obj.get('type_of_customer'):
                    val_lower = import_obj['type_of_customer'].strip().lower()
                    if val_lower not in mapping_type:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'type_of_customer', 'value': import_obj['type_of_customer'], 'allowed': list(mapping_type.keys())})
                        failure += 1
                        continue
                    import_obj['type_of_customer'] = mapping_type[val_lower]
                else:
                    import_obj['type_of_customer'] = 1

                if import_obj.get('customer_source'):
                    val_lower = import_obj['customer_source'].strip().lower()
                    if val_lower not in mapping_source:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'customer_source', 'value': import_obj['customer_source'], 'allowed': list(mapping_source.keys())})
                        failure += 1
                        continue
                    import_obj['customer_source'] = mapping_source[val_lower]
                else:
                    import_obj['customer_source'] = 1

                if import_obj.get('customer_group'):
                    val_lower = import_obj['customer_group'].strip().lower()
                    if val_lower not in mapping_group:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'customer_group', 'value': import_obj['customer_group'], 'allowed': list(mapping_group.keys())})
                        failure += 1
                        continue
                    import_obj['customer_group'] = mapping_group[val_lower]
                else:
                    import_obj['customer_group'] = 1
                import_obj['stage'] = 2
                try:
                    print('import_obj', import_obj)
                    customer = Customer._base_manager.get(customer_code=import_obj['customer_code'], stage=2)
                    if getattr(customer, 'is_deleted', False):
                        customer.deleted_at = None
                        customer.save(update_fields=['deleted_at'])
                    serializer = CustomerImportSerializer(customer, data=import_obj)
                except Customer.DoesNotExist:
                    serializer = CustomerImportSerializer(data=import_obj)
                except Exception as e:
                    print(e)
                    failure += 1
                    errors.append({'row': total, 'type': 'exception', 'message': str(e)})
                if serializer and serializer.is_valid():
                    customer = serializer.save()
                    success += 1
                else:
                    if serializer:
                        print(serializer.errors)
                        errors.append({'row': total, 'type': 'validation', 'details': serializer.errors})
                    failure += 1
        except Exception as e:
            failure += 1
            logger.error('Upload customer has exception error: %s', e)
            errors.append({'row': total, 'type': 'exception', 'message': str(e)})

    obj.success = success
    obj.failure = failure
    obj.total = total
    obj.status = 1
    obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
    obj.save()
    # logger.info('Import {} has total {} update'.format(import_id, total_updated))
    wb.close()


@shared_task
def process_import_work(import_id):
    print('===================== Process Upload Work: {}'.format(import_id))
    from core.models import ProfileHR, Works
    from django.contrib.auth.models import User
    logger = logging.getLogger('upload')
    logger.info('===================== Process Upload: {}'.format(import_id))
    obj = Upload.objects.filter(id=import_id).first()
    if not obj:
        logger.error('Upload {} Not found'.format(import_id))
        return False
    mapping_priority = {
        'thấp': 1,
        'trung bình': 2,
        'cao':3,
        'khấn cấp': 4,
        'nghiêm trọng': 5,
        'không': 6
    }
    mapping_status = {
        'chưa bắt đầu': 1,
        'đang tiến hành': 2,
        'hoàn thành': 3,
        'tạm dừng': 4,
        'đã huỷ': 5,
        'hoãn lại':6,
        'chờ duyệt': 7,
        'đã phê duyệt': 8,
        'bị từ chói': 9,
        'chờ': 10,
        'thất bại': 11,
        'thành công':12,
        'lưu trữ': 13,
        'đã xoá': 14,
        'bản nháp': 15
    }
    if not os.path.isfile(obj.file.path):
        logger.error('Upload {} has no file : {}'.format(import_id, obj.file.path))
        obj.status = 1
        obj.save()
        return False

    wb = openpyxl.load_workbook(obj.file.path, data_only=True, read_only = True, keep_vba = False)
    sheet = wb.worksheets[0]
    success = 0
    failure = 0
    total = 0
    errors = []
    COLS = ['name', 'code', 'description','status', 'assigned_to', 'assigned_by', \
      'managers', 'start_date', 'actual_start_date', 'end_date','priority']
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, max_col=len(COLS) + 1, values_only=True):
        if not any(row):  # skip empty rows
            break
        import_obj = {}
        row = row[1:]
        for j in range(0, len(COLS)):
            value = row[j]
            import_obj[COLS[j]] = None
            if not value or value=='':
                continue
            if isinstance(value, str):
                value = value.strip()
            import_obj[COLS[j]] = value
            if isinstance(value, datetime) and COLS[j] not in ['start_date', 'actual_start_date', 'end_date']:
                import_obj[COLS[j]] = value.date()
        total += 1    
        serializer = None
        try: 
            with transaction.atomic():
                if import_obj['assigned_to']:
                    _names = [n.strip() for n in import_obj['assigned_to'].split(",") if n.strip()]
                    _objs = []
                    _objs = list(User.objects.filter(username__in=_names).values_list('id', flat=True))
                    import_obj['assigned_to'] = _objs
                else:
                    import_obj['assigned_to'] = []
                if import_obj['assigned_by']:
                    _names = [n.strip() for n in import_obj['assigned_by'].split(",") if n.strip()]
                    _objs = []
                    _objs = list(User.objects.filter(username__in=_names).values_list('id', flat=True))
                    import_obj['assigned_by'] = _objs
                else:
                    import_obj['assigned_by'] = []
                if import_obj['managers']:
                    _names = [n.strip() for n in import_obj['managers'].split(",") if n.strip()]
                    _objs = []
                    _objs = list(User.objects.filter(username__in=_names).values_list('id', flat=True))
                    import_obj['managers'] = _objs
                else:
                    import_obj['managers'] = []
                if import_obj.get('priority'):
                    val_lower = import_obj['priority'].strip().lower()
                    if val_lower not in mapping_priority:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'priority', 'value': import_obj['priority'], 'allowed': list(mapping_priority.keys())})
                        failure += 1
                        continue
                    import_obj['priority'] = mapping_priority[val_lower]
                else:
                    import_obj['priority'] = 2

                if import_obj.get('status'):
                    val_lower = import_obj['status'].strip().lower()
                    if val_lower not in mapping_status:
                        errors.append({'row': total, 'type': 'invalid_choice', 'field': 'status', 'value': import_obj['status'], 'allowed': list(mapping_status.keys())})
                        failure += 1
                        continue
                    import_obj['status'] = mapping_status[val_lower]
                else:
                    import_obj['status'] = 1

                try:
                    print('import_obj', import_obj)
                    work = Works._base_manager.get(code=import_obj['code'])
                    if getattr(work, 'is_deleted', False):
                        work.deleted_at = None
                        work.save(update_fields=['deleted_at'])
                    serializer = WorkImportSerializer(work, data=import_obj)
                except Works.DoesNotExist:
                    serializer = WorkImportSerializer(data=import_obj)
                except Exception as e:
                    print(e)
                    failure += 1
                    errors.append({'row': total, 'type': 'exception', 'message': str(e)})
                if serializer and serializer.is_valid():
                    work = serializer.save()
                    success += 1
                else:
                    if serializer:
                        print(serializer.errors)
                        errors.append({'row': total, 'type': 'validation', 'details': serializer.errors})
                    failure += 1
        except Exception as e:
            failure += 1
            logger.error('Upload work has exception error: %s', e)
            errors.append({'row': total, 'type': 'exception', 'message': str(e)})

    obj.success = success
    obj.failure = failure
    obj.total = total
    obj.status = 1
    obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
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


@shared_task
def process_remove_hr(import_id):
    from core.models import ProfileHR
    obj = Upload.objects.filter(id=import_id).first()
    if not obj: return
    try:
        wb = openpyxl.load_workbook(obj.file.file, data_only=True)
        sheet = wb.active
        errors, success, failure, total = [], 0, 0, 0
        # HR template: min_col=2, COLS index 3 = employee_code
        HR_CODE_IDX = 3
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=2, values_only=True):
            if not any(row):
                break
            code = row[HR_CODE_IDX]
            if not code: continue
            total += 1
            code = str(code).strip()
            profile = ProfileHR.objects.filter(employee_code=code).first()
            if profile:
                profile.delete()
                success += 1
            else:
                errors.append({'row': total, 'type': 'not_found', 'code': code})
                failure += 1

        obj.success, obj.failure, obj.total, obj.status = success, failure, total, 1
        obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
        obj.save()
    except Exception as e:
        obj.status, obj.errors_log = 1, json.dumps([{'row': 0, 'type': 'exception', 'message': str(e)}], ensure_ascii=False)
        obj.save()


@shared_task
def process_remove_contact(import_id):
    from core.models import Customer
    obj = Upload.objects.filter(id=import_id).first()
    if not obj: return
    try:
        wb = openpyxl.load_workbook(obj.file.file, data_only=True)
        sheet = wb.active
        errors, success, failure, total = [], 0, 0, 0
        # Contact template: row[1:], COLS index 1 = customer_code (col C)
        CONTACT_CODE_IDX = 1
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=True):
            if not any(row):
                break
            code = row[CONTACT_CODE_IDX + 1]  # +1 to skip the No. column (col A)
            if not code: continue
            total += 1
            code = str(code).strip()
            customer = Customer.objects.filter(customer_code=code, stage=1).first()
            if customer:
                customer.delete()
                success += 1
            else:
                errors.append({'row': total, 'type': 'not_found', 'code': code})
                failure += 1

        obj.success, obj.failure, obj.total, obj.status = success, failure, total, 1
        obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
        obj.save()
    except Exception as e:
        obj.status, obj.errors_log = 1, json.dumps([{'row': 0, 'type': 'exception', 'message': str(e)}], ensure_ascii=False)
        obj.save()

@shared_task
def process_remove_customer(import_id):
    from core.models import Customer
    obj = Upload.objects.filter(id=import_id).first()
    if not obj: return
    try:
        wb = openpyxl.load_workbook(obj.file.file, data_only=True)
        sheet = wb.active
        errors, success, failure, total = [], 0, 0, 0
        # Customer template: row[1:], COLS index 1 = customer_code (col C)
        CUSTOMER_CODE_IDX = 1
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=True):
            if not any(row):
                break
            code = row[CUSTOMER_CODE_IDX + 1]  # +1 to skip the No. column (col A)
            if not code: continue
            total += 1
            code = str(code).strip()
            customer = Customer.objects.filter(customer_code=code, stage=2).first()
            if customer:
                customer.delete()
                success += 1
            else:
                errors.append({'row': total, 'type': 'not_found', 'code': code})
                failure += 1

        obj.success, obj.failure, obj.total, obj.status = success, failure, total, 1
        obj.errors_log = json.dumps(errors, ensure_ascii=False) if errors else None
        obj.save()
    except Exception as e:
        obj.status, obj.errors_log = 1, json.dumps([{'row': 0, 'type': 'exception', 'message': str(e)}], ensure_ascii=False)
        obj.save()

