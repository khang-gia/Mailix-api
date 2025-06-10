from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from system.serializers import DepartmentListSerializer
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'

class LoginSerializer(serializers.Serializer):
  username = serializers.EmailField(max_length=100, required=True)
  password = serializers.CharField(max_length=100, required=True)
  
  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['email'] = data['username']
    return data

class OTPSerializer(serializers.Serializer):
  code = serializers.CharField(max_length=6, required=True)
  email = serializers.EmailField(max_length=100, required=True)

class UsernameSerializer(serializers.Serializer):
  username = serializers.EmailField(max_length=100, required=True)

class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def get_full_name(self, obj):
      return '%s %s' % (obj.first_name, obj.last_name) if obj.first_name else obj.username if not hasattr(obj, 'profile_hr') else obj.profile_hr.full_name

  
class ProfileHRDetailSerializer(serializers.ModelSerializer):
    department = DepartmentListSerializer(read_only=True)
    title_name = serializers.CharField(source='title.name', read_only=True)
    type_of_labor_name = serializers.CharField(source='get_type_of_labor_display', read_only=True)
    direct_manager = UserListSerializer(read_only=True)
    class Meta:
      model = ProfileHR
      fields = '__all__'
  

class UserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=False)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    profile_hr = ProfileHRDetailSerializer(read_only=True, required=False)
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'is_superuser', 'is_staff']

    def get_display_name(self, obj):
        return '%s %s'%(obj.first_name, obj.last_name) if obj.first_name else obj.username if not hasattr(obj, 'profile_hr') else obj.profile_hr.full_name

    def get_avatar(self, obj):
      request = self.context.get('request')
      if hasattr(obj, 'profile_hr') and obj.profile_hr and obj.profile_hr.avatar:
        avatar_url = obj.profile_hr.avatar.url
        if request is not None:
          return request.build_absolute_uri(avatar_url)

        return avatar_url
      return None


    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
  name = serializers.SerializerMethodField(read_only=True)
  public_name = serializers.CharField(read_only=True, source='profile.public_name')
  class Meta:
    model = User
    fields = ['id', 'name', 'public_name', 'email']
    
  def get_name(self, obj):
    return '%s %s'%(obj.first_name, obj.last_name) if obj.first_name else obj.username



class SystemNotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = SystemNotification
    fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
  name = serializers.SerializerMethodField(read_only=True)
  public_name = serializers.CharField(read_only=True, source='profile.public_name')
  class Meta:
    model = User
    fields = ['id', 'name', 'public_name', 'email']
    
  def get_name(self, obj):
    return '%s %s'%(obj.first_name, obj.last_name) if obj.first_name else obj.username

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['created_at']

class HappeningEventSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = HappeningEvent
    fields = '__all__'

class HotEventSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = HotEvent
    fields = '__all__'


class CredentialsSerializer(serializers.Serializer):
  username = serializers.EmailField(max_length=100, required=True)
  password = serializers.CharField(max_length=100, required=True)
  first_name = serializers.CharField(max_length=100, required=False)
  
  def validate(self, data):
    super().validate(data)
    
    username = data.get('username', None)
    
    if User.objects.filter(username=username).exists():
      raise serializers.ValidationError({'username': ['Email đã tồn tại. Vui lòng thử lại với email khác.']})

    return data
  
  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['email'] = data['username']
    return data


class ProfileHRListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    title_name = serializers.CharField(source='title.name', read_only=True)
    class Meta:
      model = ProfileHR
      fields = '__all__'

class ProfileHRSerializer(serializers.ModelSerializer):
    
    class Meta:
      model = ProfileHR
      fields = '__all__'

class TitleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Title
    fields = '__all__'

class TitleListSerializer(serializers.ModelSerializer):
  class Meta:
    model = Title
    fields = '__all__'
  