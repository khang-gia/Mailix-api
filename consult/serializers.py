from rest_framework import serializers
from .models import Notification, Article, ArticleType
from core.serializers import AuthorSerializer

class NotificationSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True)
    symbol_list = serializers.SerializerMethodField(read_only=True)
    
    def get_symbol_list(self, instance: Notification):
        return instance.get_symbol_list()

    def get_type(self, instance: Notification):
        return instance.get_type_display()
    class Meta:
        ordering = '-created_at'
        model = Notification
        fields = ['id', 'title', 'message', 'symbol_list', 'related_symbols', 'created_at', 'type', 'link_to']

class ArticleNoAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ('content', 'related_symbols')

    
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ('content', 'related_symbols')

    
class ArticleDetailSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    created_by = AuthorSerializer()
    class Meta:
        model = Article
        exclude = ('related_symbols', )

    def get_content(self, instance):
        if instance.privacy == 1:
            return str(instance.content.html)
        
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user.profile.vip_level > 0:
                return str(instance.content.html)

        return ''    
    
class ArticleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleType
        fields = '__all__'
