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

    class Types(models.TextChoices):
        VIDEOGAME = "VIDEOGAME","Video Game"
        MOVIE = "MOVIE","Movie"
        MUSIC = "MUSIC","Music"
        BOOK = "BOOK","Book"
        OTHER = "OTHER","Other"

    item_type = models.CharField(max_length=15)
    addedDate = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.library.name + " - " + self.title

    def get_icon_name(self) -> str:
        return "collections"

    def get_absolute_url(self):
        return reverse("view-item", kwargs={"item_pk": self.id})

    def get_item_type_display(self):
        return Item.Types(self.item_type).label

    def get_item_types_list():
        return list(map(lambda type : Item.Types(type).label, Item.Types))


class VideoGameManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(item_type=Item.Types.VIDEOGAME)

class VideoGame(Item):
    objects = VideoGameManager()

    FORMAT_CHOICES = [
        ("NS2", "Nintendo Switch 2"),
        ("NS", "Nintendo Switch"),
        ("WU", "Nintendo Wii U"),
        ("3DS", "Nintendo 3DS"),
        ("Wii", "Nintendo Wii"),
        ("NDS", "Nintendo DS"),
        ("GCN", "Nintendo GameCube"),
        ("N64", "Nintendo N64"),
        ("SNES", "Nintendo SNES"),
        ("NES", "Nintendo NES"),
        ("PS5", "Playstation 5"),
        ("PS4", "Playstation 4"),
        ("PS3", "Playstation 3"),
        ("PS2", "Playstation 2"),
        ("PS1", "Playstation 1"),
        ("XS", "Xbox Series X/S"),
        ("XOne", "Xbox One"),
        ("X360", "Xbox 360"),
        ("Xbox", "Xbox")
    ]

    AGE_RATING_CHOICES = [
        ("E", "E"),
        ("E10", "E-10+"),
        ("T", "T"),
        ("M", "M"),
        ("A", "A"),
    ]

    item_format = models.CharField(max_length=15, choices=FORMAT_CHOICES)
    age_rating = models.CharField(max_length=15, choices=AGE_RATING_CHOICES)

    def __str__(self) -> str:
        return self.get_format_display() + " - " + self.library.name + " - " + self.title

    def get_format_display(self) -> str:
        for item_format in VideoGame.FORMAT_CHOICES:
            if self.item_format == item_format[0]:
                return item_format[1]
        return "undefined"

    def get_age_display(self) -> str:
        for age_rating in VideoGame.AGE_RATING_CHOICES:
            if self.age_rating == age_rating[0]:
                return age_rating[1]
        return "undefined"

    def save(self, *args, **kwargs):
        self.item_type = Item.Types.VIDEOGAME
        return super().save(*args, **kwargs)

    def get_icon_name(self) -> str:
        return "gamepad"

class MovieManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(item_type=Item.Types.MOVIE)

class Movie(Item):
    objects = MovieManager()

    FORMAT_CHOICES = [
        ("UHD", "4K Blu-Ray"),
        ("BR", "Blu-Ray"),
        ("HD-DVD", "HD-DVD"),
        ("DVD", "DVD"),
        ("LD", "Laser-Disc")
    ]

    AGE_RATING_CHOICES = [
        ("Y7", "Y-7"),
        ("G", "G"),
        ("PG", "PG"),
        ("TV-PG", "TV-PG"),
        ("PG-13", "PG-13"),
        ("TV-14", "TV-14"),
        ("TV-16", "TV-16"),
        ("TV-18", "TV-18"),
        ("R", "R")
    ]

    item_format = models.CharField(max_length=15, choices=FORMAT_CHOICES)
    age_rating = models.CharField(max_length=15, choices=AGE_RATING_CHOICES)

    def get_format_display(self) -> str:
        for item_format in Movie.FORMAT_CHOICES:
            if self.item_format == item_format[0]:
                return item_format[1]
        return "undefined"

    def get_age_display(self) -> str:
        for age_rating in Movie.AGE_RATING_CHOICES:
            if self.age_rating == age_rating[0]:
                return age_rating[1]
        return "undefined"

    def save(self, *args, **kwargs):
        self.item_type = Item.Types.MOVIE
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.get_format_display() + " - " + self.library.name + " - " + self.title

    def get_icon_name(self) -> str:
        return "movie"


class MusicManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(item_type=Item.Types.MUSIC)

class Music(Item):
    objects = MusicManager()

    FORMAT_CHOICES = [
        ("CD", "CD"),
        ("RD-70", "70mm Record"),
        ("RD-45", "45mm Record"),
        ("CT", "Cassette Tape"),
        ("8T", "8-Track")
    ]

    AGE_RATING_CHOICES = [
        ("Y", "Youth"),
        ("G", "General"),
        ("YA", "Young Adult"),
        ("T", "Tean"),
        ("A", "Adult")
    ]

    item_format = models.CharField(max_length=15, choices=FORMAT_CHOICES)
    age_rating = models.CharField(max_length=15, choices=AGE_RATING_CHOICES)

    def get_format_display(self) -> str:
        for item_format in Music.FORMAT_CHOICES:
            if self.item_format == item_format[0]:
                return item_format[1]
        return "undefined"

    def get_age_display(self) -> str:
        for age_rating in Music.AGE_RATING_CHOICES:
            if self.age_rating == age_rating[0]:
                return age_rating[1]
        return "undefined"

    def save(self, *args, **kwargs):
        self.item_type = Item.Types.MUSIC
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.get_format_display() + " - " + self.library.name + " - " + self.title

    def get_icon_name(self) -> str:
        return "library-music"


class BookManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(item_type=Item.Types.BOOK)

class Book(Item):
    objects = BookManager()

    FORMAT_CHOICES = [
        ("HARD", "Hard Cover"),
        ("SOFT", "Soft Cover"),
        ("ADIO", "Audiobook")
    ]

    AGE_RATING_CHOICES = [
        ("Y", "Youth"),
        ("G", "General"),
        ("YA", "Young Adult"),
        ("T", "Tean"),
        ("A", "Adult")
    ]

    item_format = models.CharField(max_length=15, choices=FORMAT_CHOICES)
    age_rating = models.CharField(max_length=15, choices=AGE_RATING_CHOICES)

    def get_format_display(self) -> str:
        for item_format in Book.FORMAT_CHOICES:
            if self.item_format == item_format[0]:
                return item_format[1]
        return "undefined"

    def get_age_display(self) -> str:
        for age_rating in Book.AGE_RATING_CHOICES:
            if self.age_rating == age_rating[0]:
                return age_rating[1]
        return "undefined"

    def save(self, *args, **kwargs):
        self.item_type = Item.Types.BOOK
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.get_format_display() + " - " + self.library.name + " - " + self.title

    def get_icon_name(self) -> str:
        return "book"

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

    def get_status_choice_display(self) -> str:
        for status in BorrowRequest.STATUS_CHOICES:
            if self.status == status[0]:
                return status[1]
        return "undefined"

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

    ## Initilization function
    def __init__(self, item) -> None:
        self.item = item ## Sets the item for the subject
        self._observers: List[Observer] = [] ## Sets the list of observers for the subject, and initializes it to an empty list

    ## Attach function 
    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    ## Detach function
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        print("Subject: Removed an observer.")

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

class ConcreteObserver(Observer):
    def __init__(self, borrower) -> None:
        self.borrower = borrower

    def update(self, subject: Subject) -> None:
        import sclibrary.notifications as N ## import put here to not create a circular dependency
        if subject.item.is_borrowed:
            print(f"Observer: {self.borrower.username} has been notified that {subject.item.title} is now borrowed.")
            N.notify_wishlist_unavailable(subject.item, self.borrower)

        else:
            print(f"Observer: {self.borrower.username} has been notified that {subject.item.title} is now available.")
            N.notify_wishlist_available(subject.item, self.borrower)



