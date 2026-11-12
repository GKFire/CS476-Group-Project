""" Test search functionality (Korbin) """
from django.test import TestCase
from django.test.client import RequestFactory
import sclibrary.models as SCLibraryModel
from sclibrary.forms.items import get_searchset


def createItem(model, title_v, library_v, item_type_v, item_format_v=None):
    if not item_format_v:
        item = model.objects.create(title=title_v, producer="producer", release="2021-01-01", library=library_v, item_type=item_type_v)
    else:
        item = model.objects.create(title=title_v, producer="producer", release="2021-01-01", library=library_v, item_type=item_type_v, item_format=item_format_v)
    item.save()
    return SCLibraryModel.Item.objects.get(id=item.id)


class ItemTypeTest(TestCase):
    def setUp(self):
        lender_1 = SCLibraryModel.Lender.objects.create_user(username="lender_1", email="lender@lender.com", password="password")
        library_1 = SCLibraryModel.Library.objects.get(owner=lender_1)
        lender_2 = SCLibraryModel.Lender.objects.create_user(username="lender_2", email="lender2@lender.com", password="password")
        library_2 = SCLibraryModel.Library.objects.get(owner=lender_2)

        self.random_item_1 = createItem(SCLibraryModel.Item, "my_random_item", library_1, SCLibraryModel.Item.Types.OTHER)
        self.videogame_1 = createItem(SCLibraryModel.VideoGame, "videogame1", library_1, SCLibraryModel.Item.Types.VIDEOGAME, "PS3")
        self.movie_1 = createItem(SCLibraryModel.Movie, "movie1", library_1, SCLibraryModel.Item.Types.MOVIE, "BR")
        self.music_1 = createItem(SCLibraryModel.Music, "music1", library_1, SCLibraryModel.Item.Types.MUSIC, "8T")
        self.music_2 = createItem(SCLibraryModel.Music, "music2", library_2, SCLibraryModel.Item.Types.MUSIC, "8T")
        self.music_3 = createItem(SCLibraryModel.Music, "music3", library_2, SCLibraryModel.Item.Types.MUSIC, "8T")
        self.book_1 = createItem(SCLibraryModel.Book, "book1", library_2, SCLibraryModel.Item.Types.BOOK, "HARD")

        self.factory = RequestFactory()

    def testgetSearchQueryList(self):
        self.assertEqual([self.book_1, self.movie_1, self.music_1, self.music_2, self.music_3, self.random_item_1, self.videogame_1], list(get_searchset(self.factory.get("/search/"))))
        self.assertEqual([self.book_1, self.movie_1, self.music_1, self.music_2, self.music_3, self.random_item_1, self.videogame_1], list(get_searchset(self.factory.get("/search/?library=0"))))
        self.assertEqual([self.movie_1, self.music_1, self.random_item_1, self.videogame_1], list(get_searchset(self.factory.get("/search/?library=1"))))
        self.assertEqual([self.book_1, self.music_2, self.music_3], list(get_searchset(self.factory.get("/search/?library=2"))))
        self.assertEqual([self.music_1, self.music_2, self.music_3], list(get_searchset(self.factory.get("/search/?type=music"))))
        self.assertEqual([self.music_2, self.music_3], list(get_searchset(self.factory.get("/search/?library=2&type=music"))))
        self.assertEqual([self.music_2], list(get_searchset(self.factory.get("/search/?title=music2"))))
        self.assertEqual([], list(get_searchset(self.factory.get("/search/?library=1&title=music2"))))
        self.assertEqual([], list(get_searchset(self.factory.get("/search/?library=5"))))
        self.assertEqual([], list(get_searchset(self.factory.get("/search/?library=notalibrary"))))