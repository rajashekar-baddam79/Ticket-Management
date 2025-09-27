import datetime
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Ticket, CustomUser

@shared_task
def check_for_escalations(ticket_id=None):
    now = datetime.datetime.now(datetime.timezone.utc)

    if ticket_id is not None:
        # Manual escalation for a specific ticket
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
            ticket.status = 'ESCALATED'
            ticket.save()

            admin_users = CustomUser.objects.filter(role='admin')
            admin_emails = [user.email for user in admin_users]

            email_subject = f"Urgent: Ticket #{ticket.id} - '{ticket.title}' has been escalated!"
            email_message = (
                f"Dear {ticket.created_by.username},\n\n"
                f"Your ticket titled '{ticket.title}' has been escalated manually by an admin.\n\n"
                f"Ticket ID: {ticket.id}\n"
                f"Priority: {ticket.priority}\n"
                f"Current Status: Escalated\n\n"
                "An administrator has been notified.\n\n"
                "Best regards,\n"
                "The Helpdesk Team"
            )

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails + [ticket.created_by.email],
                fail_silently=False,
            )
            print(f"Manual escalation email sent for Ticket #{ticket.id}")

        except Ticket.DoesNotExist:
            print(f"Ticket id {ticket_id} does not exist")

    else:
        # Periodic escalation task (existing logic)
        escalation_times = {
            'HIGH': 1,
            'MEDIUM': 4,
            'LOW': 24,
        }

        tickets_to_escalate = []

        for priority, hours in escalation_times.items():
            time_threshold = now - datetime.timedelta(hours=hours)
            tickets = Ticket.objects.filter(
                priority=priority,
                status__in=['OPEN', 'IN_PROGRESS'],
                updated_at__lt=time_threshold
            )
            tickets_to_escalate.extend(tickets)

        for ticket in tickets_to_escalate:
            ticket.status = 'ESCALATED'
            ticket.save()

            admin_users = CustomUser.objects.filter(role='admin')
            admin_emails = [user.email for user in admin_users]

            email_subject = f"Urgent: Ticket #{ticket.id} - '{ticket.title}' has been escalated!"
            email_message = (
                f"Dear {ticket.created_by.username},\n\n"
                f"Your ticket with the title '{ticket.title}' has not been resolved "
                f"within the expected timeframe and has been escalated.\n\n"
                f"Ticket ID: {ticket.id}\n"
                f"Priority: {ticket.priority}\n"
                f"Current Status: Escalated\n\n"
                "An administrator has been notified.\n\n"
                "Best regards,\n"
                "The Helpdesk Team"
            )

            try:
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails + [ticket.created_by.email],
                    fail_silently=False,
                )
                print(f"Escalation email sent for Ticket #{ticket.id}")
            except Exception as e:
                print(f"Failed to send email for Ticket #{ticket.id}: {e}")
