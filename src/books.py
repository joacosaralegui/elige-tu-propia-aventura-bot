import json
import glob

class Book(object):
    def __init__(self, path):
        self.path = path
        with open(path+"guide.json") as json_file:
            data = json.load(json_file)      
            self.start = data['start']
            self.cover = data['cover']
            self.back = data['back']
            self.guide = data['order']
            self.hash = data['hash']

    def get_next(self,id):
        return self.guide[id]

    def get_start(self):
        return self.get_next(self.start)

    def get_image(self,id):
        image = glob.glob(self.path + "*" + id + "*")
        if len(image) > 0:
            return image[0]
        return None

BOOK_PATHS = {
    'PeligroEnOriente':'books/Peligro en oriente/',
    'LaSupercomputadora':'books/El superordenador/'
}


if __name__=="__main__":
    book = Book(BOOK_PATHS[0])
    import pdb; pdb.set_trace()