import datetime
import secrets
import string
import xlwt
from django.core.exceptions import ObjectDoesNotExist

HEADER_SYTLE = xlwt.easyxf('font:bold on')
DEFAULT_STYLE = xlwt.easyxf()
CELL_STYLE_MAP = (
    (datetime.datetime, xlwt.easyxf(num_format_str="YYYY/MM/DD HH:MM")),
    (datetime.date, xlwt.easyxf(num_format_str='DD/MM/YYYY')),
    (datetime.time, xlwt.easyxf(num_format_str="HH:MM")),
    (bool, xlwt.easyxf(num_format_str="BOOLEAN")),
)


def multi_getattr(obj, attr, default=None):
    attributes = attr.split(".")

    for i in attributes:
        try:
            if obj._meta.get_field(i).choices:
                obj = getattr(obj, f"get_{i}_display")()
            else:
                obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise

    return obj


def get_column_head(obj, name):
    names = name.split(".")

    tmp = ''

    for i in names:
        tmp += obj._meta.get_field(i).verbose_name
        tmp += '.'


    return tmp


def get_column_cell(obj, name):
    try:
        attr = multi_getattr(obj, name)
    except ObjectDoesNotExist:
        return None

    if hasattr(attr, '_meta'):
        return str(attr).strip()
    elif hasattr(attr, 'all'):
        return ', '.join(str(x).strip() for x in attr.all())

    if isinstance(attr, datetime.datetime):
        from django.utils.timezone import localtime
        attr = localtime(attr)
        attr = attr.replace(tzinfo=None)

    return attr


def queryset_to_workbook(queryset,
                         columns,
                         header_style=HEADER_SYTLE,
                         default_style=DEFAULT_STYLE,
                         cell_style_map=CELL_STYLE_MAP):
    workbook = xlwt.Workbook()
    report_date = datetime.date.today()
    sheet_name = f"Export {report_date.strftime('%Y-%m-%d')}"
    sheet = workbook.add_sheet(sheet_name)

    obj = queryset.first()

    for num, column in enumerate(columns):
        value = get_column_head(obj, column)
        print('Head: {}'.format(value))
        sheet.write(0, num, value, header_style)

    for x, obj in enumerate(queryset, start=1):
        for y, column in enumerate(columns):
            value = get_column_cell(obj, column)
            style = default_style

            for value_type, cell_style in cell_style_map:
                if isinstance(value, value_type):
                    style = cell_style
                    break
            print('Value: {}'.format(value))
            sheet.write(x, y, value, style)

    return workbook


def get_user_name(u):
    return "{} {}".format(u.first_name, u.last_name) if u.first_name else u.username


def generate_secure_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))