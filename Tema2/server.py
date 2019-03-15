from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import cgi, json, codecs, requests, time, threading
from socketserver import ThreadingMixIn
import uuid

books = json.loads(open("books.json").read())
authors = json.loads(open("authors.json").read())
readers = json.loads(open("readers.json").read())
readersBooks = json.loads(open("readersBooks.json").read())

def commitChanges():
    open("books.json", 'w').write(json.dumps(books))
    open("authors.json", 'w').write(json.dumps(authors))
    open("readers.json", 'w').write(json.dumps(readers))
    open("readersBooks.json", 'w').write(json.dumps(readersBooks))

def getAllBooks():
    return books

def getAllBooksForReaderId(readerId):
    if not getReaderById(readerId):
        return False

    result = []
    for readerBook in readersBooks:
        if readerId == readerBook['readerId']:
            result.append(getBookById(readerBook['bookId']))
    return result

def getBookForReaderId(readerId, bookId):
    if not getReaderById(readerId):
        return False

    for readerBook in getAllBooksForReaderId(readerId):
        if bookId == readerBook['id']:
            return readerBook
    return False

def getAllBooksForAuthorId(authorId):
    if not getAuthorById(authorId):
        return False

    result = []
    for book in books:
        if authorId == book['authorId']:
            result.append(book)
    return result

def getBookForAuthorId(authorId, bookId):
    if not getAuthorById(authorId):
        return False

    for book in getAllBooksForAuthorId(authorId):
        if bookId == book['id']:
            return book
    return False

def getAllReaders():
    return readers

def getReaderFromBookId(bookId):
    for readerBook in readersBooks:
        if readerBook['bookId'] == bookId:
            return getReaderById(readerBook['readerId'])
    return False

def getAuthorFromBookId(bookId):
    if not getBookById(bookId):
        return False

    book = getBookById(bookId)
    author = getAuthorById(book['authorId'])
    return author

def getAllAuthors():
    return authors

def getBookById(id):
    for book in books:
        if book['id'] == id:
            return book
    return False

def getAuthorById(id):
    for author in authors:
        if author['id'] == id:
            return author
    return False

def getReaderById(id):
    for reader in readers:
        if reader['id'] == id:
            return reader
    return False

def insertBook(name, authorId, genre):
    if not getAuthorById(authorId):
        return 404

    book = {'id': str(uuid.uuid4()), 'name': name, 'authorId': authorId, 'genre': genre}
    books.append(book)
    return book

def insertReader(name):
    reader = {'id': str(uuid.uuid4()), 'name': name}
    readers.append(reader)
    return reader

def insertAuthor(name):
    author = {'id': str(uuid.uuid4()), 'name': name}
    authors.append(author)
    return author

def insertReaderBook(readerId, bookId):
    if not getBookById(bookId):
        return 404
    
    if not getReaderById(readerId):
        return 404

    if getReaderFromBookId(bookId) != False or len(getAllBooksForReaderId(readerId)) > 3:
        return 409
    
    readerBook = {'id': str(uuid.uuid4()), 'readerId': readerId, 'bookId': bookId}
    readersBooks.append(readerBook)
    return readerBook

def deleteReaderById(readerId):
    if not getReaderById(readerId):
        return False
    
    for i in range(0, len(readers)):
        if readers[i]['id'] == readerId:
            readers.pop(i)
            break
    
    for i in range(0, len(readersBooks)):
        if readersBooks[i]['readerId'] == readerId:
            readersBooks.pop(i)
            i -= 1

    return True

def deleteBookById(bookId):
    if not getBookById(bookId):
        return False
    
    for i in range(0, len(books)):
        if books[i]['id'] == bookId:
            books.pop(i)
            break
    
    for i in range(0, len(readersBooks)):
        if readersBooks[i]['bookId'] == bookId:
            readersBooks.pop(i)
            i -= 1

    return True

def deleteReaderBookById(readerId, bookId):
    if not getBookForReaderId(readerId, bookId):
        return False

    for i in range(0, len(readersBooks)):
        if readersBooks[i]['bookId'] == bookId:
            readersBooks.pop(i)
            return True

