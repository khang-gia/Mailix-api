from django.db import models
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from core.mixins.base_model import BaseModel, BaseCreateDeleteModel, BaseCreateUpdateDeleteModel, BaseCreateUpdateModel
from simple_history.models import HistoricalRecords
import filetype
import uuid
import os
# Create your models here.
ROLE_CHOICES = (
  ('U', 'User'),
  ('M', 'Manager'),
  ('A', 'Admin'),
  ('RA', 'Readonly Admin'),
)
SYSTEM_ROLE_CHOICES = (
  ('U', 'User'),
  ('M', 'Manager'),
  ('A', 'Admin'),
  ('RA', 'Readonly Admin'),
  ('SA', 'System Admin'),
)
ETHNICITY_CHOICES = (
  (0, "Kinh"),
  (1, "Tày"),
  (2, "Thái"),
  (3, "Mường"),
  (4, "Khmer"),
  (5, "H’Mông (Mong)"),
  (6, "Nùng"),
  (7, "Dao"),
  (8, "Gia Rai"),
  (9, "Ê Đê"),
  (10, "Ba Na"),
  (11, "Sán Chay"),
  (12, "Chăm (Cham)"),
  (13, "Cơ Ho"),
  (14, "Xơ Đăng"),
  (15, "Sán Dìu"),
  (16, "Hrê"),
  (17, "Mnông"),
  (18, "Ra Glai"),
  (19, "Xinh Mun"),
  (20, "Bru-Vân Kiều"),
  (21, "Thổ"),
  (22, "Giáy"),
  (23, "Cơ Tu"),
  (24, "Gié-Triêng"),
  (25, "Tà Ôi"),
  (26, "Mạ"),
  (27, "Khơ Mú"),
  (28, "Co"),
  (29, "Chứt"),
  (30, "Lự"),
  (31, "Lô Lô"),
  (32, "Mảng"),
  (33, "Cờ Lao"),
  (34, "Bố Y"),
  (35, "Si La"),
  (36, "Pu Péo"),
  (37, "Brâu"),
  (38, "Ơ Đu"),
  (39, "Rơ Măm"),
  (40, "Ngái"),
  (41, "Xtiêng"),
  (42, "Hà Nhì"),
)
RELIGION_CHOICES = (
  (0, 'Không'),
  (1, 'Cơ đốc giáo'),
  (2, 'Phật giáo'),
  (3, 'Hòa hảo'),
  (4, 'Tin lành'),
  (5, 'Tây giáo'),
  (6, 'Hồi giáo'),
  (7, 'Bà la môn'),
  (8, 'Cao đài'),
  (9, 'Phật giáo Lương'),
  (10, 'Công giáo'),
  (11, 'Thiên chúa giáo'),
  (12, 'Khác'),
)
MILITARY_STATUS_CHOICES = (
  (0, "Performed"),
  (1, "Haven't performed"),
  (2, "Not required"),
)
MARITAL_STATUS_CHOICES = (
  ('Single', "Single"),
  ('Married', "Married"),
  ('Divorced', "Divorced"),
)
EDUCATION_LEVEL_CHOICES = (
  (1, "1/12"),
  (2, "2/12"),
  (3, "3/12"),
  (4, "4/12"),
  (5, "5/12"),
  (6, "6/12"),
  (7, "7/12"),
  (8, "8/12"),
  (9, "9/12"),
  (10, "10/12"),
  (11, "11/12"),
  (12, "12/12"),
)
TYPE_OF_LABOR_CHOICES = (
  ('Full-time', "Full-time"),
  ('Part-time', "Part-time"),
  ('Temporary', "Temporary"),
  ('Internship', "Internship"),
)
TYPE_PASSPORT_CHOICES = (
  (0, "Ordinary"),
  (1, "Official"),
  (2, "Diplomatic"),
)

class Title(models.Model):
  code = models.CharField("Code", max_length=20)
  name = models.CharField("Name", max_length=50)
  description = models.TextField('Description',null=True, blank=True)


  def __str__(self):
      return "Title <{}> {}".format(self.pk, self.name)
