from django.shortcuts import render
from .models import Profile, SystemNotification, Feedback, HappeningEvent, HotEvent, ProfileHR, Title, Customer
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer, SystemNotificationSerializer, FeedbackSerializer, HappeningEventSerializer, HotEventSerializer,\
  CredentialsSerializer, ProfileHRListSerializer, ProfileHRDetailSerializer, ProfileHRSerializer, UserListSerializer, TitleSerializer, TitleListSerializer, UsernameSerializer, \
    OTPSerializer, CustomerSerializer, CustomerListSerializer, CustomerDetailSerializer
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q, Count
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from core.utils_feature import otp
from core.utils_feature.mail import send_otp, send_forget_password_otp
from rest_framework.views import APIView

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
  user = User.objects.filter(username=username).first()
  if not user:
    return Response({'username': ['User does not exist.']}, status=status.HTTP_400_BAD_REQUEST)

  request.data['email'] = user.email
  code = OTPSerializer(data=request.data)
  if not code.is_valid():
    return Response(code.errors, status=status.HTTP_400_BAD_REQUEST)
  if not otp.verify(code.data['code'], code.data['email']):
    return Response({'code': ['Mã OTP không đúng hoặc đã hết hạn.']}, status=status.HTTP_400_BAD_REQUEST)
  user = User.objects.filter(username=code.data['email']).first()
  # user.profile.email_verified = True
  # user.profile.save()
  user_serializer = UserSerializer(user)
  return Response(user_serializer.data, status=status.HTTP_200_OK)

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
    return Response({'username': ['Email hoặc mật khẩu không đúng.']}, status=status.HTTP_400_BAD_REQUEST)
  user_serializer = UserSerializer(user)
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
    return Response({'username': ['Email hoặc mật khẩu không đúng.']}, status=status.HTTP_400_BAD_REQUEST)
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
    
@api_view(['POST'])
def change_password(request):
  user = request.user
  if user.check_password(request.data['password']):
    try:
      # allow to change
      user.set_password(request.data['new_password'])
      user.save()
      return Response(status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  return Response({'detail': 'PASSWORD_INVALID'}, status=status.HTTP_400_BAD_REQUEST)



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
  class Meta:
    model = ProfileHR
    fields = ['full_name','employee_code','status']

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
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not username or not email or not password:
      return Response({'detail': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not profile_hr:
      return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if User.objects.filter(email=email).exists():
      return Response({'detail': 'Email is already in use by another account.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
      return Response({'detail': 'Username is already in use by another account.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email)
    user.set_password(password)
    user.save()
    profile_hr.user = user
    profile_hr.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class TitleViewSet(viewsets.ModelViewSet):
  queryset = Title.objects.all()
  serializer_class = TitleSerializer
  ordering_fields = ['id']
  ordering = ('-id',)
  
  def get_serializer_class(self):
    print('self.action', self.action)
    if self.action == 'list':
      return TitleListSerializer
    return TitleSerializer


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        otp_code = request.data.get('otp_code')
        remember_device = request.data.get('remember_device', False)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # --- Check for a trusted device cookie BEFORE checking OTP ---
        trusted_device_token = request.COOKIES.get('trusted_device')
        if trusted_device_token:
            # Find a matching token for this user
            for device in user.trusted_devices.all():
                if check_password(trusted_device_token, device.token):
                    # Device is trusted, bypass OTP.
                    # Update last used timestamp
                    device.save() 
                    
                    # Issue auth token and log the user in
                    auth_token, _ = Token.objects.get_or_create(user=user)
                    return Response({'token': auth_token.key, 'detail': 'Login successful.'})

        # --- If no trusted device, proceed with OTP check ---
        if not is_valid_otp(user, otp_code): # Replace with your actual OTP validation logic
             return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # --- OTP is valid, now create a trusted device if requested ---
        if remember_device:
            # Generate a new secure token for the cookie
            new_token = secrets.token_hex(32)
            
            # Hash the token before saving to the database
            hashed_token = make_password(new_token)
            
            # Create the trusted device record
            TrustedDevice.objects.create(
                user=user,
                token=hashed_token,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Issue auth token
            auth_token, _ = Token.objects.get_or_create(user=user)
            
            # Create response and set the secure cookie
            response = Response({'token': auth_token.key, 'detail': 'Login and device verification successful.'})
            response.set_cookie(
                key='trusted_device',
                value=new_token,
                max_age=30 * 24 * 60 * 60,  # 30 days
                secure=not settings.DEBUG,  # True in production
                httponly=True,              # Crucial: prevents JS access
                samesite='Strict'           # Highly recommended
            )
            return response

        # --- If not remembering device, just log in normally after OTP ---
        auth_token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': auth_token.key, 'detail': 'Login successful.'})

class CustomerFilter(FilterSet):
  search = django_filters.CharFilter(method='elastic_search')
  curator = django_filters.CharFilter(method='filter_curator')
  curator__isnull = django_filters.BooleanFilter(method='filter_curator_isnull')
  
  def filter_curator_isnull(self, queryset, name, value):
    if value:
      return queryset.filter(curators__isnull=True)
    return queryset.exclude(curators__isnull=True)

  class Meta:
    model = Customer
    fields = ['name', 'email', 'phone', 'address', 'company_name', 'type_of_customer', 'curators', 'customer_code']

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