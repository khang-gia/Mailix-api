from rest_framework import serializers
from .models import *
from core.utils import get_user_name

class TimeRecordSerializer(serializers.ModelSerializer):
  status_name = serializers.CharField(source='get_status_display', read_only=True)
  source_name = serializers.CharField(source='get_source_display', read_only=True)
  
  class Meta:
    model = TimeRecord
    fields = '__all__'
  

class TimeRecordListSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = TimeRecord
    fields = '__all__'

class TimeRecordDetailSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = TimeRecord
    fields = '__all__'