class Position(models.Model):
  code = models.CharField("Code", max_length=20)
  name = models.CharField("Name", max_length=50)
  description = models.TextField('Description',null=True, blank=True)

  def __str__(self):
    return "Position <{}> {}".format(self.code, self.name)

class Nationality(models.Model):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Nationality <{}> {}".format(self.pk, self.name)

class TimekeepingLocation(BaseModel):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Timekeeping Location <{}> {}".format(self.pk, self.name)

class Bank(models.Model):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Bank <{}> {}".format(self.pk, self.name)

class UserBankAccount(BaseCreateUpdateDeleteModel):
    user = models.ForeignKey("ProfileHR", on_delete=models.CASCADE, related_name='bank_accounts')
    bank = models.ForeignKey("core.Bank", on_delete=models.CASCADE, related_name='users')
    account_number = models.CharField("Account Number", max_length=20)
    account_name = models.CharField("Account Name", max_length=200)
    branch = models.CharField("Branch", max_length=200)

    def __str__(self):
        return "User Bank Account <{}> {}".format(self.user, self.bank)
FAMILY_RELATIONSHIP_CHOICES = (
  (0, "Father"),
  (1, "Mother"),
  (2, "Son"),
  (3, "Daughter"),
  (4, "Brother"),
  (5, "Sister"),
  (6, "Husband"),
  (7, "Wife"),
  (8, "Grandfather"),
  (9, "Grandmother"),
  (10, "Grandson"),
  (11, "Granddaughter"),
  (12, "Uncle"),
  (13, "Aunt"),
  (14, "Nephew"),
  (15, "Niece"),
)
class FamilyRelationship(BaseCreateUpdateDeleteModel):
    user = models.ForeignKey("ProfileHR", on_delete=models.CASCADE, related_name='family_relationships')
    relationship = models.IntegerField("Relationship", choices=FAMILY_RELATIONSHIP_CHOICES, null=True, blank=True)
    full_name = models.CharField("Full Name", max_length=200, null=True, blank=True)
    dob = models.DateField("Date of Birth", null=True, blank=True)
    phone = models.CharField("Phone", max_length=20, null=True, blank=True)
    email = models.EmailField("Email", null=True, blank=True)
    id_number = models.CharField("ID Number", max_length=20, null=True, blank=True)
    date_of_issue = models.DateField("Date of Issue", null=True, blank=True)
    place_of_issue = models.CharField("Place of Issue", max_length=200, null=True, blank=True)
    is_dependent = models.BooleanField("Is Dependent", default=False)
    from_date = models.DateField("From Date", null=True, blank=True)
    to_date = models.DateField("To Date", null=True, blank=True)
    tax_code = models.CharField("Tax Code", max_length=20, null=True, blank=True)
    occupation = models.CharField("Occupation", max_length=200, null=True, blank=True)
    def __str__(self):
        return "Family Relationship <{}> {}".format(self.user, self.relationship)

PROFESSIONAL_QUALIFICATION_TYPE_CHOICES = (
  (0, "Formal Education"),
  (1, "Service Education"),
  (2, "Profession"),
  (3, "Semi-Profession"),
  (4, "2nd Degree"),
  (5, "Work & Study"),
  (6, "Distance"),
  (7, "Focus"),
  (8, "Short-term"),
  (9, "Advanced"),
)
DEGREE_CHOICES = (
  (0, "Bachelor"),
  (1, "Master"),
  (2, "Doctor"),
)
class ProfessionalQualification(BaseCreateUpdateDeleteModel):
    user = models.ForeignKey("ProfileHR", on_delete=models.CASCADE, related_name='professional_qualifications')
    from_date = models.DateField("From Date", null=True, blank=True)
    to_date = models.DateField("To Date", null=True, blank=True)
    type_of_edu= models.IntegerField("Type", choices=PROFESSIONAL_QUALIFICATION_TYPE_CHOICES)
    major = models.CharField("Major", max_length=200, null=True, blank=True)
    degree = models.IntegerField("Degree", choices=DEGREE_CHOICES)
    institution = models.CharField("Institution", max_length=200, null=True, blank=True)
    def __str__(self):
        return "Professional Qualification <{}> {}".format(self.user, self.degree)

