from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Category(BaseModel):
    """
    Category model for grouping events.
    """
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name

class Event(BaseModel):
    """
    Event model as specified.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('deleted', 'Deleted'),
    ]

    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    is_free = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.title

class Ticket(BaseModel):
    """
    Ticket model as specified.
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.IntegerField()
    booked_seats = models.IntegerField(default=0)
    is_deleted_field = models.BooleanField(default=False) # Avoiding conflict with BaseModel.is_deleted
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')

    class Meta:
        db_table = 'tickets'

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class Payment(BaseModel):
    """
    Payment model as specified.
    """
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    ticket_count = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment {self.transaction_id} by {self.full_name}"
