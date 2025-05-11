from django.shortcuts import render
from .models import Profile, SystemNotification, Feedback, HappeningEvent, HotEvent, ProfileHR, Title
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer, SystemNotificationSerializer, FeedbackSerializer, HappeningEventSerializer, HotEventSerializer,\
  CredentialsSerializer, ProfileHRListSerializer, ProfileHRDetailSerializer, ProfileHRSerializer, UserListSerializer, TitleSerializer, TitleListSerializer
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

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
def register(request, *args):
  credential = CredentialsSerializer(data=request.data)
  if not credential.is_valid():
    return Response(credential.errors, status=status.HTTP_400_BAD_REQUEST)
  
  user = User.objects.create_user(**credential.data)
  user_serializer = UserSerializer(user)

  # code = otp.generate(user.email)
  # send_otp(user.email, code)
  return Response(user_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT'])
def profile_api(request):
  if request.method == 'GET':
    return Response(UserSerializer(request.user).data)
  
  return update_profile(request)

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
#   if not user.profile.email_verified:
#     code = otp.generate(user.email)
#     send_otp(user.email, code)
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
        fields = ['username__icontains', 'first_name__icontains', 'last_name__icontains', 'profile__employee_code__icontains']
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
    fields = ['full_name','employee_code']

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
