import json
import pytesseract
from PIL import Image
from django.conf import settings
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
from .models import Book
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, JsonResponse

User = get_user_model()  # Use the custom user model

# ----------SIGNUP VIEW --------------------
from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import login

def signup_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        department_name = request.POST.get('department_name')

        # Default values for Teachers and Alumni
        if role == 'teacher' or role == 'alumni':
            semester = 'N/A'  # Default value for Teachers/Alumni
            admission_number = 'N/A'  # Default value for Teachers/Alumni
        else:
            semester = request.POST.get('semester')
            admission_number = request.POST.get('admission_number')

        # Create CustomUser
        user = CustomUser.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            role=role, 
            phone_number=phone,
            department_name=department_name,
            semester=semester,
            admission_number=admission_number
        )

        # Log the user in after registration
        login(request, user)

        messages.success(request, 'Account created successfully!')

        if role == "alumni":
            return redirect('AlumniFrontPage') 
        
        return redirect('home')  # Redirect to the home page or a dashboard

    return render(request, 'signup.html')




from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

def login_view(request):
    error_message = None

    if request.method == "POST":
        role = request.POST.get('role')
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Attempt to find the user by username or email based on the input
        try:
            if '@' in username_or_email:
                # If the input contains '@', assume it's an email
                user = CustomUser.objects.get(email=username_or_email, role=role)
            else:
                # Otherwise, treat it as a username
                user = CustomUser.objects.get(username=username_or_email, role=role)

            # Check the password
            if user.check_password(password):
                login(request, user)  # Log the user in
                if role == "alumni":
                    return redirect('AlumniFrontPage')
                return redirect('home')  # Redirect to the home page
            else:
                error_message = "Invalid password. Please try again."
        except CustomUser.DoesNotExist:
            error_message = "No user found with the provided username/email and role."

    return render(request, 'login.html', {'error_message': error_message})

# ----------HOME VIEW --------------------
from .models import Book, StudyMaterial, Textbook

def home(request):
    query = request.GET.get('q', '')
    filter_by = request.GET.get('filter_by', 'textbook_name')  # Default filter_by
    books = []
    materials = []
    textbooks = []

    # Search Books
    if query:
        if filter_by == 'textbook_name':
            books = Book.objects.filter(textbook_name__icontains=query, available=True)
        elif filter_by == 'author_name':
            books = Book.objects.filter(author_name__icontains=query, available=True)
        elif filter_by == 'subject':
            books = Book.objects.filter(subject__icontains=query, available=True)
        elif filter_by == 'semester':
            books = Book.objects.filter(semester__icontains=query, available=True)
    # Search Study Materials
    if query:
        if filter_by == 'textbook_name':
            materials = StudyMaterial.objects.filter(subject__icontains=query)
        elif filter_by == 'subject':
            materials = StudyMaterial.objects.filter(subject__icontains=query)
        elif filter_by == 'semester':
            materials = StudyMaterial.objects.filter(semester__icontains=query)

# Search Textbooks
    if query:
     if filter_by == 'textbook_name':
        textbooks = Textbook.objects.filter(name__icontains=query, available=True)
     elif filter_by == 'author_name':
        textbooks = Textbook.objects.filter(author__icontains=query, available=True)
     elif filter_by == 'subject':
        textbooks = Textbook.objects.filter(subject__icontains=query, available=True)
     elif filter_by == 'semester':
        textbooks = Textbook.objects.filter(semester__icontains=query, available=True)

    # User Count
    stcians_count = CustomUser.objects.filter(role='stcians').count()
    other_students_count = CustomUser.objects.filter(role='student_other').count()
    alumni_count = CustomUser.objects.filter(role='alumni').count()
    
    users_count = stcians_count + other_students_count

    # Total Books Count (Donated + Paid + Study Materials)
    total_books = Book.objects.count() + Textbook.objects.count() + StudyMaterial.objects.count()

    return render(request, 'home.html', {
        'query': query,
        'filter_by': filter_by,
        'books': books,
        'materials': materials,
        'textbooks': textbooks,  
        'users_count': users_count,  # STCians + Other Students
        'alumni_count': alumni_count,  # Alumni count
        'total_books': total_books,  # Total books (donated + paid + study materials)
    })


