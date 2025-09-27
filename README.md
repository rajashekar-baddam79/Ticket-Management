Ticket Management System

A Django and Celery based web application for managing tickets with role-based access (User, Agent, Admin), ticket escalations, and alerts.

Features

- User authentication and role-based permissions
- Ticket creation, update, and assignment
- Agents can manage their assigned tickets and update ticket status
- Automatic escalation of tickets not updated/resolved within priority-based timeframes
- Email alerts to admins and ticket creators on escalation
- REST API with Swagger documentation
- Search and filtering on tickets and users

Installation

Prerequisites

- Python 3.10+
- Redis server (for Celery broker and backend)
- Celery worker and beat for task scheduling

Setup

git clone https://github.com/yourusername/your-repo.git
cd your-repo
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Start Redis server (docker run -d -p 6379:6379 redis)

Start Celery worker:
celery -A TicketSystem worker -l info

Start Celery beat (for periodic tasks):
celery -A TicketSystem beat -l info

Usage

- Access API documentation at /swagger/
- Use API endpoints for ticket management, searching, and escalations
- Escalations run automatically based on configured schedules

Contributing

Contributions welcome! Please open issues or pull requests.
