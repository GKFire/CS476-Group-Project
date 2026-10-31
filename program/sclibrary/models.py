from __future__ import annotations
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from random import randrange
from abc import ABC, abstractmethod
from typing import List

# Create your models here.

class UserAccountManager(BaseUserManager):
    def create_user(self, username: str, email: str, password):
        if not email or len(email) <= 0:
            raise ValueError("The email field is required to create an account!")
        if not username or len(username) <= 0:
            raise ValueError("The username field is required to create an account!")
        if not password:
            raise ValueError("A user MUST have a password associated with their account!")

        user = self.model(
            username = username.lower(),
            email = email.lower(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str, password):
        user = self.create_user(
            username = username.lower(),
            email = email.lower(), 
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.user_type = UserAccount.Types.ADMIN
        user.save(using = self._db)
        return user

class UserAccount(AbstractBaseUser):
    class Types(models.TextChoices):
        LENDER = "LENDER","lender"
        BORROWER = "BORROWER","borrower"
        ADMIN = "ADMIN","admin"
    
    user_type = models.CharField(max_length=15, choices=Types.choices)
    username = models.CharField(max_length=63, unique=True)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD="username"
    EMAIL_FIELD="email"
    REQUIRED_FIELDS= ["email"]

    objects = UserAccountManager()

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, app_label):
        return True
    def save(self, *args, **kwargs):
        if not self.user_type or self.user_type == None:
            self.user_type = UserAccount.Types.BORROWER
        return super().save(*args, **kwargs)

class BorrowerManager(models.Manager):
    def create_user(self, username: str, email: str, password=None):
        if not email or len(email) <= 0:
            raise ValueError("The email field is required to create an account!")
        if not username or len(username) <= 0:
            raise ValueError("The username field is required to create an account!")
        if not password:
            raise ValueError("A user MUST have a password associated with their account!")

        user = self.model(
            username = username.lower(),
            email = email.lower(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(user_type = UserAccount.Types.BORROWER)

class Borrower(UserAccount):
    objects = BorrowerManager()
    
    def save(self, *args, **kwargs):
        self.user_type = UserAccount.Types.BORROWER
        return super().save(*args, **kwargs)


class LenderManager(models.Manager):
    def create_user(self, username: str, email: str, password=None):
        if not email or len(email) <= 0:
            raise ValueError("The email field is required to create an account!")
        if not username or len(username) <= 0:
            raise ValueError("The username field is required to create an account!")
        if not password:
            raise ValueError("A user MUST have a password associated with their account!")

        user = self.model(
            username = username.lower(),
            email = email.lower(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(user_type = UserAccount.Types.LENDER)

class Lender(UserAccount):
    objects = LenderManager()
    
    def save(self, *args, **kwargs):
        is_new = self.id is None
        self.user_type = UserAccount.Types.LENDER
        return super().save(*args, **kwargs)


class Library(models.Model):
    name = models.CharField(max_length=63,unique=True)
    default_item_visibility = models.BooleanField(default=True)
    owner = models.OneToOneField(Lender, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    title = models.CharField(max_length=127)
    release = models.DateField()
    producer = models.CharField(max_length=127)
    # thumbnail = models.ImageField(null=True)
    condition = models.CharField(max_length=127,null=True)
    description = models.TextField(null=True)
    notes = models.TextField(null=True)

    FORMAT_CHOICES = [
        ("Video Game", (
                ("NS2", "Nintendo Switch 2"),
                ("NS", "Nintendo Switch"),
                ("WU", "Nintendo Wii U"),
                ("3DS", "Nintendo 3DS"),
                ("Wii", "Nintendo Wii"),
                ("NDS", "Nintendo DS"),
                ("GCN", "Nintendo GameCube"),
                ("PS5", "Playstation 5"),
                ("PS4", "Playstation 4"),
                ("PS3", "Playstation 3"),
                ("PS2", "Playstation 2"),
                ("PS1", "Playstation 1"),
                ("XS", "Xbox Series X/S"),
                ("XOne", "Xbox One"),
                ("X360", "Xbox 360"),
                ("Xbox", "Xbox"),),
        ),
        ("Movie", (
            ("UHD", "4K Blu-Ray"),
            ("BR", "Blu-Ray"),
            ("HD-DVD", "HD-DVD"),
            ("DVD", "DVD"),
            ("LD", "Laser-Disc"),),
        ),
        ("Music", (
            ("CD", "CD"),
            ("RD-70", "70mm Record"),
            ("RD-45", "45mm Record"),
            ("CT", "Cassette Tape"),
            ("8T", "8-Track"),),
        ),
        ("Book", "Physical Book"),
        ("Other", "Other"),
    ]

    item_format = models.CharField(max_length=15, choices=FORMAT_CHOICES)

    AGE_RATING_CHOICES = [
        ("Y7", "Y-7"),
        ("G", "G"),
        ("PG", "PG"),
        ("TV-PG", "TV-PG"),
        ("PG-13", "PG-13"),
        ("TV-14", "TV-14"),
        ("TV-16", "TV-16"),
        ("TV-18", "TV-18"),
        ("R", "R"),
        ("E", "E"),
        ("E10", "E-10+"),
        ("T", "T"),
        ("M", "M"),
        ("A", "A"),
    ]

    age_rating = models.CharField(max_length=15,choices=AGE_RATING_CHOICES)
    addedDate = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)

    def item_type(self):
        for format in Item.FORMAT_CHOICES:
            for entry in format[1]:
                if self.item_format == entry[0]:
                    return format[0]
        return None

    def __str__(self):
        return self.library.name + " - " + self.title

    def get_absolute_url(self):
        return reverse("view-item", kwargs={"item_pk": self.id})

class BorrowRequest(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    start_date = models.DateField()
    return_date = models.DateField()

    STATUS_CHOICES = [
        ("RQ", "Requested"),
        ("AC", "Active"),
        ("RJ", "Rejected"),
        ("CD", "Concluded"),
    ]

    status = models.CharField(max_length=31, choices=STATUS_CHOICES, default="RQ")

    def __str__(self):
        return self.status + " - " + self.item.title + " - " + self.borrower.username

class LenderMessage(models.Model):
    request = models.ForeignKey(BorrowRequest, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.request.item.title + " - " + self.timestamp

class BorrowerMessage(models.Model):
    request = models.ForeignKey(BorrowRequest, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.request.item.title + " - " + self.timestamp

class BorrowerWishList(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.borrower.username + " - " + self.item.title

class LenderNotification(models.Model):
    recipient = models.ForeignKey(Lender, on_delete=models.CASCADE)
    subject = models.CharField(max_length=127)
    description = models.TextField()
    has_viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject + " - " + self.recipient.username

class BorrowerNotification(models.Model):
    recipient = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    subject = models.CharField(max_length=127)
    description = models.TextField()
    has_viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject + " - " + self.recipient.username

"""

OBSERVER DESIGN PATTERN BELOW

"""
class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass


class ConcreteSubject(Subject):
    """
    The Subject owns some important state and notifies observers when the state
    changes.
    """

    _state: int = None
    """
    For the sake of simplicity, the Subject's state, essential to all
    subscribers, is stored in this variable.
    """

    _observers: List[Observer] = []
    """
    List of subscribers. In real life, the list of subscribers can be stored
    more comprehensively (categorized by event type, etc.).
    """

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    """
    The subscription management methods.
    """

    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """

        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)

    def some_business_logic(self) -> None:
        """
        Usually, the subscription logic is only a fraction of what a Subject can
        really do. Subjects commonly hold some important business logic, that
        triggers a notification method whenever something important is about to
        happen (or after it).
        """

        print("\nSubject: I'm doing something important.")
        self._state = randrange(0, 10)

        print(f"Subject: My state has just changed to: {self._state}")
        self.notify()


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass


"""
Concrete Observers react to the updates issued by the Subject they had been
attached to.
"""


class ConcreteObserverA(Observer):
    def update(self, subject: Subject) -> None:
        if subject._state < 3:
            print("ConcreteObserverA: Reacted to the event")


class ConcreteObserverB(Observer):
    def update(self, subject: Subject) -> None:
        if subject._state == 0 or subject._state >= 2:
            print("ConcreteObserverB: Reacted to the event")