COMMUNIST_PARTY_MEMBER_FORM_CHOICES = (
  (0, "On probation"),
  (1, "Full fledged"),
  (2, "Transferred"),
)
class CommunistPartyMember(models.Model):
  card_no = models.CharField("Card No", max_length=100, null=True, blank=True)
  form = models.IntegerField("Form", choices=COMMUNIST_PARTY_MEMBER_FORM_CHOICES)
  from_date = models.DateField("From Date", null=True, blank=True)
  to_date = models.DateField("To Date", null=True, blank=True)
  admission_place = models.CharField("Admission Place", max_length=200, null=True, blank=True)
  transfer_place = models.CharField("Transfer Place", max_length=200, null=True, blank=True)
  user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name='communist_party_members')

  def __str__(self):
    return "Communist Party Member <{}> {}".format(self.user, self.card_no)
PROFILE_STATUSES = (
  (0, 'Working'),
  (1, 'Temporary absent'),
  (2, 'Resigned'),
  (3, 'Providing service'),
  (4, 'Pending for recruitment'),
)

ACCOUNT_STATUSES = (
  (0, 'Active'),
  (1, 'Inactive'),
  (2, 'Pending'),
  (3, 'Locked'),
  (4, 'Deactive'),
)
class ProfileHR(BaseCreateUpdateDeleteModel):
    full_name = models.CharField("Full Name", max_length=200, db_index=True)
    user = models.OneToOneField("auth.User", on_delete=models.SET_NULL, related_name='profile_hr', db_index=True, null=True, blank=True, unique=True)
    avatar = models.ImageField("Avatar", upload_to='avatars', null=True, blank=True)
    department = models.ForeignKey("system.Department", on_delete=models.SET_NULL, related_name="profile_hr", null=True, blank=True)
    employee_code = models.CharField("Employee Code", max_length=50)
    ref_uuid = models.UUIDField("Reference UUID", default=uuid.uuid4, editable=False, db_index=True, null=True, blank=True)
    #Personal Info
    timekeeping_id = models.CharField("Timekeeping ID", max_length=50, null=True, blank=True)
    profile_code = models.CharField("Profile Code", max_length=100, null=True, blank=True)
    dob = models.DateField("Date of Birth", null=True, blank=True)
    pob = models.CharField("Place of Birth", max_length=200, null=True, blank=True)
    place_of_origin = models.CharField("Place of Origin", max_length=200, null=True, blank=True)
    gender = models.CharField("Gender", max_length=10, null=True, blank=True)
    phone = models.CharField("Phone", max_length=20, null=True, blank=True)
    phone_other = models.CharField("Mobile", max_length=20, null=True, blank=True)
    title = models.ForeignKey('core.Title', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey('core.Position', on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField('Role', max_length=5, choices=ROLE_CHOICES, default='U')
    religion = models.CharField('Religion',max_length=20, null=True, blank=True)
    ethnicity = models.CharField('Ethnicity', max_length=20, null=True, blank=True)
    military_status = models.IntegerField('Military Status', choices=MILITARY_STATUS_CHOICES, null=True, blank=True, default=0)
    marital_status = models.CharField('Marital Status',max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True, default='Single')
    nationality = models.CharField('Nationality', max_length=30, null=True, blank=True, default=0)
    tax_code = models.CharField('Tax Code', max_length=20, null=True, blank=True)
    blood_presure = models.CharField('Blood Presure', max_length=20, null=True, blank=True)
    join_date = models.DateField('Join Date', null=True, blank=True)
    actual_sign_date = models.DateField('Actual Sign Date', null=True, blank=True)
    educaional_level = models.IntegerField('Educational Level', choices=EDUCATION_LEVEL_CHOICES, null=True, blank=True, default=0)
    years_of_experience = models.CharField('Years of Experience',max_length=20, null=True, blank=True)
    major = models.CharField('Major', max_length=200, null=True, blank=True)
    highest_qualification = models.CharField('Highest Professional Qualification', max_length=200, null=True, blank=True)
    direct_manager = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='manage_users')
    type_of_labor = models.CharField('Type of Labor', choices=TYPE_OF_LABOR_CHOICES, null=True, blank=True, default='Full-time', max_length=20)

    #Passport Info
    id_number = models.CharField('ID No/Passport', max_length=20, null=True, blank=True)
    date_of_issue = models.DateField('Date of Issue', null=True, blank=True)
    place_of_issue = models.CharField('Place of Issue', max_length=200, null=True, blank=True)
    front_id_card = models.ImageField('Front ID Card', upload_to='id_card/front/', null=True, blank=True)
    back_id_card = models.ImageField('Back ID Card', upload_to='id_card/back/', null=True, blank=True)
    type_of_passport = models.IntegerField('Type of ID Card', choices=TYPE_PASSPORT_CHOICES, null=True, blank=True, default=0)
    passport_number = models.CharField('Passport Number', max_length=20, null=True, blank=True)
    date_of_issue_pp = models.DateField('Date of Issue', null=True, blank=True)
    date_of_expiry_pp = models.DateField('Date of Expiry', null=True, blank=True)
    place_of_issue_pp = models.CharField('Place of Issue', max_length=200, null=True, blank=True)
    front_passport = models.ImageField('Front Passport', upload_to='passport/front/', null=True, blank=True)

    #Contact Info
    phone_number = models.CharField('Phone Number', max_length=20, null=True, blank=True)
    email = models.EmailField('Email', null=True, blank=True)
    personal_email = models.EmailField('Personal Email', null=True, blank=True)
    permanent_address = models.CharField('Permanent Address', max_length=200, null=True, blank=True)
    current_address = models.CharField('Current Address', max_length=200, null=True, blank=True)
    public_name = models.CharField('Bút danh', max_length=50, null=True, blank=True)
    # status = models.CharField('Status', choices=PROFILE_STATUSES, default='Active', max_length=100, null=True, blank=True)
    status = models.IntegerField('Status', choices=PROFILE_STATUSES, default=0, null=True, blank=True, db_index=True)
    status_start_date = models.DateField('Status Start Date', null=True, blank=True, help_text='Date when current status begins')
    status_end_date = models.DateField('Status End Date', null=True, blank=True, help_text='Date when current status ends (for temporary absent)')
    account_status = models.IntegerField('Account Status', choices=ACCOUNT_STATUSES, default=0, null=True, blank=True, db_index=True)
    group = models.ForeignKey('system.SystemGroup',  on_delete=models.SET_NULL, related_name="profile_hrs", null=True, blank=True)
    is_first_login = models.BooleanField('Is First Login', default=True)
    is_demo_account = models.BooleanField('Is Demo Account', default=False)
    history = HistoricalRecords()

    def __str__(self):
        return "ProfileHR<{}> {}".format(self.pk, self.full_name)


class SystemNotification(models.Model):
    title = models.CharField("Title", max_length=200)
    image = models.ImageField(upload_to='system', null=True, blank=True)
    message = models.TextField("Message", null=True, blank=True)
    link_to = models.CharField("Link to", max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    show_popup = models.BooleanField("Show Popup", default=False)
    popup_time = models.DateTimeField("Popup time", null=True, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200, null=True, blank=True)
    feedback = models.TextField("Feedback", null=True, blank=True)
    image = models.ImageField(upload_to='feedback', null=True, blank=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    
    def __str__(self):
        return '{}: {}'.format(self.user, self.title)
    
class HotEvent(models.Model):
    title = models.CharField('Title', max_length=100)
    html_id = models.CharField('HTML ID', max_length=200, null=True, blank=True)
    css_classes = models.CharField('Animate Classes', max_length=200, default='animate-pulse text-yellow-600', null=True, blank=True)
    url = models.URLField("Url", null=True, blank=True)
    target = models.URLField("Target", null=True, blank=True)
    active = models.BooleanField('Active', default=False, db_index=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)

    def __str__(self) -> str:
      return f'{self.title} | {self.active}'
    
class HappeningEvent(models.Model):
  title = models.CharField("Title", max_length=200)
  embed_url = models.URLField("Embed Url", null=True, blank=True)
  start_time = models.DateTimeField("Start Time", db_index=True)
  end_time = models.DateTimeField("End Time", db_index=True)
  active = models.BooleanField('Active', default=False, db_index=True)
  
  def __str__(self):
        return self.title

USER_STATUSES = (
  (0, 'Created'),
  (1, 'Active'),
  (2, 'Pending'),
  (3, 'Locked'),
  (9, 'Deactive')
)
class Profile(BaseCreateUpdateDeleteModel):
  group = models.ForeignKey('system.SystemGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles", db_index=True)
  is_system_admin = models.BooleanField('Is System Admin', default=False, db_index=True)
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', db_index=True)
  is_adjus_permission = models.BooleanField('Is Adjust Permission',default=False, db_index=True)
  status = models.IntegerField('Status', choices=USER_STATUSES, default=0, null=True, blank=True, db_index=True)
  active_date = models.DateField('Active Date', null=True, blank=True, db_index=True)
  email_verified = models.BooleanField(default=False)
  phone_verified = models.BooleanField(default=False)
  role = models.CharField('Role', max_length=10, choices=SYSTEM_ROLE_CHOICES, default='U', db_index=True)
  def __str__(self):
      return 'UserProfile-{}'.format(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		# if not ProfileHR.objects.filter(user=instance).exists():
		# 	ProfileHR.objects.create(user=instance)


CONTRACT_TYPES = (
  (0, 'Probationary'),
  (1, 'Apprenticeship'),
  (2, '6-month'),
  (3, '1-year'),
  (4, '3-year'),
  (5, 'Part-time'),
  (6, 'Indefinite-term'),
  
)
# LEVELS = (
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
#   (0,'Level 1'),
  
# )
# class Contract(BaseCreateUpdateDeleteModel):
#   code = models.CharField("Code", max_length=100)
#   contract_type = models.IntegerField('Type', choices=CONTRACT_TYPES, default=0, db_index=True)
#   department = models.ForeignKey("system.Department", on_delete=models.SET_NULL, related_name="contracts", null=True, blank=True, db_index=True)
#   title = models.ForeignKey('core.Title', on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts', db_index=True)
#   position = models.ForeignKey('core.Position',on_delete=models.SET_NULL, null=True, blank=True,related_name='contracts', db_index=True)
#   level = models.IntegerField('Level', choices=)


CUSTOMER_TYPES = (
  (1, 'Personal'),
  (2, 'Organization'),
)
CUSTOMER_GROUPS = (
  (1, 'Loyal Customer'),
  (2, 'Former Customer'),
  (3, 'Potential Customer'),
  (4, 'Casual Customer'),
  (5, 'Newly acquired lead'),
  (6, 'Nurturing customer lead'),
  (7, 'VIP'),
  (8, 'VVIP')
)
CUSTOMER_SOURCES = (
  (1, 'Facebook'),
  (2, 'Instagram'),
  (3, 'Google'),
  (4, 'Old customer referral'),
  (5, 'Website'),
  (6, 'Self-searching'),
  (7, 'Switchboard'),
  (8, 'Broker'),
  (9, 'Sale data')
)
COMPANY_TYPES = (
  (1, 'Limited Liability Company'),
  (2, 'Joint Stock Company'),
  (3, 'Partnership'),
  (4, 'Sole Proprietorship'),
  (5, 'State-owned Enterprise'),
  (6, 'Foreign Enterprise'),
  (7, 'Cooperative'),
  (8, 'Non-profit Organization'),
)
LINE_OF_BUSINESS_CHOICES = (
  (1, 'Retail'),
  (2, 'Wholesale'),
  (3, 'Manufacturing'),
  (4, 'Service'),
  (5, 'Technology'),
  (6, 'Healthcare'),
  (7, 'Education'),
  (8, 'Finance'),
  (9, 'Real Estate'),
  (10, 'Transportation'),
  (11, 'Construction'),
  (12, 'Hospitality'),
  (13, 'Entertainment'),
  (14, 'Agriculture'),
  (15, 'Other'),
)
CUSTOMER_STATUSES = (
  (1, 'New'),
  (2, '1st Contacted'),
  (3, '2nd Contacted'),
  (4, 'Consulting'),
  (5, 'Negotiating'),
  (6, 'Contracted'),
  (7, 'Quoted'),
  (8, 'Old Customer'),
  (10, 'Others')
)
CUSTOMER_STAGES = (
  (1, 'CONTACT'),
  (2, 'CUSTOMER'),
  (3, 'DEAL'),
  (4, 'INVOICE'),
  (5, 'PAYMENT'),
  (6, 'DELIVERY'),
  (7, 'COMPLETED'),
)
TITLES = (
  (1, 'Ông'),
  (2, 'Bà'),
  (3, 'Cô'),
  (4, 'Anh'),
  (5, 'Chị'),
  (6, 'Tiến sĩ'),
  (7, 'Giáo sư'),
  (8, 'Mr.'),
  (9, 'Ms.'),
  (10, 'Mrs.'),
  (11, 'Dr.'),
  (12, 'Prof.'),
  (13, 'Sir'),
  (14, 'Madam'),
  (15, 'Lord'),
  (16, 'Lady'),
)

class Customer(BaseCreateUpdateDeleteModel):
    name = models.CharField("Name", max_length=200, db_index=True)
    avatar = models.ImageField("Avatar", upload_to='customer_avatars', null=True, blank=True)
    customer_code = models.CharField("Customer Code", max_length=100, null=True, blank=True, db_index=True)
    email = models.EmailField("Email", null=True, blank=True, db_index=True)
    phone = models.CharField("Phone", max_length=20, null=True, blank=True, db_index=True)
    address = models.CharField("Address", max_length=200, null=True, blank=True, db_index=True)
    gender = models.CharField("Gender", max_length=10, null=True, blank=True)
    dob = models.DateField("Birthday", null=True, blank=True, db_index=True)
    note = models.TextField("Note", null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    attachment = models.FileField("Attachment", upload_to='customer_attachments/', null=True, blank=True)
    tax_code = models.CharField("Tax Code", max_length=20, null=True, blank=True, db_index=True)
    id_number = models.CharField("ID Number", max_length=20, null=True, blank=True, db_index=True)
    company_name = models.CharField("Company Name", max_length=200, null=True, blank=True, db_index=True)
    company_address = models.CharField("Company Address", max_length=200, null=True, blank=True, db_index=True)
    company_phone = models.CharField("Company Phone", max_length=20, null=True, blank=True, db_index=True)
    company_email = models.EmailField("Company Email", null=True, blank=True, db_index=True)
    company_tax_code = models.CharField("Company Tax Code", max_length=20, null=True, blank=True, db_index=True)
    company_type = models.CharField("Company Type", max_length=100, null=True, blank=True, db_index=True)
    line_of_business = models.CharField("Line of Business", max_length=100, null=True, blank=True, db_index=True)
    curators = models.ManyToManyField(User, related_name='contacts', null=True, blank=True, db_index=True)
    type_of_customer = models.IntegerField("Type of customer", choices=CUSTOMER_TYPES, default=1, db_index=True)
    customer_group = models.IntegerField("Customer Group", choices=CUSTOMER_GROUPS, default=1, db_index=True)
    customer_source = models.IntegerField("Customer Source", choices=CUSTOMER_SOURCES, default=1, db_index=True)
    website = models.URLField("Website", null=True, blank=True)
    status = models.IntegerField("Status", choices=CUSTOMER_STATUSES, default=1, null=True, blank=True, db_index=True)
    stage = models.IntegerField("Stage", choices=CUSTOMER_STAGES, default=1, null=True, blank=True, db_index=True)
    title = models.CharField("Title", max_length=15,  null=True, blank=True, db_index=True)
    history = HistoricalRecords()

    class Meta:
      unique_together = ('customer_code', 'stage')
    def __str__(self):
        return self.name

def customer_attachment_path(instance, filename):
    """
    Generates the upload path for CustomerAttachment files using the unique customer code.
    Automatically renames duplicate filenames by adding (1), (2), etc.
    Format: '<customer_code>/customer_attachments/<filename>' or '<customer_code>/customer_attachments/<filename> (n)'
    """
    from django.core.files.storage import default_storage
    
    # Use the unique and immutable customer code
    customer_code = instance.customer.customer_code
    
    # Split filename into name and extension
    name, ext = os.path.splitext(filename)
    
    # Base path for customer attachments
    base_dir = os.path.join(customer_code, 'customer_attachments')
    
    # Start with the original filename
    final_filename = filename
    counter = 1
    
    # Keep checking until we find a unique filename
    while default_storage.exists(os.path.join(base_dir, final_filename)):
        final_filename = f"{name} ({counter}){ext}"
        counter += 1
    
    # Construct the final path
    return os.path.join(base_dir, final_filename)
def comment_attachment_path(instance, filename):
    """
    Saves Comment attachments under /<user_code>/comment_attachment/
    """
    customer_code = instance.customer.code
    
    return os.path.join(
        customer_code, 
        'comment_attachment', 
        filename
    )
class CustomerAttachment(BaseCreateUpdateDeleteModel):
    customer = models.ForeignKey(Customer,related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to=customer_attachment_path)
    filename = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    historical = HistoricalRecords()
    
    def save(self, *args, **kwargs):
        # Call parent save first to let Django process the upload_to function
        super().save(*args, **kwargs)
        
        # After saving, extract the actual filename from the file path
        # This will include any (1), (2) suffixes added by our custom upload_to function
        if self.file and not self.filename:
            # Get just the filename from the full path (e.g., "customer_code/customer_attachments/file (1).pdf" -> "file (1).pdf")
            self.filename = os.path.basename(self.file.name)
            # Update only the filename field without triggering another save cycle
            CustomerAttachment.objects.filter(pk=self.pk).update(filename=self.filename)

    def __str__(self):
        return f"Attachment for Customer {self.customer.name}: {self.filename or 'No Name'}"

class CustomerComment(BaseCreateUpdateDeleteModel):
    customer = models.ForeignKey(Customer, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='customer_replies')
    likes = models.ManyToManyField(User, related_name='customer_liked_comments', blank=True)
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return "Comment <{}> by {}".format(self.pk, self.user)

class CustomerCommentAttachment(models.Model):
    comment = models.OneToOneField(
        'CustomerComment', related_name='attachment', on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='customer_comment_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # 'image' or 'file'
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        
        # Auto-detect file type based on extension
        if self.file and not self.file_type:
            ext = self.filename.split('.')[-1].lower() if self.filename else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            else:
                self.file_type = 'file'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Attachment for Comment {self.comment.pk}: {self.filename or 'No Name'}"

CONTACT_ADDITIONAL_INFO_TYPES = (
  (1, 'Email'),
  (2, 'Phone'),
  (3, 'Address'),
  (4, 'Website'),
  (5, 'Facebook'),
  (6, 'LinkedIn'),
  (7, 'Twitter'),
  (8, 'Instagram'),
  (9, 'Skype'),
  (10, 'WhatsApp'),
  (11, 'Telegram'),
  (12, 'Viber'),
  (13, 'Zalo'),
  (14, 'WeChat'),
  (15, 'Other'),
)
class ContactAddtionalInfo(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='additional_infos', db_index=True)
    type_of_contact = models.IntegerField("Type of Contact", choices=CONTACT_ADDITIONAL_INFO_TYPES, default=1, db_index=True)
    description = models.TextField("Value", null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.get_type_of_contact_display(), self.description)

# CONTACT_STATUSES = (
#   (0, 'New'),
#   (1, '1st Contacted'),
#   (2, '2nd Contacted'),
#   (3, 'Consulting'),
#   (4, 'Negotiating'),
#   (5, 'Contracted'),
#   (6, 'Quoted'),
#   (7, 'Old Customer'),
#   (9, 'Others')
# )

# class Contacts(BaseCreateUpdateDeleteModel):
#     # customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts', db_index=True)
#     full_name = models.CharField("Full Name", max_length=200, db_index=True)
#     email = models.EmailField("Email", null=True, blank=True, db_index=True)
#     phone = models.CharField("Phone", max_length=20, null=True, blank=True, db_index=True)
#     position = models.CharField("Position", max_length=100, null=True, blank=True, db_index=True)
#     note = models.TextField("Note", null=True, blank=True)
#     status = models.IntegerField("Status", choices=CONTACT_STATUSES, default=0, null=True, blank=True, db_index=True)

#     history = HistoricalRecords()

#     def __str__(self):
#         return self.full_name
PRIORITY_CHOICES = (
  (1, 'Low'),
  (2, 'Medium'),
  (3, 'High'),
  (4, 'Urgent'),
  (5, 'Critical'),
  (6, 'None'),
)
STATUSES = (
  (1, 'Not Started'),
  (2, 'Backlog'),
  (3, 'To Do'),
  (4, 'In Progress'),
  (5, 'Completed'),
  (6, 'On Hold'),
  (7, 'Cancelled'),
  (8, 'Deferred'),
  (9, 'Waiting for Review'),
  (10, 'Approved'),
  (11, 'Rejected'),
  (12, 'Pending'),
  (13, 'Failed'),
  (14, 'Success'),
  (15, 'Archived'),
  (16, 'Deleted'),
  (17, 'Draft'),
)
class Works(BaseCreateUpdateDeleteModel):
    name = models.CharField("Name", max_length=200, db_index=True)
    code = models.CharField("Code", max_length=100, unique=True, null=True, blank=True, db_index=True)
    description = models.TextField("Description", null=True, blank=True)
    start_date = models.DateTimeField("Start Date", null=True, blank=True, db_index=True)
    end_date = models.DateTimeField("End Date", null=True, blank=True, db_index=True)
    actual_start_date = models.DateTimeField("Actual start Date", null=True, blank=True, db_index=True)
    assigned_to = models.ManyToManyField(User, related_name='works', blank=True, db_index=True)
    assigned_by = models.ManyToManyField(User, related_name='assigned_works', blank=True, db_index=True)
    assigned_at = models.DateTimeField("Assigned At", null=True, blank=True, db_index=True)
    managers = models.ManyToManyField(User, related_name='managed_works', blank=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_works', db_index=True)
    priority = models.IntegerField("Priority", choices=PRIORITY_CHOICES, default=2, null=True, blank=True, db_index=True)
    status = models.IntegerField("Status", choices=STATUSES, default=1, null=True, blank=True, db_index=True)
    progress = models.PositiveIntegerField(default=0)
    related_work = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_works', db_index=True)
    brief = models.TextField("Brief", null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return "Work <{}> {}".format(self.pk, self.name)


class WorkAttachment(BaseCreateUpdateDeleteModel):
    work = models.ForeignKey(Works, related_name='attachments', on_delete=models.CASCADE, db_index=True)
    file = models.FileField(upload_to='work_attachments/')
    filename = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    historical = HistoricalRecords()
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Attachment for Work {self.work.name}: {self.filename or 'No Name'}"

class WorkComment(BaseCreateUpdateDeleteModel):
    work = models.ForeignKey(Works, related_name='comments', on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Comment <{self.pk}> by {self.user}"

class WorkCommentAttachment(models.Model):
    comment = models.OneToOneField(
        'WorkComment', related_name='attachment', on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='work_comment_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # 'image' or 'file'
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        
        # Auto-detect file type based on extension
        if self.file and not self.file_type:
            ext = self.filename.split('.')[-1].lower() if self.filename else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            else:
                self.file_type = 'file'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Attachment for Comment {self.comment.pk}: {self.filename or 'No Name'}"

