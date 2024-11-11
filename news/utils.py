from django.utils.timezone import now
from datetime import timedelta

def calculate_account_age(date_joined):
    delta = now() - date_joined
    if delta < timedelta(hours=1):
        return f"{delta.seconds // 60} minutes ago"
    elif delta < timedelta(days=1):
        return f"{delta.seconds // 3600} hours ago"
    elif delta < timedelta(days=30):
        return f"{delta.days} days ago"
    elif delta < timedelta(days=365):
        return f"{delta.days // 30} months ago"
    else:
        return f"{delta.days // 365} years ago"