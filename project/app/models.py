from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User

class Restaurants(models.Model):
    title = models.CharField(max_length = 100)
    image = models.ImageField(null = True, blank = True, upload_to = "images/")
    address = models.CharField(max_length = 150)
    description = models.CharField(max_length = 650, default = "...")
    work_time = models.CharField(max_length = 50, default = "9:00 am - 22:00 pm")
    

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurants,
                                  on_delete=models.CASCADE)
    image = models.ImageField(null = True, blank = True, upload_to = "images/")
    title = models.CharField(max_length=70,)
    price = models.IntegerField()
    # contributors = models.ManyToManyField('Customer')

    def __str__(self):
        return self.title


class Customer(models.Model):
    first_names = models.CharField(max_length=50,
                                   help_text="The contributor's first name or names.")
    last_names = models.CharField(max_length=50,
                                  help_text="The contributor's last name or names.")
    email = models.EmailField(help_text="The contact email for the contributor.")

    def initialled_name(self):
        initials = ''.join([name[0] for name
                            in self.first_names.split(' ')])
        return "{}, {}".format(self.last_names, initials)

    def __str__(self):
        return self.initialled_name()
    

class Review(models.Model):
    content = models.TextField()
    rating = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.creator.username, self.restaurant.title)
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

class PaymentCard(models.Model):
    card_number = models.CharField(max_length=16)
    sum = models.IntegerField(default=0)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_number

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    table_number = models.IntegerField()

    def __str__(self):
        return f'Table {self.table_number} at {self.restaurant.title}'

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'{self.customer.username} at {self.table} on {self.start_time.strftime("%d %b %Y %H:%M")}'

    def is_conflicting(self):
        """
        Check if this reservation conflicts with any existing reservations for the same table
        """
        conflicting_reservations = Reservation.objects.filter(table=self.table, start_time__lt=self.end_time, end_time__gt=self.start_time)
        return conflicting_reservations.exists()


# Create your models here.
