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

class UserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=False)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'is_superuser', 'is_staff']

    def get_display_name(self, obj):
        # if obj.first_name:
        #     return "{} {}".format(obj.first_name, obj.last_name).strip()
        # return obj.username
        return '%s %s'%(obj.first_name, obj.last_name) if obj.first_name else obj.username

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
    department_name = serializers.CharField(source='department__name', read_only=True)
    class Meta:
      model = ProfileHR
      fields = '__all__'
  
class ProfileHRDetailSerializer(serializers.ModelSerializer):

    class Meta:
      model = ProfileHR
      fields = '__all__'
  
class ProfileHRSerializer(serializers.ModelSerializer):

    class Meta:
      model = ProfileHR
      fields = '__all__'