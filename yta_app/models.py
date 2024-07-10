from django.db import models
import uuid
from django.db.models import Max
from django.db import transaction
from ytauser.models import CustomUser  # Import CustomUser from ytauser.models
import base64
from PIL import Image
import io
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    address = models.TextField()
    email = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    primary_contact_number = models.CharField(max_length=15)
    website = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_organizations")

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'organization'
        verbose_name = "organization"
        verbose_name_plural = "organization"

class IconUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    icon_file = models.FileField(upload_to='icons/', help_text="Upload the icon file")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="uploaded_icon")


    def __str__(self):
        return f"Icon {self.id} uploaded by {self.uploaded_by.mobile if self.uploaded_by else 'Unknown'}"


class OverlayUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    overlay_file = models.FileField(upload_to='overlay/', help_text="Upload the overlay file")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="uploaded_overaly")


    def __str__(self):
        return f"Overlay {self.id} uploaded by {self.uploaded_by.mobile if self.uploaded_by else 'Unknown'}"

class CatalogItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=255, help_text="Name of the main category")
    sub_category_name = models.CharField(max_length=255, help_text="Name of the sub-category")
    sub_category_icon = models.ForeignKey('IconUpload', on_delete=models.SET_NULL, null=True, blank=True, related_name="catalog_items", help_text="Foreign Key to the icon upload")
    overlay = models.ForeignKey('OverlayUpload', on_delete=models.SET_NULL, null=True, blank=True, related_name="catalog_overlay", help_text="Foreign Key to the icon upload")
    classname = models.CharField(max_length=255, null=True, blank=True)
    success_message = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.CharField(max_length=255, null=True, blank=True)
    detection_info = models.CharField(max_length=255, null=True, blank=True)
    help_text = models.CharField(max_length=255, null=True, blank=True)
    reserved1 = models.CharField(max_length=255, null=True, blank=True)
    reserved2 = models.CharField(max_length=255, null=True, blank=True)    
    description = models.TextField(blank=True, help_text="Detailed description of the catalog item")
    score = models.IntegerField(default=0, help_text="Score or rating of the catalog item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_catalog_items")
    
    def __str__(self):
        return f"{self.category_name} - {self.sub_category_name}"

    class Meta:
        db_table = 'catalog'
        verbose_name = "Catalog Item"
        verbose_name_plural = "Catalog Items"


class SurveyTemplate(models.Model):
    survey_id = models.AutoField(primary_key=True)
    catalog_id = models.ForeignKey('CatalogItem', on_delete=models.CASCADE, related_name="surveys")
    survey_date = models.DateField()
    description = models.TextField(blank=True)
    survey_template = models.JSONField()  # Updated to use the standard JSONField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey Template {self.survey_id} for Catalog Item {self.catalog_id}"

    class Meta:
        db_table = 'SurveyTemplate'
        verbose_name = "Survey"
        verbose_name_plural = "Surveys"

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255,null=True, blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    job_number = models.CharField(max_length=20, unique=True)
    category_list = models.CharField(max_length=255, default='Others', blank=True)
    categories = models.JSONField(default=list)  # Assuming default categories function is defined elsewhere
    job_name = models.CharField(max_length=255)
    job_description = models.TextField()
    assigned_person = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_jobs')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_jobs')
    accepted_date = models.DateTimeField(null=True, blank=True)
    accepted_by = models.CharField(max_length=255, null=True, blank=True)
    additional_notes = models.CharField(max_length=255, null=True, blank=True)
    end_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    job_image = models.ImageField(upload_to='job_images/', null=True, blank=True)
    is_template = models.BooleanField(default=False)
    template_names = models.CharField(max_length=255, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, default='APD', blank=True, related_name='jobs')
    status = models.CharField(max_length=10, choices=[('Accepted', 'Accepted'), ('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    is_accepted = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')

    @classmethod
    def generate_job_number(cls):
        with transaction.atomic():
            # Retrieve the maximum job_number in the database, defaulting to 99 if none is found
            last_job = cls.objects.aggregate(max_job_number=Max('job_number'))
            last_job_number = last_job['max_job_number']
            if last_job_number is None:
                return "100"
            next_job_number = str(int(last_job_number) + 1)
            return next_job_number

    def save(self, *args, **kwargs):
        if not self.job_number:
            self.job_number = Job.generate_job_number()
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_name} ({self.job_number})"
    



class ImageUpload(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='imageuploaded_user',null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    subcategory = models.TextField(null=True, blank=True)
    flagged_reason = models.TextField(null=True, blank=True)
    image_name_ai = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    folder = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='uploaded_images')
    jobno = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='uploaded_images')
    survey = models.JSONField(default=list)  # Survey data in JSON format

    def __str__(self):
        return self.name

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lb_user')
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    task = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task} - {self.user_id}"


class StreamData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inference_data = models.JSONField(default=dict)
    image = models.ForeignKey('ImageUpload', on_delete=models.CASCADE, related_name='stream_data',null=True, blank=True)
    category = models.CharField(max_length=255)
    site = models.CharField(max_length=255)
    engine_identity = models.CharField(max_length=255)
    camera_state = models.IntegerField(default=0)
    generated_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.site}"


class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    publication_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_news")

    def __str__(self):
        return self.title
