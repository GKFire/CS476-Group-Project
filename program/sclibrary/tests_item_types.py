from django.test import TestCase
import sclibrary.models as SCLibraryModel
import sclibrary.forms.items as ItemForm

class ItemTypeTest(TestCase):
    def setUp(self):
        lender = SCLibraryModel.Lender.objects.create_user(username="lender", email="lender@lender.com", password="password")
        library = SCLibraryModel.Library.objects.get(owner=lender)
        SCLibraryModel.Item.objects.create(title="my random item", producer="producer", release="2021-01-01", library=library, item_type=SCLibraryModel.Item.Types.OTHER).save()
        SCLibraryModel.VideoGame.objects.create(title="videogame1", producer="producer", release="2021-01-01", library=library, item_type=SCLibraryModel.Item.Types.VIDEOGAME, item_format="PS3").save()
        SCLibraryModel.VideoGame.objects.create(title="videogame2", producer="producer", release="2021-01-01", library=library, item_format="PS3").save()
        SCLibraryModel.Movie.objects.create(title="movie1", producer="producer", release="2021-01-01", library=library, item_type=SCLibraryModel.Item.Types.MOVIE, item_format="BR").save()
        SCLibraryModel.Music.objects.create(title="music1", producer="producer", release="2021-01-01", library=library, item_type=SCLibraryModel.Item.Types.MUSIC, item_format="8T").save()
        SCLibraryModel.Book.objects.create(title="book1", producer="producer", release="2021-01-01", library=library, item_type=SCLibraryModel.Item.Types.BOOK, item_format="HARD").save()

    def testGetItemCreateForm(self):
        self.assertEqual(ItemForm.CreateItem, ItemForm.createNewItem(None))
        self.assertEqual(ItemForm.CreateItem, ItemForm.createNewItem("literally anything here"))
        self.assertEqual(ItemForm.CreateVideoGameItem, ItemForm.createNewItem("videogame"))
        self.assertEqual(ItemForm.CreateVideoGameItem, ItemForm.createNewItem("VIDEOGAME"))
        self.assertEqual(ItemForm.CreateMovieItem, ItemForm.createNewItem("movie"))
        self.assertEqual(ItemForm.CreateMovieItem, ItemForm.createNewItem("MOVIE"))
        self.assertEqual(ItemForm.CreateMusicItem, ItemForm.createNewItem("music"))
        self.assertEqual(ItemForm.CreateMusicItem, ItemForm.createNewItem("MUSIC"))
        self.assertEqual(ItemForm.CreateBookItem, ItemForm.createNewItem("book"))
        self.assertEqual(ItemForm.CreateBookItem, ItemForm.createNewItem("BOOK"))

    def testGetItemEditForm(self):
        self.assertEqual(ItemForm.EditItem, ItemForm.editItem(1))
        self.assertEqual(ItemForm.EditVideoGameItem, ItemForm.editItem(2))
        self.assertEqual(ItemForm.EditVideoGameItem, ItemForm.editItem(3))
        self.assertEqual(ItemForm.EditMovieItem, ItemForm.editItem(4))
        self.assertEqual(ItemForm.EditMusicItem, ItemForm.editItem(5))
        self.assertEqual(ItemForm.EditBookItem, ItemForm.editItem(6))