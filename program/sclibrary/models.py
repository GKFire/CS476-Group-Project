from django.db import models

# Create your models here.

class Lender(models.Model):
    username = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=256)

class Borrower(models.Model):
    username = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=256)

class Library(models.Model):
    name = models.CharField(max_length=64)
    default_item_visibility = models.BooleanField()
    owner = models.ForeignKey(Lender, on_delete=models.CASCADE)

class Item(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    release = models.DateField()
    producer = models.CharField(max_length=128)
    thumbnail = models.ImageField()
    condition = models.CharField(max_length=128)
    description = models.TextField()
    notes = models.TextField()

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

    item_format = models.CharField(max_length=16, choices=FORMAT_CHOICES)

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


    age_rating = models.CharField(max_length=16,choices=AGE_RATING_CHOICES)
    addedDate = models.DateTimeField()
    lastModified = models.DateTimeField()
    is_visible = models.BooleanField()

class BorrowRequest(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    start_date = models.DateField()
    return_date = models.DateField()

    STATUS_CHOICES = [
        ("RQ", "Requested"),
        ("AC", "Active"),
        ("RJ", "Rejected"),
        ("CD", "Concluded"),
    ]

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="CD")

class LenderMessage(models.Model):
    request = models.ForeignKey(BorrowRequest, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField()

class BorrowerMessage(models.Model):
    request = models.ForeignKey(BorrowRequest, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField()

class BorrowerWishList(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    added = models.DateTimeField()

class LenderNotification(models.Model):
    recipient = models.ForeignKey(Lender, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    description = models.TextField()
    has_viewed = models.BooleanField()
    timestamp = models.DateTimeField()

class BorrowerNotification(models.Model):
    recipient = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    description = models.TextField()
    has_viewed = models.BooleanField()
    timestamp = models.DateTimeField()

