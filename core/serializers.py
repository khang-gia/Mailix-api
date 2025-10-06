from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from system.models import ScheduleEvent
from system.serializers import DepartmentListSerializer
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'

class LoginSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=100, required=True)
  password = serializers.CharField(max_length=100, required=True)
  
  def to_representation(self, instance):
    data = super().to_representation(instance)
    # data['email'] = data['username']
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
        exclude = ['password', 'user_permissions', 'is_superuser', 'is_staff']


    def get_full_name(self, obj):
      return '%s %s' % (obj.first_name, obj.last_name) if obj.first_name else obj.username if not hasattr(obj, 'profile_hr') else obj.profile_hr.full_name

  
class ProfileHRDetailSerializer(serializers.ModelSerializer):
    department = DepartmentListSerializer(read_only=True)
    title_name = serializers.CharField(source='title.name', read_only=True)
    type_of_labor_name = serializers.CharField(source='get_type_of_labor_display', read_only=True)
    direct_manager = UserListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
      model = ProfileHR
      fields = '__all__'
  

class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    profile_hr = ProfileHRDetailSerializer(read_only=True, required=False)
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'is_staff']

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

class UserOtherViewSerializer(serializers.ModelSerializer):
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
    system_date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    class Meta:
      model = ProfileHR
      fields = '__all__'

class ProfileHRSerializer(serializers.ModelSerializer):
    class Meta:
      model = ProfileHR
      fields = '__all__'

    def update(self, instance, validated_data):
      personal_email = validated_data.get('personal_email', None)
      print('Personal email:', personal_email)
      # update profile fields
      for attr, value in validated_data.items():
          setattr(instance, attr, value)
      instance.save()

      # update user personal_email if provided
      if personal_email and instance.user:
          print('Updating user email to:', personal_email)
          instance.user.email = personal_email
          instance.user.save()

      return instance

class TitleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Title
    fields = '__all__'

class TitleListSerializer(serializers.ModelSerializer):
  class Meta:
    model = Title
    fields = '__all__'

class CustomerAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAddtionalInfo
        exclude = ['customer',]

class CustomerSerializer(serializers.ModelSerializer):
    additional_infos = CustomerAdditionalSerializer(many=True, required=False)
    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
      curators = validated_data.pop('curators', [])
      additional_infos = validated_data.pop('additional_infos', [])
      
      type_of_customer = validated_data.pop('type_of_customer', None)
      if type_of_customer == 1:
        company_fields = [
        'company_name', 'company_address', 'company_phone',
        'company_email', 'company_tax_code', 'company_type', 'line_of_business'
        ]
        for field in company_fields:
          validated_data[field] = None
        
      customer = Customer.objects.create(**validated_data)
      customer.curators.set(curators)
      if additional_infos:
        for info in additional_infos:
          contact_additional_info = ContactAddtionalInfo.objects.create(customer=customer, **info)
      return customer

    def update(self, instance, validated_data):
      curators = validated_data.pop('curators', None)
      type_of_customer = validated_data.pop('type_of_customer', None)
      additional_infos = validated_data.pop('additional_infos', [])
      
      if type_of_customer == 1:
        company_fields = [
        'company_name', 'company_address', 'company_phone',
        'company_email', 'company_tax_code', 'company_type', 'line_of_business'
        ]
        for field in company_fields:
          validated_data[field] = None
      for attr, value in validated_data.items():
        setattr(instance, attr, value)
      if curators is not None:
        instance.curators.set(curators)
      instance.save()
      if additional_infos:
        instance.additional_infos.all().delete()
        for info in additional_infos:
          ContactAddtionalInfo.objects.create(customer=instance, **info)
      return instance

