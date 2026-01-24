from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate, login
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django.shortcuts import redirect
from .models import (
    User,
    DoctorProfile,
    AvailabilitySlot,
    Booking
)

# ---------------- HOME ----------------
def home(request):
    return render(request, "core/home.html")


def after_login_redirect(request):
    if request.user.role == "doctor":
        return redirect("doctor_dashboard")
    return redirect("patient_dashboard")


User = get_user_model()

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return after_login_redirect(request) 
    else:
        form = CustomUserCreationForm()
    return render(request, "core/register.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = "core/login.html"

    def form_valid(self, form):
        """Called when the form is valid"""
        user = form.get_user()
        role = self.request.POST.get("role", "").lower()  # get role from form

        # Check if user role matches selected role
        if user.role != role:
            form.add_error(None, "Selected role does not match your account.")
            return self.form_invalid(form)

        login(self.request, user)  # login the user

        # Redirect to respective dashboard
        if user.role == "doctor":
            return redirect("doctor_dashboard")
        return redirect("patient_dashboard")
# ---------------- PATIENT VIEWS ----------------

from django.utils import timezone
from django.shortcuts import render
from .models import DoctorProfile, AvailabilitySlot

# ---------------- PATIENT VIEWS ----------------
@login_required
def patient_dashboard(request):
    """
    Shows all doctors to patient with their available slots
    """
    if request.user.role != "patient":
        return HttpResponseForbidden("Patients only")

    today = timezone.now().date()
    doctors = DoctorProfile.objects.select_related("user")

    # attach available slots to each doctor
    for doctor in doctors:
        doctor.available_slots = AvailabilitySlot.objects.filter(
            doctor=doctor.user,
            is_booked=False,
            date__gte=today
        ).order_by("date", "start_time")

    return render(request, "core/patient_dashboard.html", {
        "doctors": doctors
    })


@login_required
def doctor_slots(request, doctor_id):
    """
    Patient sees available slots for a doctor
    (future + not booked)
    """
    if request.user.role != "patient":
        return HttpResponseForbidden("Patients only")

    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    slots = AvailabilitySlot.objects.filter(
        doctor=doctor.user,
        is_booked=False,
        date__gte=timezone.now().date()
    ).order_by("date", "start_time")

    return render(request, "core/doctor_slots.html", {
        "doctor": doctor,
        "slots": slots
    })

from django.contrib import messages
from django.db import IntegrityError

@login_required
@transaction.atomic
def book_and_notify(request, slot_id):
    print("BOOK VIEW HIT")
    if request.user.role != "patient":
        return HttpResponseForbidden("Patients only")

    slot = get_object_or_404(
        AvailabilitySlot.objects.select_for_update(),
        id=slot_id
    )

    # Double safety check
    if slot.is_booked:
        messages.error(request, "This slot is already booked.")
        return redirect("patient_dashboard")

    try:
        Booking.objects.create(
            doctor=slot.doctor,
            patient=request.user,
            slot=slot
        )
        slot.is_booked = True
        slot.save()

    except IntegrityError:
        # Handles DB-level duplicate booking
        messages.error(request, "This slot was just booked by someone else.")
        return redirect("patient_dashboard")

    messages.success(request, "Appointment booked successfully!")
    return redirect("patient_dashboard")



# ---------------- DOCTOR VIEWS ----------------

@login_required
def doctor_dashboard(request):
    """
    Doctor sees their own slots
    """
    if request.user.role != "doctor":
        return HttpResponseForbidden("Doctors only")

    slots = AvailabilitySlot.objects.filter(
        doctor=request.user
    ).order_by("date", "start_time")

    return render(request, "core/doctor_dashboard.html", {
        "slots": slots
    })


@login_required
def add_slot(request):
    """
    Doctor creates availability slot
    """
    if request.user.role != "doctor":
        return HttpResponseForbidden("Doctors only")

    if request.method == "POST":
        AvailabilitySlot.objects.create(
            doctor=request.user,
            date=request.POST["date"],
            start_time=request.POST["start_time"],
            end_time=request.POST["end_time"]
        )
        return redirect("doctor_dashboard")

    return render(request, "core/add_slot.html")


@login_required
def delete_slot(request, slot_id):
    """
    Doctor deletes their own slot (only if not booked)
    """
    if request.user.role != "doctor":
        return HttpResponseForbidden("Doctors only")

    slot = get_object_or_404(
        AvailabilitySlot,
        id=slot_id,
        doctor=request.user
    )

    if slot.is_booked:
        return HttpResponseForbidden("Cannot delete booked slot")

    slot.delete()
    return redirect("doctor_dashboard")
