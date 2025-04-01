from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('stcians', 'STCians'),
        ('student_other', 'Student (Other Colleges)'),
        ('teacher', 'Teacher'),
        ('alumni', 'Alumni'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='stcians')
    email = models.EmailField(unique=True, blank=False, null=False)  # Ensures email is unique and required
    department_name = models.CharField(max_length=50, blank=True, null=True)
    semester = models.CharField(max_length=10, blank=True, null=True)
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Set unique=True
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
from django.db import models
from django.conf import settings

class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    textbook_name = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    semester = models.PositiveIntegerField()
    image = models.ImageField(upload_to='book_images/')
    feedback = models.TextField(blank=True, null=True)  # Optional feedback field
    rating = models.PositiveIntegerField(blank=True, null=True, choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)])  # Star rating (1-5)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.CharField(max_length=50, default='free')  # New price field with default value 'free'
    available = models.BooleanField(default=True)  # New field to track availability

    def __str__(self):
        return self.textbook_name

from django.db import models

class StudyMaterial(models.Model):
    subject = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    semester = models.PositiveIntegerField()
    description = models.TextField(help_text="E.g., Topics discussed: Basics of Machine Learning, Linear Regression, Neural Networks...")
    file = models.FileField(upload_to='study_materials/')

    def __str__(self):
        return f"{self.subject} - {self.module} (Semester {self.semester})"

    class Meta:
        verbose_name = 'Study Material'
        verbose_name_plural = 'Study Materials'


from django.db import models
from django.conf import settings  # Ensure AUTH_USER_MODEL is correctly referenced

class Textbook(models.Model):
    name = models.CharField(max_length=255, verbose_name="Textbook Name")
    author = models.CharField(max_length=255, verbose_name="Author Name")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    semester = models.PositiveSmallIntegerField(
        verbose_name="Semester", choices=[(i, f"Semester {i}") for i in range(1, 9)]
    )
    image = models.ImageField(upload_to="textbook_images/", verbose_name="Image")
    feedback = models.TextField(blank=True, null=True, verbose_name="Feedback")
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        verbose_name="Rating",
        blank=True,
        null=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price (INR)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    available = models.BooleanField(default=True, verbose_name="Available")  # New availability field
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE,
    verbose_name="Uploaded By"
)
 # Ensures that when a user is deleted, their books are removed

    def __str__(self):
        return f"{self.name} by {self.author} (₹{self.price})"
# ----------------------------
from django.db import models
from django.conf import settings

class BookRequest(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    
    donation_place = models.CharField(max_length=255)
    donation_time = models.TimeField()
    donation_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.book.textbook_name} by {self.receiver.username}"



from django.db import models
from django.conf import settings
from datetime import date

class SellRequest(models.Model):
    textbook = models.ForeignKey('Textbook', on_delete=models.CASCADE, verbose_name="Requested Textbook")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buy_requests", verbose_name="Buyer")
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sell_requests", verbose_name="Requester")  # New field
    place = models.CharField(max_length=255, verbose_name="Meeting Place")
    time = models.CharField(max_length=50, verbose_name="Meeting Time")
    date = models.DateField(default=date.today, verbose_name="Meeting Date")
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
            ('Completed', 'Completed')
        ],
        default='Pending',
        verbose_name="Request Status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Request Created At")

    def __str__(self):
        return f"{self.requester.username} requested {self.textbook.textbook_name} - {self.status}"



from django.db import models
from django.conf import settings  # Import settings to get custom user model
from .models import Book

class Notification(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="donor_notifications", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="receiver_notifications", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # Copying details from BookRequest
    donation_date = models.DateField(null=True, blank=True)
    donation_time = models.TimeField(null=True, blank=True)
    donation_place = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=20, choices=[("Accepted", "Accepted"), ("Rejected", "Rejected")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.book.textbook_name} - {self.status}"

from django.db import models
from django.conf import settings  # Import settings to get custom user model
from .models import SellRequest  # Import SellRequest model

class SellNotification(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sell_notifications", on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="buy_notifications", on_delete=models.CASCADE)
    sell_request = models.ForeignKey(SellRequest, on_delete=models.CASCADE)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requester_notifications", on_delete=models.CASCADE)  # New field
    # Copying details from SellRequest
    meeting_date = models.DateField(null=True, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_place = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[("Accepted", "Accepted"), ("Rejected", "Rejected")],
        verbose_name="Request Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sell Notification: {self.sell_request.textbook.textbook_name} - {self.status}"
    
    
#audio#
from django.db import models
from django.contrib.auth.models import User

class AudioNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    semester = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='audio_notes/')  # Stores the recorded audio
    created_at = models.DateTimeField(auto_now_add=True)
    transcribed_text = models.TextField(blank=True, null=True)  # Add this field
    pdf_file = models.FileField(upload_to="pdf/", blank=True, null=True)  # Add this 

    def __str__(self):
        return self.title