class CustomerListSerializer(serializers.ModelSerializer):
    customer_source = serializers.CharField(source='get_customer_source_display', read_only=True)
    customer_group = serializers.CharField(source='get_customer_group_display', read_only=True)
    type_of_customer = serializers.CharField(source='get_type_of_customer_display', read_only=True) 
    curators = UserOtherViewSerializer(read_only=True, many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'

class CustomerDetailSerializer(serializers.ModelSerializer):
    curators = UserListSerializer(read_only=True, many=True)
    additional_infos = CustomerAdditionalSerializer(many=True, read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'

class ScheduleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEvent
        fields = '__all__'

    def create(self, validated_data):
      participants = validated_data.pop('participants', [])
      event = ScheduleEvent.objects.create(**validated_data)
      event.participants.set(participants)
      return event

    def update(self, instance, validated_data):
      participants = validated_data.pop('participants', None)

      for attr, value in validated_data.items():
        setattr(instance, attr, value)
      
      if participants is not None:
        instance.participants.set(participants)
      
      instance.save()
      return instance

class ScheduleEventListSerializer(serializers.ModelSerializer):
    user = UserOtherViewSerializer(read_only=True)
    class Meta:
        model = ScheduleEvent
        exclude = [ 'participants']

class ScheduleEventDetailSerializer(serializers.ModelSerializer):
    user = UserOtherViewSerializer(read_only=True)
    participants = UserListSerializer(read_only=True, many=True)
    
    class Meta:
        model = ScheduleEvent
        fields = '__all__'

class WorkSerializer(serializers.ModelSerializer):
    schedule = ScheduleEventSerializer(required=False, allow_null=True)
    class Meta:
        model = Works
        fields = '__all__'

    def create(self, validated_data):
      assigned_to = validated_data.pop('assigned_to', [])
      assigned_by = validated_data.pop('assigned_by', [])
      managers = validated_data.pop('managers', [])
      schedule_data = validated_data.pop('schedule', None)
      work = Works.objects.create(**validated_data)
      work.assigned_to.set(assigned_to)
      work.assigned_by.set(assigned_by)
      work.managers.set(managers)
      if schedule_data:
        participants = schedule_data.pop('participants', [])
        schedule_data['user'] = work.created_by if not schedule_data.get('user') else schedule_data['user']
        schedule_event = ScheduleEvent.objects.create(work=work, **schedule_data)
        schedule_event.participants.set(participants)
      return work

    def update(self, instance, validated_data):
      assigned_to = validated_data.pop('assigned_to', None)
      assigned_by = validated_data.pop('assigned_by', None)
      managers = validated_data.pop('managers', None)
      # schedule_data = validated_data.pop('schedule', None)

      for attr, value in validated_data.items():
        setattr(instance, attr, value)
      
      if assigned_to is not None:
        instance.assigned_to.set(assigned_to)
      if assigned_by is not None:
        instance.assigned_by.set(assigned_by)
      if managers is not None:
        instance.managers.set(managers)
      # if schedule_data:
      #   try:
      #     schedule_event = ScheduleEvent.objects.get(work=instance)
      #     for attr, value in schedule_data.items():
      #       setattr(schedule_event, attr, value)
      #     schedule_event.save()
      #   except ScheduleEvent.DoesNotExist:
      #     ScheduleEvent.objects.create(work=instance, **schedule_data)
      instance.save()
      return instance

class WorkListSerializer(serializers.ModelSerializer):
    assigned_to = UserOtherViewSerializer(read_only=True, many=True)
    assigned_by = UserOtherViewSerializer(read_only=True, many=True)
    managers = UserOtherViewSerializer(read_only=True, many=True)
    created_by = UserOtherViewSerializer(read_only=True)
    class Meta:
        model = Works
        fields = '__all__'
      

class WorkDetailSerializer(serializers.ModelSerializer):
    assigned_to = UserListSerializer(read_only=True, many=True)
    assigned_by = UserListSerializer(read_only=True, many=True)
    managers = UserListSerializer(read_only=True, many=True)
    
    class Meta:
        model = Works
        fields = '__all__'

  