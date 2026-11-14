import sclibrary.models as SCLibraryModels
import sclibrary.forms.items as ItemForms


class AbstractItemFactory:
    default_class = SCLibraryModels.Item
    instances = []

    def appendItemInstance(self, typename: str, classdef):
        typename = typename.upper()
        for instance in self.instances:
            if instance[0] == typename:
                return
        self.instances.append((typename, classdef))

    def removeItemInstance(self, typename: str):
        typename = typename.upper()
        for instance in self.instances:
            if instance[0] == typename:
                self.instances.remove(instance)
                return

    def getItemMethods(self, typename: str):
        if typename != None:
            typename = typename.upper()
            for instance in self.instances:
                if instance[0] == typename:
                    return instance[1]
        return (self.default_class, ItemForms.CreateItem, ItemForms.EditItem)

    def createNewItem(self, type: str):
        return self.getItemMethods(type)[1]

    def editItem(self, item_id: int):
        item = SCLibraryModels.Item.objects.get(id=item_id)
        return self.getItemMethods(item.item_type)[2]

    def getProperItem(self, item):
        return self.getItemMethods(item.item_type)[0].objects.get(id=item.id)

    def getProperItems(self, items):
        return list(map(lambda item: self.getItemMethods(item.item_type)[0].objects.get(id=item.id), items))



class ItemFactory(AbstractItemFactory):

    def __init__(self):
        self.instances = [
            (SCLibraryModels.Item.Types.VIDEOGAME, (SCLibraryModels.VideoGame, ItemForms.CreateVideoGameItem, ItemForms.EditVideoGameItem)),
            (SCLibraryModels.Item.Types.MOVIE, (SCLibraryModels.Movie, ItemForms.CreateMovieItem, ItemForms.EditMovieItem)),
            (SCLibraryModels.Item.Types.MUSIC, (SCLibraryModels.Music, ItemForms.CreateMusicItem, ItemForms.EditMusicItem)),
            (SCLibraryModels.Item.Types.BOOK, (SCLibraryModels.Book, ItemForms.CreateBookItem, ItemForms.EditBookItem))
        ]
