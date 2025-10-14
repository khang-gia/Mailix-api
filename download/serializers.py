from rest_framework import serializers
from download.models import Download

class DownloadSerializer(serializers.ModelSerializer):
  status_name = serializers.CharField(source='get_status_display', read_only=True)
  name = serializers.SerializerMethodField()

  class Meta:
    model = Download
    exclude = ['query']

  def get_name(self, obj):
    try:
      return obj.filename.name.split('/')[-1]
    except Exception:
      return ''
    
