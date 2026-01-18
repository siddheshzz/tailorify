# import os
# from celery import Celery
# import resend

# # Inside Docker, 'redis' resolves to the Redis container IP
# redis_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
# resend.api_key = os.getenv("RESEND_KEY")

# celery_app = Celery(
#     "tailorify_tasks",
#     broker=redis_url,
#     backend=redis_url
# )

# @celery_app.task
# def sample_task(name: str):
#     r = resend.Emails.send({
#             "from": "onboarding@resend.dev",
#             "to": ".me",
#             "subject": "Hello World",
#             "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
#         })
#     return f"Hello {name}, Sent mail complete!"