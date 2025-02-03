from django.db import models
from django.utils import timezone
from django_quill.fields import QuillField

from core.utils.date import is_dayoff, tplus

ARTICLE_TYPES = (
    (1, 'Khuyến nghị'),
    (2, 'Phân tích'),
    (3, 'Tin tức'),
    (9, 'Khác'),
)
ARTICLE_PRIVACIES = (
    (1, 'Miễn Phí'),
    (2, 'Có Phí'),
)
ARTICLE_STATUSES = (
    (1, 'Draft'),
    (2, 'Ready'),
    (3, 'Published'),
)
class Notification(models.Model):
    title = models.CharField("Tiêu đề", max_length=250, error_messages="Tiêu đề quá dài")
    message = models.TextField("Nội dung", null=True, blank=True)
    related_symbols = models.CharField("Mã CP", max_length=250, null=True, blank=True)
    type = models.IntegerField("Loại bài viết", default=1)
    link_to = models.CharField("Link to", max_length=200, null=True, blank=True)
    article_id = models.BigIntegerField('ID Bài viết', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_symbol_list(self):
        if self.related_symbols:
            return self.related_symbols.split(',')
        return []
        
    def edit_symbol_list(self, symbol_list):
        self.symbols = ','.join(symbol_list)

    def __str__(self):
        return 'Notification: [{}]'.format(self.title)

class ArticleType(models.Model):
    label = models.CharField("Label", max_length=50)
    value = models.IntegerField("Value", unique=True)

    def __str__(self) -> str:
        return '{} | {}'.format(self.value, self.label)

class Article(models.Model):
    title = models.CharField("Tiêu đề", max_length=250, error_messages="Tiêu đề quá dài")
    slug = models.SlugField("Slug", max_length=250, allow_unicode=False)
    thumb = models.ImageField("Hình ảnh", upload_to="articles", null=True, blank=True)
    message = models.TextField("Tóm tắt", null=True, blank=True)
    content = QuillField("Nội dung")
    related_symbols = models.CharField("Mã CP", max_length=250, null=True, blank=True)
    article_type = models.ForeignKey('consult.ArticleType', on_delete=models.CASCADE, null=True)
    privacy = models.IntegerField("Chính sách", choices=ARTICLE_PRIVACIES, default=1)
    status = models.IntegerField("Trạng thái", choices=ARTICLE_STATUSES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    published_at = models.DateTimeField("Thời gian xuất bản", default=timezone.now)
    has_notify = models.BooleanField('Gửi thông báo', default=False)
    source_name = models.CharField("Nguồn", max_length=200, null=True, blank=True)
    source_link = models.URLField("Link Nguồn", null=True, blank=True)

    def get_symbol_list(self):
        if self.related_symbols:
            return self.related_symbols.split(',')
        return []
        
    def edit_symbol_list(self, symbol_list):
        self.symbols = ','.join(symbol_list)

    def __str__(self):
        return 'Article: [{}]'.format(self.title)
    
class TelegramPushChannel(models.Model):
    
    channel_id = models.CharField("Channel Id", max_length=200, null=True, blank=True)
    enabled = models.BooleanField("Enabled", default=True)

    def __str__(self):
        return self.channel_id

CLOSED_REASONS = [
    (0, 'OPENING'),
    (1, 'REACHED TARGET'),
    (2, 'STOP LOSS'),
    (3, 'MACROECONOMICS'),
    (4, 'RE-ARRANGE PORFOLIO'),
    (5, 'OTHERS')

]
STRATEGIES = (
    ('T', 'Trading'),
    ('L', 'Long Term'),
    ('V', 'Value'),
)
class Recommendation(models.Model):

    symbol = models.CharField("Symbol", max_length=15, db_index=True)
    buy_date = models.DateField("Buy Date", null=True, blank=True)
    buy_price = models.FloatField("Buy Price", null=True, blank=True)
    stop_loss = models.FloatField("Stop Loss", null=True, blank=True)
    target_price = models.FloatField("Target Price", null=True, blank=True)
    ratio = models.FloatField("Ratio", null=True, blank=True)
    note = models.TextField("Note", null=True, blank=True)
    strategy = models.TextField('Strategy', max_length=5, choices=STRATEGIES, default='T')
    is_closed = models.BooleanField("Is Closed", default=False)
    closed_date = models.DateField("Close Date", null=True, blank=True)
    closed_price = models.FloatField("Latest / Close Price", null=True, blank=True)
    closed_reason = models.IntegerField('Closed Reason', choices=CLOSED_REASONS, default=0, null=True, blank=True)
    is_archived = models.BooleanField("Is Archived", default=False, db_index=True)

    created_at = models.DateTimeField('Created At', auto_now_add=True)
    
    @property
    def t_plus(self):

        if not self.buy_date:
            return None
        
        return tplus(self.buy_date, self.closed_date)
        
    @property
    def profit(self):
        if not self.closed_price or not self.buy_price:
            return None
        return 100 * (self.closed_price - self.buy_price) / self.buy_price
    