def deleteAuthorById(authorId):
    if not getAuthorById(authorId):
        return False
    
    for i in range(0, len(authors)):
        if authors[i]['id'] == authorId:
            authors.pop(i)
            break

    if getAllBooksForAuthorId(authorId):
        for book in getAllBooksForAuthorId(authorId):
            deleteBookById(book['id'])

    return True

def updateBook(bookId, data):
    if not getBookById(bookId) or not getAuthorById(data['authorId']):
        return False

    for i in range(0, len(books)):
        if books[i]['id'] == bookId:
            books[i]['name'] = data['name']
            books[i]['genre'] = data['genre']
            books[i]['authorId'] = data['authorId']
            return books[i]

def updateAuthor(authorId, data):
    if not getAuthorById(authorId):
        return False
        
    for i in range(0, len(authors)):
        if authors[i]['id'] == authorId:
            authors[i]['name'] = data['name']
            return authors[i]

def bulkInsertReaderBooks(readerId, bookIds):
    if len(bookIds) > 3:
        return False

    currentReaderBooks = getAllBooksForReaderId(readerId)

    for book in currentReaderBooks:
        deleteReaderBookById(readerId, book['id'])

    for bookId in bookIds:
        insertReaderBook(readerId, bookId)
    return True
    

def updateReader(readerId, data):
    if not getReaderById(readerId):
        return False
        
    for i in range(0, len(readers)):
        if readers[i]['id'] == readerId:
            readers[i]['name'] = data['name']
            if 'books' in data:
                if not bulkInsertReaderBooks(readerId,data['books']):
                    return 409
            return readers[i]

def splitUrl(path):
    if '?' in path:
        path = path.split("?")[0]
    return path.split('/')[1:]


class RestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            splittedUrl = splitUrl(self.path)
            response = 400

            if self.headers['Content-Type'] != 'application/json':
                self.send_response(415)
                self.end_headers()
                return

            if splittedUrl[0] == 'readers':
                if len(splittedUrl) == 1:
                    response = getAllReaders()
                    if len(response) == 0:
                        response = 204
                elif len(splittedUrl) == 2:
                    response = getReaderById(splittedUrl[1])
                elif len(splittedUrl) == 3 and splittedUrl[2] == 'books':
                    response = getAllBooksForReaderId(splittedUrl[1])
                    if len(response) == 0:
                        response = 204
                elif len(splittedUrl) == 4 and splittedUrl[2] == 'books':
                    response = getBookForReaderId(splittedUrl[1], splittedUrl[3])

            elif splittedUrl[0] == 'books':
                if len(splittedUrl) == 1:
                    response = getAllBooks()
                    if len(response) == 0:
                        response = 204
                if len(splittedUrl) == 2:
                    response = getBookById(splittedUrl[1])
                if len(splittedUrl) == 3 and splittedUrl[2] == 'reader':
                    response = getReaderFromBookId(splittedUrl[1])
                    if len(response) == 0:
                        response = 204
                if len(splittedUrl) == 3 and splittedUrl[2] == 'author':
                    response = getAuthorFromBookId(splittedUrl[1])

            elif splittedUrl[0] == 'authors':
                if len(splittedUrl) == 1:
                    response = getAllAuthors()
                    if len(response) == 0:
                        response = 204
                if len(splittedUrl) == 2:
                    response = getAuthorById(splittedUrl[1])
                if len(splittedUrl) == 3 and splittedUrl[2] == 'books':
                    response = getAllBooksForAuthorId(splittedUrl[1])
                    if len(response) == 0:
                        response = 204
                if len(splittedUrl) == 4 and splittedUrl[2] == 'books':
                    response = getBookForAuthorId(splittedUrl[1], splittedUrl[3])

            if response == 400 or response == 204:
                self.send_response(204)
                self.end_headers()
                return
            if not response:
                self.send_response(404)
                self.end_headers()
                return
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return
        except:
            self.send_response(500)
            self.end_headers()
            return

    def do_POST(self):
        try:
            response = 400
            splittedUrl = splitUrl(self.path)
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))

            if self.headers['Content-Type'] != 'application/json':
                self.send_response(415)
                self.end_headers()
                return

            if splittedUrl[0] == 'readers':
                if len(splittedUrl) == 1:
                    if not 'name' in data:
                        response = 400
                    else:
                        response = insertReader(data['name'])
                elif len(splittedUrl) == 4 and splittedUrl[2] == 'books':
                    response = insertReaderBook(splittedUrl[1], splittedUrl[3])
            elif splittedUrl[0] == 'books':
                if len(splittedUrl) == 1:
                    if not 'name' in data or not 'authorId' in data or not 'genre' in data:
                        response = 400
                    else:
                        response = insertBook(data['name'], data['authorId'], data['genre'])
            elif splittedUrl[0] == 'authors':
                if len(splittedUrl) == 1:
                    if not 'name' in data:
                        response = 400
                    else:
                        response = insertAuthor(data['name'])
                if len(splittedUrl) == 3 and splittedUrl[2] == 'books':
                    if not 'name' in data or not 'genre' in data:
                        response = 400
                    else:
                        response = insertBook(data['name'], splittedUrl[1], data['genre'])

            if response == 409 or response == 404 or response == 400:
                    self.send_response(response)
                    self.end_headers()
                    return
            else:
                self.send_response(201)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                commitChanges()
                return
        except:
            self.send_response(500)
            self.end_headers()
            return

    def do_PUT(self):
        try:
            response = 400
            splittedUrl = splitUrl(self.path)
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))

            if self.headers['Content-Type'] != 'application/json':
                self.send_response(415)
                self.end_headers()
                return

            if len(splittedUrl) == 2 and splittedUrl[0] == 'readers':
                if not 'name' in data:
                    response = 400
                else:
                    response = updateReader(splittedUrl[1], data)
            elif len(splittedUrl) == 2 and splittedUrl[0] == 'books':
                if not 'name' in data or not 'authorId' in data or not 'genre' in data:
                    response = 400
                else:
                    response = updateBook(splittedUrl[1], data)
            elif len(splittedUrl) == 2 and splittedUrl[0] == 'authors':
                if not 'name' in data:
                    response = 400
                else:
                    response = updateAuthor(splittedUrl[1], data)

            if response == 400:
                self.send_response(400)
                self.end_headers()
                return
            if response == 409:
                self.send_response(409)
                self.end_headers()
                return
            if not response:
                self.send_response(404)
                self.end_headers()
                return
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                commitChanges()
                return
        except:
            self.send_response(500)
            self.end_headers()
            return

    def do_DELETE(self):
        try:
            response = 400
            splittedUrl = splitUrl(self.path)

            if self.headers['Content-Type'] != 'application/json':
                self.send_response(415)
                self.end_headers()
                return

            if len(splittedUrl) == 2 and splittedUrl[0] == 'readers':
                response = deleteReaderById(splittedUrl[1])
            elif len(splittedUrl) == 2 and splittedUrl[0] == 'books':
                response = deleteBookById(splittedUrl[1])
            elif len(splittedUrl) == 4 and splittedUrl[0] == 'readers' and splittedUrl[2] == 'books':
                response = deleteReaderBookById(splittedUrl[1], splittedUrl[3])
            elif len(splittedUrl) == 2 and splittedUrl[0] == 'authors':
                response = deleteAuthorById(splittedUrl[1])
            
            if response == 400:
                self.send_response(400)
                self.end_headers()
                return
            if not response:
                self.send_response(404)
                self.end_headers()
                return
            else:
                self.send_response(204)
                self.end_headers()
                commitChanges()
                return
        except:
            self.send_response(500)
            self.end_headers()
            return



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

httpd = ThreadedHTTPServer(('0.0.0.0', 8000), RestHTTPRequestHandler)
httpd.serve_forever()