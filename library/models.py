from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Model for hold user details in tha app
    """
    phone_no = models.CharField(max_length=20, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        abstract = False
        default_permissions = ()

    def __str__(self):
        return self.username


class Book(models.Model):
    """
    Model for hold user details in the library
    """
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=128)
    book_code = models.CharField(max_length=50, unique=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()

    class Meta:
        default_permissions = ()
    
    def __str__(self):
        return self.title


class RequestBook(models.Model):
    """
    Model for hold book rquest and return
    """
    book_status = (
        ('1', 'placed'),
        ('2', 'returned'),
    )

    customer = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, on_delete=models.CASCADE)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=book_status)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.customer.first_name

    
class TimePeriod(models.Model):
    """
    Model for hold Library app permission time
    """
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        default_permissions = ()

    def __str__(self):
        return str(self.start_time)


class UserPermissions(models.Model):
    """
    user permission model, 
    staff add book permisssion for purticular staff
    """
    name = models.CharField(max_length=200, default="UserPermissions")

    class Meta:
        default_permissions = ()
        permissions = (
            ('staff_add_book', 'Add Book'),
            ('user_read_book', 'Read Book'),
        )

    def __str__(self):
        return self.name