# ----------Donation Dashboard VIEW --------------------

def donate_view(request):
    return render(request, 'donation_dashboard.html')  


# ----------Donate TextBook View ---------
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Book


def donate_textbook(request):
    if request.method == 'POST':
        textbook_name = request.POST.get('textbook_name')
        author_name = request.POST.get('author_name')
        subject = request.POST.get('subject')
        semester = request.POST.get('semester')
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')
        price = request.POST.get('price', 'free')
        image = request.FILES.get('image')

        if image:
            book = Book.objects.create(
                user=request.user,
                textbook_name=textbook_name,
                author_name=author_name,
                subject=subject,
                semester=semester,
                feedback=feedback,
                rating=rating,
                price=price,
                image=image
            )
            return redirect("home")
    
    return render(request, 'donate_textbook1.html')


def extract_text(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        try:
            # Open image
            img = Image.open(image)
            img = img.convert('L')  # Convert to grayscale
            
            # Enhance Image Quality
            img = img.filter(ImageFilter.SHARPEN)  # Sharpen the image
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Improve contrast
            
            # Perform OCR
            text = pytesseract.image_to_string(img, lang='eng')
            lines = text.split("\n")
            
            # Clean the text (Remove empty lines and unwanted characters)
            clean_lines = [line.strip() for line in lines if line.strip()]
            
            if clean_lines:
                return JsonResponse({"extracted_text": clean_lines})
            else:
                return JsonResponse({"error": "No text found or poor image quality!"})

        except Exception as e:
            return JsonResponse({"error": f"Failed to extract text: {str(e)}"})

    return JsonResponse({"error": "No image uploaded!"})

# ----------Book View ---------


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Book, BookRequest
from datetime import datetime, timedelta
from django.core.mail import send_mail

def get_next_working_days():
    """
    Returns the next 3 working days (Monday to Friday) as a list of strings in 'YYYY-MM-DD' format.
    """
    working_days = []
    current_date = datetime.today()
    while len(working_days) < 3:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday to Friday
            working_days.append(current_date.strftime('%Y-%m-%d'))
    return working_days

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # ❌ Restrict "Students from Other Colleges" from viewing book details
    if request.user.role == "student_other":
        messages.error(request, "You are not allowed to view this page.")
        return redirect("home")
           
    donor_name = book.user.get_full_name() if book.user else "Anonymous"
    dates = get_next_working_days()

    # Prevent the donor from requesting their own book
    if request.user == book.user:
        messages.error(request, "You cannot request a book that you have donated.")
        return redirect('home')  # Redirecting to home or another appropriate page

    if request.method == "POST":
        place = request.POST.get('place')
        time = request.POST.get('time')
        date = request.POST.get('date')

        if not place or not time or not date:
            messages.error(request, "Please fill in all fields.")
        elif date not in dates:
            messages.error(request, "Invalid date selected. Please choose a valid working day.")
        else:
            try:
                time_24_hour = datetime.strptime(time, "%I:%M %p").time()
                BookRequest.objects.create(
                    book=book,
                    receiver=request.user,
                    donor=book.user,
                    donation_place=place,
                    donation_time=time_24_hour,
                    donation_date=date,
                    status="Pending",
                )

                 # 📩 **Send Email to Donor**
                send_mail(
                    "New Book Request Received",
                    f"Hello {book.user.username},\n\n"
                    f"You have received a new request for your book:\n"
                    f"📖 Book Name: {book.textbook_name}\n"
                    f"✍️ Author: {book.author_name}\n"
                    f"📍 Requested Pickup Location: {place}\n"
                    f"📅 Date: {date}\n"
                    f"🕒 Time: {time}\n\n"
                    "Please log in to your Edubridge account to accept or reject the request.\n\n"
                    "Best regards,\nEdubridge Team",
                    settings.EMAIL_HOST_USER,
                    [book.user.email],  # Email sent to the donor
                    fail_silently=False,
                )
                messages.success(request, "Your request has been sent to the donor.")
                return redirect('book_detail', pk=pk)
            except ValueError:
                messages.error(request, "Invalid time format. Please enter the time in 'HH:MM AM/PM' format.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

    context = {
        'book': book,
        'donor_name': donor_name,
        'feedback': book.feedback,
        'rating': book.rating,
        'dates': dates,
    }
    return render(request, 'book_detail.html', context)


# ----------Notification View ---------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from .models import Textbook, SellRequest
from datetime import datetime, timedelta
from django.core.mail import send_mail

@login_required
def textbook_detail(request, textbook_id):
    textbook = get_object_or_404(Textbook, id=textbook_id)

    # Generate available dates for selection (Next 7 days)
    dates = [(now().date() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]  # Ensure correct format

    # Prevent the seller from requesting their own textbook
    if request.user == textbook.user:
        messages.warning(request, "You cannot request the textbook that you have listed for sale.")
        return redirect("home")  # Redirect to home or another appropriate page
    
    if request.method == "POST":
        place = request.POST.get("place")
        time = request.POST.get("time") or None  # Ensure time is stored properly
        date_str = request.POST.get("date")

        # Ensure all fields are selected
        if not place or not date_str:
            return render(request, "textbook_detail.html", {
                "textbook": textbook,
                "dates": dates,
                "error": "Please fill all required fields."
            })

        try:
            # Convert date to the correct format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return render(request, "textbook_detail.html", {
                "textbook": textbook,
                "dates": dates,
                "error": "Invalid date format. Please select a valid date."
            })

        # Create and save the SellRequest entry
        sell_request = SellRequest.objects.create(
            textbook=textbook,
            buyer=request.user,
            requester=request.user,  # Ensure requester is saved correctly
            place=place,
            time=time,
            date=date_obj,
            status="Pending"
        )

        # Double-check if requester is saved correctly
        if sell_request.requester != request.user:
            sell_request.requester = request.user
            sell_request.save()

         # 📩 **Send Email to Seller**
        send_mail(
            "New Sell Request Received",
            f"Hello {textbook.user.username},\n\n"
            f"You have received a new request for your textbook:\n"
            f"📚 Book Name: {textbook.name}\n"
            f"✍️ Author: {textbook.author}\n"
            f"📍 Meeting Place: {place}\n"
            f"📅 Date: {date_str}\n"
            f"🕒 Time: {time if time else 'Not specified'}\n\n"
            "Please log in to your Edubridge account to accept or reject the request.\n\n"
            "Best regards,\nEdubridge Team",
            settings.EMAIL_HOST_USER,
            [textbook.user.email],  # Email sent to the seller
            fail_silently=False,
        )
        messages.success(request, "Your request has been sent to the seller.")
        return redirect("manage_requests")  # Redirect to requests management page

    return render(request, "textbook_detail.html", {"textbook": textbook, "dates": dates})

# ----------Request View ---------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BookRequest, SellRequest, Notification, SellNotification
from django.db.models import Q
from datetime import datetime
from django.utils import timezone

@login_required
def manage_requests(request):
    user = request.user

    threshold_date = timezone.now() - timedelta(days=7)
    BookRequest.objects.filter(created_at__lt=threshold_date).delete()
    SellRequest.objects.filter(created_at__lt=threshold_date).delete()

    # Get pending book donation and selling requests (where the user is the donor/seller)
    donation_requests = BookRequest.objects.filter(book__user=user, status="Pending")
    sell_requests = SellRequest.objects.filter(textbook__user=user, status="Pending")

    # Get requests sent by the user
    sent_requests = BookRequest.objects.filter(receiver=user).exclude(book__user=user)
    sent_sell_requests = SellRequest.objects.filter(buyer=user, status="Pending")

    # Get accepted notifications (latest on top)
    notifications = Notification.objects.filter(Q(donor=user) | Q(receiver=user), status="Accepted").order_by('-created_at')
    sell_notifications = SellNotification.objects.filter(Q(seller=user) | Q(buyer=user), status="Accepted").order_by('-created_at')

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        sell_request_id = request.POST.get("sell_request_id")
        action = request.POST.get("action")
        sell_action = request.POST.get("sell_action")


        
        # Handling book donation requests
        if request_id:
            book_request = get_object_or_404(BookRequest, id=request_id)

            if action == "accept":
                book_request.status = "Accepted"
                book_request.save()
                
                
                # Create notification for receiver
                Notification.objects.create(
                    donor=book_request.book.user,
                    receiver=book_request.receiver,
                    book=book_request.book,
                    donation_date=book_request.donation_date,
                    donation_time=book_request.donation_time,
                    donation_place=book_request.donation_place,
                    status="Accepted",
                )
                book = book_request.book
                book.available = False
                book.save()

                messages.success(request, "Book donation request accepted successfully!")

            elif action == "reject":
                book_request.status = "Rejected"
                book_request.save()

                # Notify receiver
                Notification.objects.create(
                    donor=book_request.book.user,
                    receiver=book_request.receiver,
                    book=book_request.book,
                    status="Rejected"
                )

                messages.warning(request, "Book donation request rejected.")

        # Handling selling requests
        elif sell_request_id:
            sell_request = get_object_or_404(SellRequest, id=sell_request_id)

            # Convert time format if necessary
            formatted_time = None
            if sell_request.time:
                try:
                    formatted_time = datetime.strptime(sell_request.time, "%I:%M %p").time()  # Convert AM/PM to 24-hour format
                except ValueError:
                    formatted_time = sell_request.time  # If already in correct format, use it as is

            if sell_action == "accept":
                sell_request.status = "Accepted"
                sell_request.save()

                # Create SellNotification with requester field
                SellNotification.objects.create(
                    seller=sell_request.textbook.user,  # Seller
                    buyer=sell_request.buyer,  # Buyer
                    requester=request.user,  # Requester added
                    sell_request=sell_request,
                    meeting_date=sell_request.date,  # Delivery Date
                    meeting_time=formatted_time,  # Use the correctly formatted time
                    meeting_place=sell_request.place,  # Delivery Place
                    status="Accepted",
                )

                # Mark textbook as unavailable
                textbook = sell_request.textbook
                textbook.available = False
                textbook.save()

                messages.success(request, "Selling request has been accepted. Buyer has been notified.")

            elif sell_action == "reject":
                sell_request.status = "Rejected"
                sell_request.save()

                # Notify buyer using SellNotification with requester field
                SellNotification.objects.create(
                    seller=sell_request.textbook.user,
                    buyer=sell_request.buyer,
                    requester=request.user,  # Requester added
                    sell_request=sell_request,
                    status="Rejected"
                )

                messages.warning(request, "Selling request has been rejected.")

        return redirect("manage_requests")

    return render(request, "manage_requests.html", {
        "donation_requests": donation_requests,
        "sell_requests": sell_requests,
        "sent_requests": sent_requests,
        "sent_sell_requests": sent_sell_requests,
        "notifications": notifications,
        "sell_notifications": sell_notifications,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BookRequest, SellRequest, Notification, SellNotification
from datetime import datetime

@login_required
def accept_request(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        sell_request_id = request.POST.get("sell_request_id")

        # Accepting a book donation request
        if request_id:
            book_request = get_object_or_404(BookRequest, id=request_id)

            # Update request status
            book_request.status = "Accepted"
            book_request.save()

            # Ensure time format consistency
            donation_time = book_request.donation_time if book_request.donation_time else None

            # Create a Notification with all request details
            Notification.objects.create(
                donor=book_request.book.user,
                receiver=book_request.receiver,
                book=book_request.book,
                donation_date=book_request.donation_date,
                donation_time=donation_time,
                donation_place=book_request.donation_place,
                status="Accepted",
            )

            messages.success(request, "Book donation request has been accepted.")
        
        # Accepting a selling request
        elif sell_request_id:
            sell_request = get_object_or_404(SellRequest, id=sell_request_id)

            # Update request status
            sell_request.status = "Accepted"
            sell_request.save()

            # Ensure meeting_time is formatted correctly
            formatted_time = None
            if sell_request.time:
                try:
                    formatted_time = datetime.strptime(sell_request.time, "%I:%M %p").time()
                except ValueError:
                    formatted_time = sell_request.time  # Use as-is if already formatted correctly

            # Create a SellNotification
            SellNotification.objects.create(
                seller=sell_request.textbook.user,
                buyer=sell_request.buyer,
                requester=request.user,  # Use request.user instead of sell_request.requester
                sell_request=sell_request,
                meeting_date=sell_request.date,
                meeting_time=formatted_time,
                meeting_place=sell_request.place,
                status="Accepted",
            )

            messages.success(request, "Selling request has been accepted. Buyer has been notified.")

        return redirect("manage_requests")

# ----------Userdashborad View ---------

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Textbook, Book  # Import your models

@login_required
def dashboard(request):
    # Fetch the logged-in user
    user = request.user

    # Fetch donated books uploaded by the user
    donated_books = Book.objects.filter(user=user)

    # Fetch paid books purchased by the user
    paid_books = Textbook.objects.filter(user=user)

    # Pass the data to the template
    context = {
        'user': user,
        'donated_books': donated_books,
        'paid_books': paid_books,
    }

    return render(request, 'dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import Book


def delete_book(request, book_id):
    # Get the book to be deleted
    book = get_object_or_404(Book, id=book_id, user=request.user)
    
    # Delete the book
    book.delete()
    
    # Redirect back to the dashboard
    return redirect('user_dashboard')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Textbook, Book

@login_required
def delete_paid_book(request, book_id):
    # Get the book purchased by the user
    book = get_object_or_404(Textbook, id=book_id, user=request.user)
    
    # Delete the book
    book.delete()
    
    # Redirect back to the dashboard
    return redirect('user_dashboard')

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book
from django.contrib import messages

@login_required
def enable_availability(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    book.available = True
    book.save()
    messages.success(request, "Book availability has been updated!")
    return redirect("user_dashboard")  # Change to your actual dashboard URL name



# ----------SM detail View ---------

from django.shortcuts import render, get_object_or_404
from .models import StudyMaterial

def study_material_detail(request, material_id):
    # Fetch the specific study material by its ID or return a 404 error if not found
    material = get_object_or_404(StudyMaterial, pk=material_id)
    
    # Fetch uploader name if you have an uploader field (if it's a ForeignKey to User, for example)
    uploader_name = material.uploader.username if hasattr(material, 'uploader') and material.uploader else "Unknown"  # Modify based on your actual model structure

    context = {
        'material': material,
        'uploader_name': uploader_name,
    }
    return render(request, 'study_material_detail.html', context)



# ----------Donate SM View ---------

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import StudyMaterial
from django.core.exceptions import ValidationError

def donate_study_material(request):
    if request.method == 'POST':
        # Handle form submission
        subject = request.POST.get('subject')
        module = request.POST.get('module')
        semester = request.POST.get('semester')
        description = request.POST.get('description')  # New field
        file = request.FILES.get('file')

        # Validate that all required fields are provided
        if not subject or not module or not semester or not description or not file:
            return HttpResponse("All fields are required.", status=400)

        # Validate that semester is a valid number (1-8)
        try:
            semester = int(semester)
            if semester < 1 or semester > 8:
                return HttpResponse("Semester must be between 1 and 8.", status=400)
        except ValueError:
            return HttpResponse("Semester must be a valid number.", status=400)

        # Check if file is of an allowed type
        allowed_file_types = ['.pdf', '.ppt', '.pptx', '.docx', '.txt']
        if not any(file.name.endswith(ext) for ext in allowed_file_types):
            return HttpResponse(f"Invalid file type. Only the following types are allowed: {', '.join(allowed_file_types)}.", status=400)

        # Save the study material
        try:
            study_material = StudyMaterial(
                subject=subject,
                module=module,
                semester=semester,
                description=description,  # Save description
                file=file
            )
            study_material.save()
            return redirect("home")  # Redirect to the home page after successful donation
        except ValidationError as e:
            return HttpResponse(f"Error: {e}", status=400)

    # Render the form
    return render(request, 'donate_study_material.html')


import pytesseract
from PIL import Image
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Textbook

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text.strip()
    except Exception as e:
        return f"OCR Error: {e}"

@login_required
def sell_books(request):
    extracted_text = ""
    if request.method == "POST":
        textbook_name = request.POST.get("textbook_name", "").strip()
        author_name = request.POST.get("author_name", "").strip()
        subject = request.POST.get("subject", "").strip()
        semester = request.POST.get("semester", "").strip()
        price = request.POST.get("price", "").strip()
        feedback = request.POST.get("feedback", "").strip()
        rating = request.POST.get("rating", "").strip()
        image = request.FILES.get("image")

        if image:
            temp_image_path = default_storage.save("temp/" + image.name, image)
            extracted_text = extract_text_from_image(default_storage.path(temp_image_path))
            default_storage.delete(temp_image_path)  # Cleanup temp file

        if not (textbook_name and author_name and subject and semester and price):
            messages.error(request, "All fields except feedback and rating are required.")
            return render(request, "sell_book.html", {"extracted_text": extracted_text})

        try:
            semester = int(semester)
            if semester not in range(1, 9):
                raise ValueError("Invalid semester value.")

            price = Decimal(price)
            if price < 0:
                raise ValueError("Price must be a positive number.")

            rating = int(rating) if rating else None
            if rating and rating not in range(1, 6):
                raise ValueError("Rating must be between 1 and 5.")

            # Save textbook
            Textbook.objects.create(
                name=textbook_name,
                author=author_name,
                subject=subject,
                semester=semester,
                price=price,
                feedback=feedback,
                rating=rating,
                image=image,
                user=request.user
            )
            messages.success(request, "Your textbook has been successfully added!")
            return redirect("home")

        except ValueError as e:
            messages.error(request, f"Invalid input: {e}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, "sell_book.html", {"extracted_text": extracted_text})


from django.shortcuts import render
from .models import Book, StudyMaterial, Textbook
from collections import defaultdict

def available_books(request):
    query = request.GET.get('q', '')
    filter_by = request.GET.get('filter_by', 'textbook_name')  # Default filter

    # Fetch books
    donated_books = Book.objects.filter(available=True)  # Get all books
    paid_books = Textbook.objects.filter(available=True)  # Get all paid books
    pdf_books = StudyMaterial.objects.all()  # Get all study materials

    # Apply search filters if query exists
    if query:
        if filter_by == 'textbook_name':
            donated_books = donated_books.filter(textbook_name__icontains=query)
            paid_books = paid_books.filter(name__icontains=query)
            pdf_books = pdf_books.filter(subject__icontains=query)
        elif filter_by == 'author_name':
            donated_books = donated_books.filter(author_name__icontains=query)
            paid_books = paid_books.filter(author__icontains=query)
        elif filter_by == 'subject':
            donated_books = donated_books.filter(subject__icontains=query)
            paid_books = paid_books.filter(subject__icontains=query)
            pdf_books = pdf_books.filter(subject__icontains=query)
        elif filter_by == 'semester':
            donated_books = donated_books.filter(semester__icontains=query)
            paid_books = paid_books.filter(semester__icontains=query)
            pdf_books = pdf_books.filter(semester__icontains=query)

    # Group books by subject
    grouped_donated_books = defaultdict(list)
    grouped_paid_books = defaultdict(list)
    grouped_pdf_books = defaultdict(list)

    for book in donated_books:
        grouped_donated_books[book.subject].append(book)


    for book in paid_books:
        grouped_paid_books[book.subject].append(book)

    for pdf in pdf_books:
        grouped_pdf_books[pdf.subject].append(pdf)

    context = {
        'query': query,
        'filter_by': filter_by,
        'grouped_donated_books': dict(grouped_donated_books),
        'grouped_paid_books': dict(grouped_paid_books),
        'grouped_pdf_books': dict(grouped_pdf_books),
    }

    return render(request, 'available_books.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def alumni_front_page(request):
     # User Count
    stcians_count = CustomUser.objects.filter(role='stcians').count()
    other_students_count = CustomUser.objects.filter(role='student_other').count()
    alumni_count = CustomUser.objects.filter(role='alumni').count()
    
    users_count = stcians_count + other_students_count

    # Total Books Count (Donated + Paid + Study Materials)
    total_books = Book.objects.count() + Textbook.objects.count() + StudyMaterial.objects.count()

    return render(request, 'alumni_front_page.html',{  
        'users_count': users_count,  # STCians + Other Students
        'alumni_count': alumni_count,  # Alumni count
        'total_books': total_books,  # Total books (donated + paid + study materials)
    })



def alumni_chat_view(request):
    return render(request, 'home.html')  # Replace 'home.html' with your actual template


def receive_view(request):
    return render(request, 'home.html')  # Replace 'home.html' with your actual template



#----------------------audio--------------------#
import os
import speech_recognition as sr
from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from fpdf import FPDF

class PDF(FPDF):


    def footer(self):
        """Optional: Add a footer with page number."""
        self.set_y(-15)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

import os
import speech_recognition as sr
from django.shortcuts import render
from django.conf import settings
from .models import AudioNote
from django.contrib.auth.decorators import login_required

def format_text(raw_text):
    """Formats text with basic rules (you can extend this)."""
    formatted_text = raw_text.replace(" heading ", "\n\n**").replace(" stop ", ".\n\n")
    return formatted_text

@login_required
def upload_audio(request):
    transcribed_text = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        subject = request.POST.get("subject", "").strip()
        semester = request.POST.get("semester", "").strip()
        audio_file = request.FILES.get("audio_file")

        if not (title and subject and semester and audio_file):
            return render(request, "upload_audio.html", {"error": "All fields are required."})

        # Save the uploaded file to media/audio/
        audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        file_path = os.path.join(audio_dir, audio_file.name)

        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Process the audio file with speech recognition
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(file_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = recognizer.record(source)

                # Transcribe audio
                raw_text = recognizer.recognize_google(audio_data, language="en-US")

                # Apply formatting rules
                transcribed_text = format_text(raw_text)

                # Save to AudioNote model
                AudioNote.objects.create(
                    user=request.user,
                    title=title,
                    subject=subject,
                    semester=int(semester),
                    audio_file=f"audio/{audio_file.name}",  
                )

        except sr.UnknownValueError:
            transcribed_text = "Could not understand the audio. Please try speaking more clearly."
        except sr.RequestError as e:
            transcribed_text = f"Error with the speech recognition service: {e}"

    return render(request, "upload_audio.html", {"transcribed_text": transcribed_text})


import re

def format_text(text):
    """
    Convert spoken keywords into formatted text.
    - 'title' → Bold heading (Markdown-style ##, ALL CAPS)
    - 'subtitle' → Bold + Italic subheading (text)
    - 'paragraph' → Starts a new paragraph (first letter capitalized)
    - 'newline' → Moves to a new line
    - 'bullet' → Converts text into a bulleted list
    - 'number' → Converts text into a numbered list
    - 'bold' → Makes the next words bold
    - 'italic' → Makes the next words italic
    - 'quote' → Formats text as a quote block
    - 'table start' / 'table end' → Marks table sections
    """
    words = text.split()
    formatted_text = []
    is_title = False
    is_subtitle = False
    is_bold = False
    is_italic = False
    is_bullet = False
    is_number = False
    is_quote = False
    is_table = False
    table_data = []
    num_count = 1  # Counter for numbered lists

    i = 0
    while i < len(words):
        word = words[i].lower()

        if word in ["heading", "title"]:  # Treat both as headings
            formatted_text.append("\n## ")  # Markdown-style heading
            is_title = True
        elif word == "sub":
            is_subtitle = True
        elif word == "paragraph":
            formatted_text.append("\n\n")  # New paragraph
            is_title = False
        elif word == "newline":
            formatted_text.append("\n")  # Line break
        elif word == "bullet":
            is_bullet = True
        elif word == "numbered":
            is_number = True
        elif word == "bold":
            is_bold = True
        elif word == "italic":
            is_italic = True
        elif word == "quote":
            formatted_text.append("\n> ")  # Quote block
            is_quote = True
        elif word == "table" and i + 1 < len(words) and words[i + 1].lower() == "start":
            formatted_text.append("\n| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|")
            is_table = True
            i += 1  # Skip 'start'
        elif word == "table" and i + 1 < len(words) and words[i + 1].lower() == "end":
            formatted_text.append("\n".join(table_data))  # Append collected table rows
            table_data = []
            is_table = False
            i += 1  # Skip 'end'
        else:
            # Apply formatting to normal words
            formatted_word = words[i]

            if is_title:
                formatted_word = formatted_word.upper()  # Convert title text to uppercase
            if is_subtitle:
                formatted_word = f"\n\n### **{formatted_word}"  # Proper formatting for subtitle
                formatted_text.append(formatted_word)  # Append subtitle separately
                is_subtitle = False
                i += 1
                continue  # Move to the next word

            if is_bold:
                formatted_word = f"{formatted_word}"
            if is_italic:
                formatted_word = f"{formatted_word}"
            if is_quote:
                formatted_word = f"{formatted_word}"  # Quotes stay normal
            if is_bullet:
                formatted_word = f"\n-> {formatted_word}"
                is_bullet = False
            if is_number:
                formatted_word = f"\n{num_count}. {formatted_word}"
                num_count += 1
                is_number = False
            if is_table:
                table_data.append(f"| {formatted_word} |  |  |")  # Placeholder table row
                continue  # Skip normal formatting for table rows

            formatted_text.append(formatted_word)

            # Reset single-use flags
            is_title = False
            is_subtitle = False
            is_bold = False
            is_italic = False

        i += 1

    # Capitalize the first letter of each paragraph
    formatted_output = " ".join(formatted_text).strip()
    paragraphs = formatted_output.split("\n\n")
    formatted_paragraphs = [p[0].upper() + p[1:] if p else p for p in paragraphs]
    
    return "\n\n".join(formatted_paragraphs)
import os
import re
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Edubridge Audio Notes", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, title.upper(), ln=True, align="C")  # Convert to uppercase
        self.ln(5)

    def chapter_subtitle(self, subtitle):
        self.set_font("Arial", "I", 14)
        self.cell(0, 8, subtitle, ln=True, align="L")
        self.ln(3)

    def add_paragraph(self, text):
        self.set_font("Arial", "", 12)
        formatted_text = text.capitalize()  # Ensure the first letter is capitalized
        self.multi_cell(0, 8, formatted_text.encode("latin-1", "replace").decode("latin-1"))
        self.ln(5)

    def add_bullet(self, text):
        self.set_font("Arial", "", 12)
        self.cell(10)
        self.cell(0, 8, f"-> {text}", ln=True, align="L")

    def add_numbered(self, text):  # Updated function name
        self.set_font("Arial", "", 12)
        self.cell(10)
        self.cell(0, 8, text, ln=True, align="L")

    def add_quote(self, text):
        self.set_font("Arial", "I", 12)
        self.cell(10)
        self.multi_cell(0, 8, text.encode("latin-1", "replace").decode("latin-1"), border=1)
        self.ln(3)

    def add_table(self, rows):
        self.set_font("Arial", "", 12)
        for row in rows:
            columns = row.split("|")[1:-1]
            for col in columns:
                self.cell(60, 8, col.strip(), border=1, align="C")
            self.ln(8)

import os
import re
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from fpdf import FPDF

def convert_to_pdf(request):
    if request.method == "POST":
        formatted_text = request.POST.get("formatted_text", "")

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        lines = formatted_text.split("\n")
        table_rows = []
        is_table = False

        for line in lines:
            line = line.strip()

            # Handling Title (## HEADING)
            if line.startswith("## "):
                pdf.chapter_title(line.replace("## ", "").strip())

           # Handling Subtitle (SUBTITLE** or **SUBTITLE)
            elif (line.startswith("") and line.endswith("")) or (line.startswith("") and line.endswith("")):
             subtitle_text = line.replace("", "").replace("", "").replace("*", "").strip()
             pdf.chapter_subtitle(subtitle_text)


            # Handling Bullet Points (-> Item)
            elif line.startswith("-> "):
                pdf.add_bullet(line.replace("-> ", "").strip())

            # Handling Numbered List (1. Item)
            elif re.match(r"^\d+\.", line):
                pdf.add_numbered(line.strip())

            # Handling Quotes (> Quoted Text)
            elif line.startswith("> "):
                pdf.add_quote(line.replace("> ", "").strip())

            # Handling Table Rows (| Column1 | Column2 | Column3 |)
            elif line.startswith("|"):
                if not is_table:
                    pdf.ln(5)  # Add space before the table
                    is_table = True
                table_rows.append(line)

            # Regular Paragraphs
            else:
                if is_table:
                    pdf.add_table(table_rows)
                    table_rows = []
                    is_table = False
                pdf.add_paragraph(line.capitalize())  # Capitalize first letter of paragraph

        # Save PDF
        pdf_dir = os.path.join(settings.MEDIA_ROOT, "pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, "transcribed_text.pdf")
        pdf.output(pdf_path)

        return FileResponse(open(pdf_path, "rb"), as_attachment=True, content_type="application/pdf")

    return render(request, "upload_audio.html")