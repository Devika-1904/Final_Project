from django.urls import path
from .views import signup_view, login_view
from django.conf import settings
from django.conf.urls.static import static
from .views import study_material_detail

from . import views 


urlpatterns = [
    path('signup/', signup_view, name='signup_view'),
    path('', login_view, name='login_view'),
    path('alumni/', views.alumni_front_page, name='AlumniFrontPage'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path("textbook/<int:textbook_id>/", views.textbook_detail, name="textbook_detail"),
    path('home/', views.home, name='home'),
    path('enable-availability/<int:book_id>/', views.enable_availability, name='enable_availability'),
    path('donate/', views.donate_view, name='Donate'),
    path('material/<int:material_id>/', study_material_detail, name='study_material_detail'),
    path('donate_study_material/', views.donate_study_material, name='donate_study_material'),
    path('delete-paid-book/<int:book_id>/', views.delete_paid_book, name='delete_paid_book'),
    path('receive/', views.receive_view, name='receive'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('dashboard/', views.dashboard, name='user_dashboard'),
    path('audio/', views.alumni_chat_view, name='alumini'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('donate/textbook', views.donate_textbook, name='donate_textbook'),
    path('extract_text/', views.extract_text, name='extract_text'),
    # path('donate/textbook/', views.donate_textbook, name='donate_textbook'),
    path('available-books/', views.available_books, name='available_books'),
    
    path('sell_books/', views.sell_books, name='sell_books'),
    path("upload_audio/", views.upload_audio, name="upload_audio"),
    path("convert_to_pdf/", views.convert_to_pdf, name="convert_to_pdf"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)