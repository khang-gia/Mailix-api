from rest_framework import serializers
from upload.models import Upload
from core.utils import get_user_name

class UploadSerializer(serializers.ModelSerializer):
  created_by_name = serializers.SerializerMethodField()
  status_name = serializers.CharField(source='get_status_display', read_only=True)
  
  class Meta:
    model = Upload
    fields = '__all__'
  
  def get_created_by_name(self, obj):
    return get_user_name(obj.created_by)

    