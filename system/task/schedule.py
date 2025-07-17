from celery import shared_task
from django.utils import timezone
from datetime import timedelta, date
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import ScheduleEvent

@shared_task
def send_upcoming_event_reminders():
    now = timezone.now()
    window = now + timedelta(minutes=5)

    events = ScheduleEvent.objects.filter(has_reminder=True)

    for event in events:
        if not event.reminder_time_value:
            continue

        # Compute reminder delta
        delta = timedelta()
        if event.reminder_time_unit == 'minutes':
            delta = timedelta(minutes=event.reminder_time_value)
        elif event.reminder_time_unit == 'hours':
            delta = timedelta(hours=event.reminder_time_value)
        elif event.reminder_time_unit == 'days':
            delta = timedelta(days=event.reminder_time_value)

        # Expand occurrences
        occurrences = expand_occurrences(event, now, window)

        for occ_time in occurrences:
            reminder_time = occ_time - delta

            if now <= reminder_time <= window:
                recipient = event.reminder_email or event.user.email

                subject = f"🔔 Nhắc sự kiện: {event.title}"
                html_content = render_to_string('mails/event_reminder.html', {
                    'title': event.title,
                    'start_datetime': occ_time.strftime('%Y-%m-%d %H:%M'),
                    'end_datetime': event.end_datetime.strftime('%Y-%m-%d %H:%M') if event.end_datetime else '',
                    'description': event.description,
                    'location': event.location,
                })

                email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [recipient])
                email.content_subtype = "html"
                email.send()



def expand_occurrences(event, range_start, range_end):
    occurrences = []

    # Base values
    dt = event.start_datetime
    end = event.repeat_until or range_end

    # One-time event
    if event.frequency == 'none':
        if range_start <= dt <= range_end:
            occurrences.append(dt)
        return occurrences

    # Recurring event
    while dt <= end:
        if dt >= range_start and dt <= range_end:
            if event.frequency == 'daily':
                occurrences.append(dt)
            elif event.frequency == 'weekly':
                weekday = dt.strftime('%a').lower()[:3]
                if weekday in (event.repeat_on_weekdays or []):
                    occurrences.append(dt)
            elif event.frequency == 'monthly':
                if dt.day == event.start_datetime.day:
                    occurrences.append(dt)

        # Advance
        if event.frequency == 'daily':
            dt += timedelta(days=1)
        elif event.frequency == 'weekly':
            dt += timedelta(days=1)
        elif event.frequency == 'monthly':
            try:
                # crude but safe monthly increment
                month = dt.month + 1 if dt.month < 12 else 1
                year = dt.year + 1 if month == 1 else dt.year
                dt = dt.replace(year=year, month=month)
            except ValueError:
                break

    return occurrences