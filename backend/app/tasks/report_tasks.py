from app.core.celery_app import celery_app

@celery_app.task
def generate_sales_report():
    # placeholder
    print("Generating sales report")
