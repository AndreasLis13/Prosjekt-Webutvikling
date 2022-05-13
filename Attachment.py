
from mimetypes import init


class Attachment:
    def __init__(self, id, BrukerId, KategoriId, Tittel, Beskrivelse, Dato, File, Mimetype, Size):
        self.id = id
        self.BrukerId = BrukerId 
        self.KategoriId = KategoriId
        self.Tittel = Tittel
        self.Beskrivelse = Beskrivelse
        self.Dato = Dato 
        self.File = File 
        self.Mimetype = Mimetype 
        self.Size = Size 

    
    def file(self):
        return self.File

    def mimetype(self):
        return self.Mimetype 

    def size(self):
        return self.Size

    def filename(self):
        return self.Tittel
    
    def id(self):
        return self.id

    def dato(self):
        return self.dato 


class Comment:
    def __init__(self, KommentarId, PostId, Kommentar, BrukerId):
        self.KommentarId = KommentarId
        self.PostId = PostId
        self.Kommentar = Kommentar 
        self.BrukerId = BrukerId



        