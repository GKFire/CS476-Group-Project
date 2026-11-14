from django.test import TestCase
import sclibrary.models as SCLibraryModel
import sclibrary.forms.items as ItemForm
from django.apps import apps

sclibraryconfig = apps.get_app_config("sclibrary")

class ItemTypeTest(TestCase):
    def setUp(self):
        self.lender = SCLibraryModel.Lender.objects.create_user(username="lender", email="lender@lender.com", password="password")
        self.library = SCLibraryModel.Library.objects.get(owner=self.lender)
        self.item_1 = SCLibraryModel.Item.objects.create(title="my random item", producer="producer", release="2021-01-01", library=self.library, item_type=SCLibraryModel.Item.Types.OTHER)
        self.item_1.save()
        self.item_2 = SCLibraryModel.VideoGame.objects.create(title="videogame1", producer="producer", release="2021-01-01", library=self.library, item_type=SCLibraryModel.Item.Types.VIDEOGAME, item_format="PS3")
        self.item_2.save()
        self.item_3 = SCLibraryModel.VideoGame.objects.create(title="videogame2", producer="producer", release="2021-01-01", library=self.library, item_format="PS3")
        self.item_3.save()
        self.item_4 = SCLibraryModel.Movie.objects.create(title="movie1", producer="producer", release="2021-01-01", library=self.library, item_type=SCLibraryModel.Item.Types.MOVIE, item_format="BR")
        self.item_4.save()
        self.item_5 = SCLibraryModel.Music.objects.create(title="music1", producer="producer", release="2021-01-01", library=self.library, item_type=SCLibraryModel.Item.Types.MUSIC, item_format="8T")
        self.item_5.save()
        self.item_6 = SCLibraryModel.Book.objects.create(title="book1", producer="producer", release="2021-01-01", library=self.library, item_type=SCLibraryModel.Item.Types.BOOK, item_format="HARD")
        self.item_6.save()

    def testGetItemCreateForm(self):
        self.assertEqual(ItemForm.CreateItem, sclibraryconfig.item_factory.createNewItem(None))
        self.assertEqual(ItemForm.CreateItem, sclibraryconfig.item_factory.createNewItem("literally anything here"))
        self.assertEqual(ItemForm.CreateVideoGameItem, sclibraryconfig.item_factory.createNewItem("videogame"))
        self.assertEqual(ItemForm.CreateVideoGameItem, sclibraryconfig.item_factory.createNewItem("VIDEOGAME"))
        self.assertEqual(ItemForm.CreateMovieItem, sclibraryconfig.item_factory.createNewItem("movie"))
        self.assertEqual(ItemForm.CreateMovieItem, sclibraryconfig.item_factory.createNewItem("MOVIE"))
        self.assertEqual(ItemForm.CreateMusicItem, sclibraryconfig.item_factory.createNewItem("music"))
        self.assertEqual(ItemForm.CreateMusicItem, sclibraryconfig.item_factory.createNewItem("MUSIC"))
        self.assertEqual(ItemForm.CreateBookItem, sclibraryconfig.item_factory.createNewItem("book"))
        self.assertEqual(ItemForm.CreateBookItem, sclibraryconfig.item_factory.createNewItem("BOOK"))

    def testGetItemEditForm(self):
        self.assertEqual(ItemForm.EditItem, sclibraryconfig.item_factory.editItem(1))
        self.assertEqual(ItemForm.EditVideoGameItem, sclibraryconfig.item_factory.editItem(2))
        self.assertEqual(ItemForm.EditVideoGameItem, sclibraryconfig.item_factory.editItem(3))
        self.assertEqual(ItemForm.EditMovieItem, sclibraryconfig.item_factory.editItem(4))
        self.assertEqual(ItemForm.EditMusicItem, sclibraryconfig.item_factory.editItem(5))
        self.assertEqual(ItemForm.EditBookItem, sclibraryconfig.item_factory.editItem(6))

    def testGetProperItem(self):
        self.assertEqual(self.item_1, SCLibraryModel.Item.objects.get(id=self.item_1.id))
        self.assertEqual(self.item_1, sclibraryconfig.item_factory.getProperItem(SCLibraryModel.Item.objects.get(id=self.item_1.id)))

        self.assertNotEqual(self.item_2, SCLibraryModel.Item.objects.get(id=self.item_2.id))
        self.assertEqual(self.item_2, sclibraryconfig.item_factory.getProperItem(SCLibraryModel.Item.objects.get(id=self.item_2.id)))

        self.assertNotEqual(self.item_3, SCLibraryModel.Item.objects.get(id=self.item_3.id))
        self.assertNotEqual(self.item_3, sclibraryconfig.item_factory.getProperItem(SCLibraryModel.Item.objects.get(id=self.item_2.id)))
        self.assertEqual(self.item_3, sclibraryconfig.item_factory.getProperItem(SCLibraryModel.Item.objects.get(id=self.item_3.id)))

    def testGetProperItems(self):
        self.assertEqual([SCLibraryModel.Item.objects.get(id=self.item_1.id), SCLibraryModel.Item.objects.get(id=self.item_2.id), SCLibraryModel.Item.objects.get(id=self.item_3.id), SCLibraryModel.Item.objects.get(id=self.item_4.id), SCLibraryModel.Item.objects.get(id=self.item_5.id), SCLibraryModel.Item.objects.get(id=self.item_6.id)], list(SCLibraryModel.Item.objects.all()))
        self.assertNotEqual([self.item_1, self.item_2, self.item_3, self.item_4, self.item_5, self.item_6], list(SCLibraryModel.Item.objects.all()))
        self.assertEqual([self.item_1, self.item_2, self.item_3, self.item_4, self.item_5, self.item_6], sclibraryconfig.item_factory.getProperItems(list(SCLibraryModel.Item.objects.all())))
        self.assertEqual([self.item_2, self.item_3], sclibraryconfig.item_factory.getProperItems(list(SCLibraryModel.Item.objects.filter(item_type="VIDEOGAME"))))