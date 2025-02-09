from django.db import models
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_softdelete.models import SoftDeleteModel

# Create your models here.

GENDER_CHOICES = (
  ('MALE', 'Male'),
  ('FEMALE', 'Female'),
)
ROLE_CHOICES = (
  ('U', 'User'),
  ('M', 'Manager'),
  ('A', 'Admin'),
  ('RA', 'Readonly Admin'),
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
  (0, "Single"),
  (1, "Married"),
  (2, "Divorced"),
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
  (0, "Full-time"),
  (1, "Part-time"),
  (2, "Temporary"),
  (3, "Internship"),
)
TYPE_PASSPORT_CHOICES = (
  (0, "Ordinary"),
  (1, "Official"),
  (2, "Diplomatic"),
)

class BaseCreateDeleteModel(SoftDeleteModel):
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    is_archived = models.BooleanField('Is Archived', default=False)
    archived_at = models.DateTimeField('Archived At', auto_now = True, null=True)
    class Meta:
        abstract = True

class BaseCreateUpdateModel(BaseCreateDeleteModel):
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        abstract = True

class Department(BaseCreateUpdateModel):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)
    location = models.CharField("Location", max_length=200, null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="childen")

    def _str_(self) -> str:
        return "Department <{}> {}".format(self.pk, self.name)

class Title(models.Model):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Title <{}> {}".format(self.pk, self.name)
class Nationality(BaseCreateUpdateModel):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Nationality <{}> {}".format(self.pk, self.name)

class TimekeepingLocation(BaseCreateUpdateModel):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Timekeeping Location <{}> {}".format(self.pk, self.name)

class Bank(models.Model):
    code = models.CharField("Code", max_length=20)
    name = models.CharField("Name", max_length=50)

    def __str__(self):
        return "Bank <{}> {}".format(self.pk, self.name)

class UserBankAccount(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name='bank_accounts')
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
class FamilyRelationship(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name='family_relationships')
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
class ProfessionalQualification(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name='professional_qualifications')
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


class Profile(BaseCreateUpdateModel):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey("core.Department", on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    employee_code = models.CharField("Employee Code", max_length=50)
    #Personal Info
    timekeeping_id = models.CharField("Timekeeping ID", max_length=50, null=True, blank=True)
    profile_code = models.CharField("Profile Code", max_length=100, null=True, blank=True)
    dob = models.DateField("Date of Birth", null=True, blank=True)
    pob = models.CharField("Place of Birth", max_length=200, null=True, blank=True)
    place_of_origin = models.CharField("Place of Origin", max_length=200, null=True, blank=True)
    gender = models.CharField("Gender", max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField("Phone", max_length=20, null=True, blank=True)
    phone_other = models.CharField("Mobile", max_length=20, null=True, blank=True)
    title = models.ForeignKey('core.Title', on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField('Role', max_length=5, choices=ROLE_CHOICES, default='U')
    religion = models.IntegerField('Religion', choices=RELIGION_CHOICES, null=True, blank=True, default=0)
    ethnicity = models.IntegerField('Ethnicity', choices=ETHNICITY_CHOICES, null=True, blank=True, default=0)
    military_status = models.IntegerField('Military Status', choices=MILITARY_STATUS_CHOICES, null=True, blank=True, default=0)
    marital_status = models.IntegerField('Marital Status', choices=MARITAL_STATUS_CHOICES, null=True, blank=True, default=0)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True, blank=True)
    tax_code = models.CharField('Tax Code', max_length=20, null=True, blank=True)
    blood_presure = models.CharField('Blood Presure', max_length=20, null=True, blank=True)
    join_date = models.DateField('Join Date', null=True, blank=True)
    actual_sign_date = models.DateField('Actual Sign Date', null=True, blank=True)
    educaional_level = models.IntegerField('Educational Level', choices=EDUCATION_LEVEL_CHOICES, null=True, blank=True, default=0)
    years_of_experience = models.IntegerField('Years of Experience', null=True, blank=True)
    major = models.CharField('Major', max_length=200, null=True, blank=True)
    highest_qualification = models.CharField('Highest Professional Qualification', max_length=200, null=True, blank=True)
    direct_manager = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='manage_users')
    type_of_labor = models.IntegerField('Type of Labor', choices=TYPE_OF_LABOR_CHOICES, null=True, blank=True, default=0)

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
    permanent_address = models.CharField('Permanent Address', max_length=200, null=True, blank=True)
    current_address = models.CharField('Current Address', max_length=200, null=True, blank=True)
    public_name = models.CharField('Bút danh', max_length=50, null=True, blank=True)

    def __str__(self):
        return "Profile<{}> {}".format(self.pk, self.user)


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
