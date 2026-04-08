from app.core.celery_app import celery_app

@celery_app.task
def send_welcome_email(to_email: str):
    # placeholder
    print(f"Send welcome email to {to_email}")
