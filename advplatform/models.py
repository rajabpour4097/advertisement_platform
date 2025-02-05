from django.db import models

'''
    TODO:
        3-start time and end time and deadline of 
            campaigns will be set
        
        
''' 

CUSTOMER = 1
DEALER = 2

JURIDICAL = 1
PRIVATE = 2

CORPORATE = 1
INFLUENCER = 2
PRIVATE_DESIGNER = 3

USER_TYPE = (
        (CUSTOMER, "Customer"),
        (DEALER, "Dealer"),
    )

CUSTOMER_TYPE = (
    (JURIDICAL, "Juridical"),
    (PRIVATE, "Private"),
)

DEALER_TYPE = (
    (CORPORATE, "Corporate"),
    (INFLUENCER, "Influencer"),
    (PRIVATE_DESIGNER, "Private Designer"),
)


class ActivityCategory(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Activity Category'
        verbose_name_plural = 'Activity Categories'
    
    def __str__(self):
        return self.name


class SpecialityCategory(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Speciality Category'
        verbose_name_plural = 'Speciality Categories'
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
    
    def __str__(self):
        return self.name
        
    
class AbstarctUser(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=40)
    firstname = models.CharField(max_length=30, null=True, blank=True)
    lastname = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=40, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def get_fullname(self):
        return f'{self.firstname} {self.lastname}'


class Mentor(AbstarctUser):
    rank = models.SmallIntegerField(default=0)
    speciality_field = models.ForeignKey(SpecialityCategory, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Mentor'
        verbose_name_plural = 'Mentors'
    
    def __str__(self):
        return (f'{self.firstname} {self.lastname}')
    

class Customer(AbstarctUser):
    field_of_activity = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    bussines_value = models.BigIntegerField(null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=CUSTOMER_TYPE)
    customer_mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return (f'{self.firstname} {self.lastname}')
       

class Dealer(AbstarctUser):
    rank = models.SmallIntegerField(default=0)
    type = models.PositiveSmallIntegerField(choices=DEALER_TYPE)
    
    class Meta:
        verbose_name = 'Dealer'
        verbose_name_plural = 'Dealers'
    
    def __str__(self):
        return (f'{self.firstname} {self.lastname}')

    
class Campaign(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic)
    describe = models.TextField()
    purposed_price = models.BigIntegerField(default=0)
    starttimedate = models.DateTimeField(null=True, blank=True)
    endtimedate = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    list_of_participants = models.ManyToManyField(
        Dealer, blank=True,
        related_name='campaigns'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
    
    def get_countdown_datetime(self):
        return self.endtimedate.strftime('%Y-%m-%dT%H:%M:%S')
    
    # def  participants_to_str(self):
    #     return ", ".join([participant.get_fullname for participant in self.list_of_participants])
    
    # def  topics_to_str(self):
    #     return ", ".join([topic.name for topic in self.topic])
    
    def __str__(self):
        return (f'{self.id} {self.customer}')
    
    

class Portfolio(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)
    done_time = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
    
    def __str__(self):
        return (f'{self.id} {self.dealer}')
    

class CustomerImages(models.Model):
    image = models.ImageField(upload_to='customers/')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customerimages')
    
    def __str__(self):
        return str(self.customer)


class DealerImages(models.Model):
    image = models.ImageField(upload_to='dealers/')
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='dealerimages')
    
    def __str__(self):
        return str(self.dealer)


class MentorImages(models.Model):
    image = models.ImageField(upload_to='mentors/')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentorimages')
    
    def __str__(self):
        return str(self.mentor)
    

class CampaignImages(models.Model):
    image = models.ImageField(upload_to='campaigns/')
    campaigns = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaignsimages')
    
    def __str__(self):
        return str(self.campaigns)


class PortfolioImages(models.Model):
    image = models.ImageField(upload_to='portfolios/')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolioimages')
    
    def __str__(self):
        return str(self.portfolio)