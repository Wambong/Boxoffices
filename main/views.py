from django.shortcuts import render
from accounts.models import *
from django.http import HttpResponseRedirect
from django.views.generic import View, CreateView, FormView, ListView
from datetime import date, datetime
from django.contrib import messages
# Create your views here.

#qr code
import qrcode
from django.shortcuts import render, redirect
from io import BytesIO
from django.http import HttpResponse
from PIL import Image
from django.urls import reverse
import base64

#dowload
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader



def index(request):
    movies = Movie.objects.all()
    context = {
        'mov': movies
    }
    return render(request,"index.html", context)

def movies(request, id):
    #cin = Cinema.objects.filter(shows__movie=id).distinct()
    movies = Movie.objects.get(movie=id)
    cin = Cinema.objects.filter(cinema_show__movie=movies).prefetch_related('cinema_show').distinct()  # get all cinema
    show = Shows.objects.filter(movie=id)
    context = {
        'movies':movies,
        'show':show,
        'cin':cin,
    }
    return render(request, "movies.html", context )

def seat(request, id):
    show = Shows.objects.get(shows=id)
    seat = Bookings.objects.filter(shows=id)
    return render(request,"seat.html", {'show':show, 'seat':seat})


def booked(request):
    if request.method == 'POST':
        user = request.user
        seat = ','.join(request.POST.getlist('check'))
        show = request.POST['show']


        # Save the date to the database using your model
        book = Bookings(useat=seat, shows_id=show, user=user)
        book.save()
        messages.success(request, "Ticket booked successfully")
        return render(request, "booked.html", {'book': book})
    else:
        return render(request, "booked.html")


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img_buffer = BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(img_buffer, format="PNG")

    return img_buffer.getvalue()


def ticket(request, id):
    ticket = Bookings.objects.get(id=id)
    qr_data = f"Ticket ID: {ticket.id}\nUser: {ticket.user.username}\nSeats: {ticket.useat}"
    qr_code_image_bytes = generate_qr_code(qr_data)
    qr_code_image_base64 = base64.b64encode(qr_code_image_bytes).decode('utf-8')
    context = {
        'ticket': ticket,
        'qr_code_image_base64': qr_code_image_base64,
    }
    return render(request, "ticket.html", context)

def download_ticket(request, id):
    ticket = Bookings.objects.get(id=id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'

    qr_data = f"Ticket ID: {ticket.id}\nUser: {ticket.user.username}\nSeats: {ticket.useat}"
    qr_code_image_bytes = generate_qr_code(qr_data)
    qr_code_image_base64 = base64.b64encode(qr_code_image_bytes).decode('utf-8')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))

    # Background color for the title row
    p.setFillColorRGB(0.53, 0.81, 0.98)
    p.rect(0, 520, 1000, 60, fill=True)

    # Ticket content
    p.setFont("Helvetica", 12)
    p.drawString(20, 300, "BoxOffice")
    p.drawString(400, 570, f"{ticket.shows.movie.movie_name}")
    p.drawString(400, 550, f"({ticket.shows.cinema.cinema_name})")

    # Convert base64 to bytes
    qr_code_image_data = base64.b64decode(qr_code_image_base64)
    # Draw QR code
    p.drawImage(ImageReader(BytesIO(qr_code_image_data)), 20, 350, width=150, height=150)

    # Ticket details
    p.drawString(200, 420, f"Booking ID: {ticket.pk}")
    p.drawString(200, 400, f"User: {ticket.user.username}")
    p.drawString(200, 380, f"Date: {ticket.shows.date}")
    p.drawString(200, 360, f"Price: ₽{ticket.shows.price}")
    p.drawString(400, 420, f"Seats: {ticket.useat}")
    p.drawString(400, 400, f"Time: {ticket.shows.time}")
    p.drawString(400, 380, f"Hall: H1")

    # Cinema information
    cinema_info = f"{ticket.shows.cinema.cinema_name}: {ticket.shows.cinema.address}"
    p.drawString(20, 320, cinema_info)

    p.showPage()
    p.save()

    buffer.seek(0)
    response.write(buffer.read())
    buffer.close()

    return response

class SearchView(ListView):
    model = Movie
    template_name = 'search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        query = request.GET.get('q')
        movie_list = Movie.objects.filter(
            Q(movie_name__icontains=query) |
            Q(movie_rdate__icontains=query) |
            Q(movie_des__icontains=query) |
            Q(movie_genre__icontains=query)
        )
        return movie_list

