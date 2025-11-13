from django.shortcuts import render
from .models import Profile, SystemNotification, Feedback, HappeningEvent, HotEvent, ProfileHR, Title, Customer, Works
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer, SystemNotificationSerializer, FeedbackSerializer, HappeningEventSerializer, HotEventSerializer,\
  CredentialsSerializer, ProfileHRListSerializer, ProfileHRDetailSerializer, ProfileHRSerializer, UserListSerializer, TitleSerializer, TitleListSerializer, UsernameSerializer, \
    OTPSerializer, CustomerSerializer, CustomerListSerializer, CustomerDetailSerializer, WorkSerializer, WorkListSerializer, WorkDetailSerializer, WorkHistorySerializer
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q, Count
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, user_logged_in
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from core.utils_feature import otp
from core.utils_feature.mail import send_otp, send_forget_password_otp, send_password_on_create_user
from rest_framework.views import APIView
import secrets
import io
from core.xlsx import ExportXlsx
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from system.models import TrustedDevice
from django.utils import timezone
from core.utils import generate_secure_password
from system.miab import add_mail_user, set_mail_user_password
from django.db import transaction
from django.http import HttpResponse

def update_profile(request):
    data = request.data
    user_serializer = UserSerializer(request.user, data = data)
    if user_serializer.is_valid():
        user_serializer.save()
    else:
        print(user_serializer.errors)
    if 'profile' in data:
        profile_serializer = ProfileSerializer(request.user.profile, data=data['profile'])
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            print(profile_serializer.errors)
        
    return Response(user_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([])
def reset_password(request, *args):
  new_password = request.data.get('password', None)
  if not new_password:
    return Response({'password': ['Mật khẩu không được để trống.']}, status=status.HTTP_400_BAD_REQUEST)
  otp_serializer = OTPSerializer(data=request.data)
  if not otp_serializer.is_valid():
    return Response(otp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  if not otp.verify(otp_serializer.data['code'], otp_serializer.data['email']):
    return Response({'code': ['Mã OTP không đúng hoặc đã hết hạn.']}, status=status.HTTP_400_BAD_REQUEST)
  user = User.objects.filter(username=request.data['username']).first()
  user.set_password(new_password)
  user.save()
  user_serializer = UserSerializer(user)
  return Response(user_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def change_password(request, *args):
  new_password = request.data.get('new_password', None)
  old_password = request.data.get('old_password', None)
  user = request.user
  if not user.check_password(old_password):
    return Response({'detail': 'PASSWORD_INVALID'}, status=status.HTTP_401_UNAUTHORIZED)
  if not new_password:
    return Response({'detail': 'PASSWORD IS REQUIRED'}, status=status.HTTP_400_BAD_REQUEST)
  user.set_password(new_password)
  user.save()
  profile_hr= user.profile_hr
  profile_hr.is_first_login = False
  profile_hr.save()
  success, res = set_mail_user_password(profile_hr.email, new_password) # Set miab password also
  if not success:
    raise Exception('Cannot create email account on Mail-in-a-Box server.')
  user_serializer = UserSerializer(user)
  return Response(user_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def register(request, *args):
  credential = CredentialsSerializer(data=request.data)
  if not credential.is_valid():
    return Response(credential.errors, status=status.HTTP_400_BAD_REQUEST)
  
  user = User.objects.create_user(**credential.data)
  user_serializer = UserSerializer(user)

  # code = otp.generate(user.email)
  # send_otp(user.email, code)
  return Response(user_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([])
def generate_otp(request, *args):
  username = UsernameSerializer(data=request.data)
  if not username.is_valid():
    return Response(username.errors, status=status.HTTP_400_BAD_REQUEST)
  
  user = User.objects.filter(username=username.data['username']).first()
  if not user:
    return Response({'username': ['Email không tồn tại.']}, status=status.HTTP_400_BAD_REQUEST)
  user_serializer = UserSerializer(user)

  code = otp.generate(user.email)
  view = request.data.get('view', 'registration')
  if view == 'registration':
    send_otp(user.email, code)
  elif view == 'resetpassword':
    send_forget_password_otp(user.email, code)
  return Response(user_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([])
def generate_otp_with_email(request, *args):
  email = request.data.get('email')
  if not email:
    return Response({'email': ['Thiếu email.']}, status=status.HTTP_400_BAD_REQUEST)
  user = User.objects.filter(email=email).first()
  if not user:
    return Response({'email': ['Email không tồn tại hoặc chưa được đăng ký.']}, status=status.HTTP_400_BAD_REQUEST)
  user_serializer = UserSerializer(user)
  code = otp.generate(email)
  send_forget_password_otp(email, code)
  return Response(user_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def verify_otp(request, *args):
  username = request.data.get('username')
  trust_device = request.data.get('is_trust_device', False)
  user = User.objects.filter(username=username).first()
  if not user:
    return Response({'username': ['User does not exist.']}, status=status.HTTP_400_BAD_REQUEST)

  request.data['email'] = user.email
  code = OTPSerializer(data=request.data)
  if not code.is_valid():
    return Response(code.errors, status=status.HTTP_400_BAD_REQUEST)
  if not otp.verify(code.data['code'], code.data['email']):
    return Response({'code': ['Mã OTP không đúng hoặc đã hết hạn.']}, status=status.HTTP_400_BAD_REQUEST)

  # --- OTP is valid, now create a trusted device if requested ---
  if trust_device:
    # Generate a new secure token for the cookie
    new_token = secrets.token_hex(32)
    
    # Hash the token before saving to the database
    hashed_token = make_password(new_token)
    
    # Create the trusted device record
    meta = request.META
    ip_address = meta.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() if 'HTTP_X_FORWARDED_FOR' in meta else meta.get('REMOTE_ADDR', None)
    user_agent = meta.get('HTTP_USER_AGENT', None)
    TrustedDevice.objects.create(
        user=user,
        token=hashed_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Create response and set the secure cookie
    response = Response({'detail': 'Device is now trusted.'}, status=status.HTTP_200_OK)
    response.set_cookie(
        key='trusted_device',
        value=new_token,
        max_age=30 * 24 * 60 * 60,  # 30 days
        secure=settings.COOKIE_SECURE_FLAG,  # True in production
        httponly=True,              # Crucial: prevents JS access
        samesite='Lax'           # Highly recommended
    )
    print('Set trusted device cookie:', response.cookies.get('trusted_device'))
    return response
  return Response({'detail': 'Device is now trusted.'}, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT'])
def profile_api(request):
  if request.method == 'GET':
    return Response(UserSerializer(request.user).data)
  
  return update_profile(request)

@api_view(['POST'])
@permission_classes([])
def pre_login(request, *args):
  credential = LoginSerializer(data=request.data)
  if not credential.is_valid():
    return Response(credential.errors, status=status.HTTP_400_BAD_REQUEST)
  user = authenticate(**credential.data)
  if not user:
    return Response({'username': ['Email hoặc mật khẩu không đúng.']}, status=status.HTTP_401_UNAUTHORIZED)
  user_serializer = UserSerializer(user)
  profile_user = ProfileHR.objects.filter(user=user).first()
  if profile_user and profile_user.is_demo_account:
    # Directly log in demo accounts without OTP
    return Response({'allowed_login':True}, status=status.HTTP_200_OK)
    
  print('cookies: ',request.COOKIES)
  trusted_device_token = request.COOKIES.get('trusted_device')
  print('trusted_device_token: ', trusted_device_token)
  if trusted_device_token:
    # Find a matching token for this user
    for device in user.trusted_devices.all():
      if check_password(trusted_device_token, device.token):
        # Device is trusted, bypass OTP.
        device.last_used_at = timezone.now()
        device.save() 
        
        # Issue refresh token and log the user in
        # refresh = RefreshToken.for_user(user)
        # return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': user_serializer.data}, status=status.HTTP_200_OK)
        return Response({'allowed_login':True}, status=status.HTTP_200_OK)

  code = otp.generate(user.email)
  send_otp(user.email, code)
  return Response(user_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([])
def login(request, *args):
  credential = LoginSerializer(data=request.data)
  if not credential.is_valid():
    return Response(credential.errors, status=status.HTTP_400_BAD_REQUEST)
  user = authenticate(**credential.data)
  if not user:
    return Response({'username': ['Email hoặc mật khẩu không đúng.']}, status=status.HTTP_401_UNAUTHORIZED)
  user_serializer = UserSerializer(user)
  refresh = RefreshToken.for_user(user)
  return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': user_serializer.data}, status=status.HTTP_200_OK)

class UserFilter(FilterSet):
    username = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    search = django_filters.CharFilter(method='elastic_search')
    role = django_filters.CharFilter(field_name="profile__role")
    class Meta:
        model = User
        fields = ['username', 'is_active', 'role']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['username__icontains', 'first_name__icontains', 'last_name__icontains', 'profile_hr__full_name__icontains', 'email__icontains']
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request, *args):
        if request.method == 'GET': # get profile
            return Response(UserSerializer(request.user, context={'request': request}).data)
        
        # update profile
        data = request.data

        user_serializer = UserSerializer(request.user, data = data)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            print(user_serializer.errors)
        
        if 'profile' in data:
            profile_serializer = ProfileSerializer(request.user.profile, data=data['profile'])
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            print(profile_serializer.errors)
            
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None, *args, **kwargs):
        u_serializer = UserSerializer(data=request.data)
        if u_serializer.is_valid():
            u_obj = u_serializer.save()
            u_obj.set_password(request.data['password'])
            u_obj.save()

            p_serializer = ProfileSerializer(u_obj.profile, data=request.data['profile'])
            if p_serializer.is_valid():
                p_serializer.save()
                return Response(u_serializer.data, status=status.HTTP_200_OK)
            return Response({'success': False, 'error': p_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  
        return Response({'success': False, 'error': u_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
       return super().update(request, *args, **kwargs)
    
# @api_view(['POST'])
# def change_password(request):
#   user = request.user
#   if user.check_password(request.data['password']):
#     try:
#       # allow to change
#       user.set_password(request.data['new_password'])
#       user.save()
#       return Response(status=status.HTTP_200_OK)
#     except Exception as e:
#       return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#   return Response({'detail': 'PASSWORD_INVALID'}, status=status.HTTP_400_BAD_REQUEST)



class SystemNotificationViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = SystemNotification.objects.all().order_by('-created_at')[:20]
  serializer_class = SystemNotificationSerializer
  ordering_fields = []

class FeedbackViewSet(viewsets.ModelViewSet):

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticated]
    ordering = ('-created_at')
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['user'] = request.user.id
        request.data._mutable = False
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
      qs = super().get_queryset()
      if self.request.user.groups.filter(name='CONSULT_ADMIN').exists() or self.request.user.is_superuser:
        return qs
      return qs.none()
class HappeningEventViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = HappeningEvent.objects.all()
  serializer_class = HappeningEventSerializer
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_queryset(self):
    now = timezone.now()
    return self.queryset.filter(end_time__gt=now, start_time__lt=now)

class HotEventViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = HotEvent.objects.filter(active=True).order_by('-id')
  serializer_class = HotEventSerializer
  ordering_fields = ['id']
  ordering = ('-id',)

class ProfileHRFilter(FilterSet):
  departments = django_filters.CharFilter(method='filter_departments')
  direct_managers = django_filters.CharFilter(method='filter_direct_managers')
  search = django_filters.CharFilter(method='elastic_search')
  class Meta:
    model = ProfileHR
    fields = ['full_name','employee_code','status']

  def elastic_search(self, queryset, name, value):
    if not value:
        return queryset
    fields = ['full_name__icontains', 'profile_code__icontains', 'employee_code__icontains', 'department__name__icontains']
    _q = Q()
    for field in fields:
      _q = _q | Q(**{field: value})
    
    return queryset.filter(_q)

  def filter_departments(self, queryset, name, value):
    if not value:
        return queryset

    department_ids = value.split(',')
    return queryset.filter(department__id__in=department_ids).distinct()

  def filter_direct_managers(self, queryset, name, value):
    if not value:
        return queryset

    direct_manager_ids = value.split(',')
    return queryset.filter(direct_manager__id__in=direct_manager_ids).distinct()
class ProfileHRViewSet(viewsets.ModelViewSet):
  queryset = ProfileHR.objects.all()
  serializer_class = ProfileHRSerializer
  filterset_class = ProfileHRFilter
  permission_classes = [IsAuthenticated]
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    if self.action == 'list':
      return ProfileHRListSerializer
    elif self.action == 'retrieve':
      return ProfileHRDetailSerializer
    return ProfileHRSerializer

  @action(detail=False, methods=['post'])
  def delete_users(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    profile_ids = request.data['profiles']
    if not profile_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for profile_id in profile_ids:
      try:
        profile = ProfileHR.objects.get(pk=profile_id)
        profile.delete()
      except ProfileHR.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)

  @action(detail=False, methods=['post'])
  def deactivate_profile(self, request, pk=None):
    profile_ids = request.data['profiles']
    if not profile_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for profile_id in profile_ids:
      try:
        profile = ProfileHR.objects.get(pk=profile_id)
        profile.status = 'Inactive'
        profile.save()
      except ProfileHR.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)

  @action(detail=True , methods=['post'])
  def create_account(self, request, pk=None):
    profile_hr = self.get_object()
    email = request.data.get('email', None)
    authen_email = request.data.get('authen_email', None)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not password:
      password = generate_secure_password(12)
    if not username or not email or not password or not authen_email:
      return Response({'detail': 'Username, email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not profile_hr:
      return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if User.objects.filter(email=authen_email).exists():
      return Response({'detail': 'Authen email is already in use by another account.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
      return Response({'detail': 'Username is already in use by another account.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
      with transaction.atomic():
        user = User.objects.create_user(username=username, email=authen_email)
        user.set_password(password)
        user.save()
        success, res = add_mail_user(email, password)
        if not success:
          raise Exception('Cannot create email account on Mail-in-a-Box server.')
        profile_hr.user = user
        profile_hr.email = authen_email
        profile_hr.is_first_login = True
        profile_hr.save()
        transaction.on_commit(lambda: send_password_on_create_user(authen_email, email, username, password))
    except Exception as e:
      return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['get'])
  def export_profile_hrs(self, request, pk=None):
    qs = self.get_queryset()
    qs = self.filter_queryset(qs)
    is_user = request.user.profile_hr.role == 'U'

    HEADERS = ['No.','NGÀY VÀO', 'NGÀY KÝ HỢP ĐỒNG LAO ĐỘNG CHÍNH THỨC', 'HỌ VÀ TÊN', 'MÃ NHÂN SỰ', \
      'MÃ CHẤM CÔNG', ' NGÀY SINH ', 'NƠI SINH', 'NGUYÊN QUÁN', 'GIỚI TÍNH', 'QUỐC TỊCH', 'TÔN GIÁO','DÂN TỘC','TRÌNH ĐỘ PHỔ THÔNG', 'SÔ NĂM KINH NGHIỆM',' TRÌNH ĐỘ HỌC VẤN CAO NHẤT','NGƯỜI QUẢN LÝ TRỰC TIẾP', \
      'NƠI Ở HIỆN TẠI', 'ĐỊA CHỈ THƯỜNG TRÚ', 'EMAIL', 'EMAIL CÁ NHÂN',' SỐ ĐIỆN THOẠI']
    # if not is_user:
    #     HEADERS += ['ID_NUMBER', 'GENDER', 'BIRTH_DATE_APPLICANT', 'ADDRESS_CURRENT', 'MOBILE_NUMBER', \
    #     'REF1_NUMBER', 'REF2_NUMBER']
    HEADERS += ['PHÒNG BAN','LOẠI LAO ĐỘNG','TRẠNG THÁI']

    SHEET_NAME = 'HỒ SƠ NHÂN SỰ'
    output = io.BytesIO()
    xlsx = ExportXlsx(output, SHEET_NAME)
    xlsx.add_header(HEADERS)

    PROFILE_STATUSES = (
      (0, 'Working'),
      (1, 'Temporary absent'),
      (2, 'Resigned'),
      (3, 'Providing service'),
      (4, 'Pending for recruitment'),
    )
    EDUCATION_LEVEL_CHOICES = (
      (1, "1/12"),
      (2, "2/12"),
      (3, "3/12"),
      (4, "4/12"),
      (5, "5/12"),
      (6, "6/12"),
      (7, "7/12"),
      (8, "8/12"),
      (9, "9/12"),
      (10, "10/12"),
      (11, "11/12"),
      (12, "12/12"),
    )
    for x, obj in enumerate(qs):
      direct_manager = ''
      department= ''
      if obj.direct_manager:
        direct_manager = obj.direct_manager.username
      if obj.department:
        department = obj.department.name
      educaional_level = ''
      if obj.educaional_level:
        educaional_level = ([x for x in EDUCATION_LEVEL_CHOICES if x[0] == obj.educaional_level][0][1])
      data = [x+1, obj.join_date, obj.actual_sign_date, obj.full_name, obj.employee_code, \
        obj.timekeeping_id, obj.dob, obj.pob, obj.place_of_origin, obj.gender, obj.nationality, obj.religion,\
        obj.ethnicity, educaional_level, obj.years_of_experience, obj.highest_qualification, direct_manager,\
        obj.current_address, obj.permanent_address, obj.email, obj.personal_email, obj.phone, department, obj.type_of_labor]
      
      data.append([x for x in PROFILE_STATUSES if x[0] == obj.status][0][1])

      xlsx.add_row(data)

    xlsx.close()
    output.seek(0)

    response = HttpResponse(
      output,
      content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="HR_Export.xlsx"'
    return response

  @action(detail=False, methods=['post'], permission_classes=[])
  def download(self, request, pk=None):
    download = Download.objects.create(
      query = json.dumps(request.data),
      created_by = request.user,
      export_type = 'hrm'
    )

    return Response({'detail': 'Download is in progress', 'id': download.id}, status=status.HTTP_200_OK)

class TitleFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    class Meta:
        model = Title
        fields = ['name', 'code']

    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains', 'code__icontains']
        _q = Q()
        for field in fields:
         _q = _q | Q(**{field: value})
        
        return queryset.filter(_q)

class TitleViewSet(viewsets.ModelViewSet):
  queryset = Title.objects.all()
  serializer_class = TitleSerializer
  filterset_class = TitleFilter
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    print('self.action', self.action)
    if self.action == 'list':
      return TitleListSerializer
    return TitleSerializer


class TrustedDeviceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Return simplified data, never the token itself
        devices = request.user.trusted_devices.all().values(
            'id', 'ip_address', 'user_agent', 'last_used_at'
        )
        return Response(list(devices))

    def delete(self, request, *args, **kwargs):
        device_id = request.data.get('device_id')
        if not device_id:
            return Response({'error': 'Device ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure the user can only delete their own devices
        try:
            device_to_delete = request.user.trusted_devices.get(id=device_id)
            device_to_delete.delete()
            return Response({'detail': 'Device has been removed.'}, status=status.HTTP_204_NO_CONTENT)
        except TrustedDevice.DoesNotExist:
            return Response({'error': 'Device not found.'}, status=status.HTTP_404_NOT_FOUND)


class CustomerFilter(FilterSet):
  search = django_filters.CharFilter(method='elastic_search')
  curator = django_filters.CharFilter(method='filter_curator')
  curator__isnull = django_filters.BooleanFilter(method='filter_curator_isnull')
  curators = django_filters.CharFilter(method='filter_curators')
  statuses = django_filters.CharFilter(method='filter_statuses')

  def filter_curator_isnull(self, queryset, name, value):
    if value:
      return queryset.filter(curators__isnull=True)
    return queryset.exclude(curators__isnull=True)

  class Meta:
    model = Customer
    fields = ['name', 'email', 'phone', 'address', 'company_name', 'type_of_customer', 'curators', 'customer_code', 'stage','status', 'customer_source', 'customer_group']

  def elastic_search(self, queryset, name, value):
    if not value:
      return queryset
    
    fields = ['name__icontains', 'email__icontains', 'phone__icontains', 'address__icontains', 'company_name__icontains', 'company_tax_code']
    _q = Q()
    for field in fields:
      _q = _q | Q(**{field: value})

    return queryset.filter(_q)

  def filter_curator(self, queryset, name, value):
    return queryset.filter(curators__id=value)  # Filter by a specific curator ID

  def filter_curators(self, queryset, name, value):
    if not value:
        return queryset

    curator_ids = value.split(',')
    return queryset.filter(curators__id__in=curator_ids).distinct()

  def filter_statuses(self, queryset, name, value):
    if not value:
        return queryset

    status_ids = value.split(',')
    print('status_ids', status_ids)
    return queryset.filter(status__in=status_ids).distinct()

class CustomerViewSet(viewsets.ModelViewSet):
  queryset = Customer.objects.all()
  serializer_class = CustomerSerializer
  filterset_class = CustomerFilter
  ordering_fields = ['id']
  ordering = ('-id',)

  def get_serializer_class(self):
    if self.action == 'list':
      return CustomerListSerializer
    elif self.action == 'retrieve':
      return CustomerDetailSerializer
    return CustomerSerializer
  
  @action(detail=False, methods=['post'])
  def delete_customers(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    customer_ids = request.data['customers']
    if not customer_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for customer_id in customer_ids:
      try:
        profile = Customer.objects.get(pk=customer_id)
        profile.delete()
      except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)

  @action(detail=True, methods=['post'])
  def convert_to_customer(self, request, pk=None):
    customer = self.get_object()
    if not customer:
      return Response({'detail': 'Contact not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    customer.stage = 2
    customer.save()

    return Response(CustomerSerializer(customer).data, status=status.HTTP_200_OK)

  @action(detail=True, methods=['post'])
  def contact_change_status(self, request, pk=None):
    customer = self.get_object()
    if not customer:
      return Response({'detail': 'Contact not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status', None)
    if not new_status:
      return Response({'detail': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    customer.status = new_status
    customer.save()

    return Response(CustomerSerializer(customer).data, status=status.HTTP_200_OK)

  @action(detail=False, methods=['post'], permission_classes=[])
  def contact_download(self, request, pk=None):
    download = Download.objects.create(
      query = json.dumps(request.data),
      created_by = request.user,
      export_type = 'contact'
    )

    return Response({'detail': 'Download is in progress', 'id': download.id}, status=status.HTTP_200_OK)

  @action(detail=False, methods=['post'], permission_classes=[])
  def download(self, request, pk=None):
    download = Download.objects.create(
      query = json.dumps(request.data),
      created_by = request.user,
      export_type = 'customer'
    )

    return Response({'detail': 'Download is in progress', 'id': download.id}, status=status.HTTP_200_OK)

  @action(detail=False, methods=['get'])
  def export_contacts(self, request, pk=None):
    qs = self.get_queryset()
    qs = self.filter_queryset(qs)
    is_user = request.user.profile_hr.role == 'U'

    HEADERS = ['No.','HỌ VÀ TÊN', 'MÃ LIÊN HỆ', 'DANH XƯNG', 'NGÀY SINH', \
      'GIỚI TÍNH', 'NGƯỜI PHỤ TRÁCH', 'ĐỊA CHỈ', 'EMAIL', 'ĐIỆN THOẠI', 'MÃ SỐ THUẾ', 'LOẠI LIÊN HỆ','NGUỒN LIÊN HỆ','TÊN CÔNG TY', 'SỐ ĐIỆN THOẠI CÔNG TY','EMAIL CÔNG TY','ĐỊA CHỈ CÔNG TY', \
      'MÃ SỐ THUẾ CÔNG TY']

    SHEET_NAME = 'DANH SÁCH LIÊN HỆ'
    output = io.BytesIO()
    xlsx = ExportXlsx(output, SHEET_NAME)
    xlsx.add_header(HEADERS)

    CUSTOMER_TYPES = (
      (1, 'Cá nhân'),
      (2, 'Tổ chức'),
    )
    CUSTOMER_SOURCES = (
      (1, 'Facebook'),
      (2, 'Instagram'),
      (3, 'Google'),
      (4, 'Khách cũ giới thiệu'),
      (5, 'Website'),
      (6, 'Tự tìm kiếm'),
      (7, 'Tổng đài'),
      (8, 'Môi giới'),
      (9, 'Dữ liệu bán hàng')
    )
    for x, obj in enumerate(qs):
      curators = ''
      type_of_customer = ''
      customer_source = ''
      if obj.curators.exists():
        curators = ', '.join([user.username for user in obj.curators.all()])
      if obj.type_of_customer:
        type_of_customer = ([x for x in CUSTOMER_TYPES if x[0] == obj.type_of_customer][0][1])
      if obj.customer_source:
        customer_source = ([x for x in CUSTOMER_SOURCES if x[0] == obj.customer_source][0][1])

      data = [x+1, obj.name, obj.customer_code, obj.title, obj.dob, \
        obj.gender, curators, obj.address, obj.email, obj.phone, obj.tax_code, type_of_customer,\
        customer_source, obj.company_name, obj.company_phone, obj.company_email, obj.company_address,\
        obj.company_tax_code]
      
      # data.append([x for x in PROFILE_STATUSES if x[0] == obj.status][0][1])

      xlsx.add_row(data)

    xlsx.close()
    output.seek(0)

    response = HttpResponse(
      output,
      content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Contacts_Export.xlsx"'
    return response


  @action(detail=False, methods=['get'])
  def export_customers(self, request, pk=None):
    qs = self.get_queryset()
    qs = self.filter_queryset(qs)
    is_user = request.user.profile_hr.role == 'U'

    HEADERS = ['No.','HỌ VÀ TÊN', 'MÃ KHÁCH HÀNG', 'DANH XƯNG', 'NGÀY SINH', \
      'GIỚI TÍNH', 'NGƯỜI PHỤ TRÁCH', 'ĐỊA CHỈ', 'EMAIL', 'ĐIỆN THOẠI', 'MÃ SỐ THUẾ', 'LOẠI KHÁCH HÀNG','NGUỒN KHÁCH HÀNG','NHÓM KHÁCH HÀNG','TÊN CÔNG TY', 'SỐ ĐIỆN THOẠI CÔNG TY','EMAIL CÔNG TY','ĐỊA CHỈ CÔNG TY', \
      'MÃ SỐ THUẾ CÔNG TY']

    SHEET_NAME = 'DANH SÁCH KHÁCH HÀNG'
    output = io.BytesIO()
    xlsx = ExportXlsx(output, SHEET_NAME)
    xlsx.add_header(HEADERS)

    CUSTOMER_TYPES = (
      (1, 'Cá nhân'),
      (2, 'Tổ chức'),
    )
    CUSTOMER_GROUPS = (
      (1, 'Khánh hàng trung thành'),
      (2, 'Khách hàng cũ'),
      (3, 'Khách hàng tiềm năng'),
      (4, 'Khách vãng lai'),
      (5, 'Khách hàng tiềm năng mới'),
      (6, 'Khách hàng đang chăm sóc'),
      (7, 'VIP'),
      (8, 'VVIP')
    )
    CUSTOMER_SOURCES = (
      (1, 'Facebook'),
      (2, 'Instagram'),
      (3, 'Google'),
      (4, 'Khách cũ giới thiệu'),
      (5, 'Website'),
      (6, 'Tự tìm kiếm'),
      (7, 'Tổng đài'),
      (8, 'Môi giới'),
      (9, 'Dữ liệu bán hàng')
    )
    for x, obj in enumerate(qs):
      curators = ''
      type_of_customer = ''
      customer_group = ''
      customer_source = ''
      if obj.curators.exists():
        curators = ', '.join([user.username for user in obj.curators.all()])
      if obj.type_of_customer:
        type_of_customer = ([x for x in CUSTOMER_TYPES if x[0] == obj.type_of_customer][0][1])
      if obj.customer_source:
        customer_source = ([x for x in CUSTOMER_SOURCES if x[0] == obj.customer_source][0][1])
      if obj.customer_group:
        customer_group = ([x for x in CUSTOMER_GROUPS if x[0] == obj.customer_group][0][1])
      data = [x+1, obj.name, obj.customer_code, obj.title, obj.dob, \
        obj.gender, curators, obj.address, obj.email, obj.phone, obj.tax_code, type_of_customer,\
        customer_source, customer_group, obj.company_name, obj.company_phone, obj.company_email, obj.company_address,\
        obj.company_tax_code]
      
      # data.append([x for x in PROFILE_STATUSES if x[0] == obj.status][0][1])

      xlsx.add_row(data)

    xlsx.close()
    output.seek(0)

    response = HttpResponse(
      output,
      content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Customers_Export.xlsx"'
    return response
class WorkFilter(FilterSet):
  search = django_filters.CharFilter(method='elastic_search')
  assigned_to_person = django_filters.CharFilter(method='filter_assigned_to_person')
  assigned_to__isnull = django_filters.BooleanFilter(method='filter_assigned_to_isnull')
  assigned_tos = django_filters.CharFilter(method='filter_assigned_tos')
  assigned_bys = django_filters.CharFilter(method='filter_assigned_bys')
  managers = django_filters.CharFilter(method='filter_managers')
  statuses = django_filters.CharFilter(method='filter_statuses')
  priorities = django_filters.CharFilter(method='filter_priorities')
  class Meta:
    model = Works
    fields = ['name', 'assigned_to','status','code', 'priority']

  def filter_assigned_to_isnull(self, queryset, name, value):
    if value:
      return queryset.filter(assigned_to__isnull=True)
    return queryset.exclude(assigned_to__isnull=True)

  def elastic_search(self, queryset, name, value):
    if not value:
      return queryset
    
    fields = ['name__icontains','code__icontains']
    _q = Q()
    for field in fields:
      _q = _q | Q(**{field: value})

    return queryset.filter(_q)

  def filter_assigned_to_person(self, queryset, name, value):
    return queryset.filter(assigned_to__id=value)  # Filter by a specific curator ID

  def filter_assigned_tos(self, queryset, name, value):
    if not value:
        return queryset

    assigned_to__ids = value.split(',')
    return queryset.filter(assigned_to__id__in=assigned_to__ids).distinct()

  def filter_assigned_bys(self, queryset, name, value):
    if not value:
        return queryset

    assigned_by_ids = value.split(',')
    return queryset.filter(assigned_by__id__in=assigned_by_ids).distinct()

  def filter_managers(self, queryset, name, value):
    if not value:
        return queryset

    manager_ids = value.split(',')
    return queryset.filter(managers__id__in=manager_ids).distinct()

  def filter_statuses(self, queryset, name, value):
    if not value:
        return queryset

    status_ids = value.split(',')
    return queryset.filter(status__in=status_ids).distinct()
  
  def filter_priorities(self, queryset, name, value):
    if not value:
        return queryset

    priority_ids = value.split(',')
    return queryset.filter(priority__in=priority_ids).distinct()

class WorkViewSet(viewsets.ModelViewSet):
  queryset = Works.objects.all()
  serializer_class = WorkSerializer
  filterset_class = WorkFilter
  ordering_fields = ['id']
  ordering = ('-id',)

  def get_serializer_class(self):
    if self.action == 'list':
      return WorkListSerializer
    elif self.action == 'retrieve':
      return WorkDetailSerializer
    return WorkSerializer
  
  @action(detail=False, methods=['post'])
  def delete_work(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    work_ids = request.data['profiles']
    if not work_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for work_id in work_ids:
      try:
        work = Works.objects.get(pk=work_id)
        work.delete()
      except Works.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)

  @action(detail=False, methods=['post'])
  def delete_works(self, request, pk=None):
    # role = request.user.profile.role
    # print(role)
    # if role == 'M':
    #   return Response(status=status.HTTP_403_FORBIDDEN)
    work_ids = request.data['works']
    if not work_ids:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    for work_id in work_ids:
      try:
        work = Works.objects.get(pk=work_id)
        work.delete()
      except Works.DoesNotExist:
        pass
      except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)

  @action(detail=False, methods=['get'])
  def export_work_list(self, request, pk=None):
    qs = self.get_queryset()
    qs = self.filter_queryset(qs)
    is_user = request.user.profile_hr.role == 'U'

    HEADERS = ['No.','TÊN CÔNG VIỆC', 'MÃ CÔNG VIỆC', 'MÔ TẢ', 'TRẠNG THÁI', \
      'NGƯỜI THỰC HIỆN', 'NGƯỜI GIAO', 'NGƯỜI QUẢN LÝ', 'NGÀY BẮT ĐẦU', 'NGÀY BẮT ĐÀU THỰC TẾ', 'NGÀY KẾT THÚC', 'ĐỘ ƯU TIÊN']

    SHEET_NAME = 'DANH SÁCH CÔNG VIỆC'
    output = io.BytesIO()
    xlsx = ExportXlsx(output, SHEET_NAME)
    xlsx.add_header(HEADERS)

    PRIORITY_CHOICES = (
      (1, 'Low'),
      (2, 'Medium'),
      (3, 'High'),
      (4, 'Urgent'),
      (5, 'Critical'),
      (6, 'None'),
    )
    STATUSES = (
      (1, 'Not Started'),
      (2, 'In Progress'),
      (3, 'Completed'),
      (4, 'On Hold'),
      (5, 'Cancelled'),
      (6, 'Deferred'),
      (7, 'Waiting for Review'),
      (8, 'Approved'),
      (9, 'Rejected'),
      (10, 'Pending'),
      (11, 'Failed'),
      (12, 'Success'),
      (13, 'Archived'),
      (14, 'Deleted'),
      (15, 'Draft'),
    )
    for x, obj in enumerate(qs):
      assigned_tos = ''
      assigned_bys = ''
      managers = ''
      priority = ''
      status = ''
      customer_source = ''
      if obj.assigned_to.exists():
        assigned_tos = ', '.join([user.username for user in obj.assigned_to.all()])
      if obj.assigned_by.exists():
        assigned_bys = ', '.join([user.username for user in obj.assigned_by.all()])
      if obj.managers.exists():
        managers = ', '.join([user.username for user in obj.managers.all()])
      if obj.priority:
        priority = ([x for x in PRIORITY_CHOICES if x[0] == obj.priority][0][1])
      if obj.status:
        status = ([x for x in STATUSES if x[0] == obj.status][0][1])
      start_date = obj.start_date.replace(tzinfo=None) if obj.start_date else ''
      actual_start_date = obj.actual_start_date.replace(tzinfo=None) if obj.actual_start_date else ''
      end_date  = obj.end_date.replace(tzinfo=None) if obj.end_date else ''
      data = [x+1, obj.name, obj.code, obj.description, status,  assigned_tos, assigned_bys, \
      managers, start_date, actual_start_date, end_date, priority]
      
      # data.append([x for x in PROFILE_STATUSES if x[0] == obj.status][0][1])

      xlsx.add_row(data)

    xlsx.close()
    output.seek(0)

    response = HttpResponse(
      output,
      content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Works_Export.xlsx"'
    return response

  @action(detail=True, methods=['get'])
  def history(self, request, pk=None):
      work = self.get_object()
      model = work.history.__dict__['model']
      works_history = Works.history.filter(id=pk).order_by('-history_date')
      serializer = WorkHistorySerializer(model, works_history, many=True)
      serializer.is_valid()

      return Response(serializer.data, status=status.HTTP_200_OK)