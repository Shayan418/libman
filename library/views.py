import json
import urllib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from datetime import date, datetime, timedelta, timezone


from .models import User, Books, record

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        print(user)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "library/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "library/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "library/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "library/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "library/register.html")
    
    
def index(request):
    
    return render(request, "library/index.html",{
        'books': Books.objects.all()
    })
    

@login_required
def addBook(request):
    if request.user.is_superuser:
        
        if request.method == "POST":
            
            if('submit_button' in request.POST):
                url = f"https://www.googleapis.com/books/v1/volumes/{request.POST['submit_button']}"
                serialized_data = urllib.request.urlopen(url).read()
                data = json.loads(serialized_data)
                book = Books()
                book.bookid = (data['id'])
                book.title = (data['volumeInfo']['title'])
                book.description = (data['volumeInfo']['description'])
                book.authors = (''.join(data['volumeInfo']['authors']))
                book.isbn = (data['volumeInfo']['industryIdentifiers'][0]['identifier'])
                book.thumbnail = data['volumeInfo']['imageLinks']['smallThumbnail']
                
                try:
                    book.save()
                    pass
                except:
                    messages.info(request, "book already exists")
                    return render(request, 'library/addbook.html')
                
                messages.info(request, f"Added to library - {book.title}")
                return render(request, 'library/addbook.html')
            
            searchTerm = request.POST['search'].replace(' ','+')
            url = f"https://www.googleapis.com/books/v1/volumes?q={searchTerm}"
            serialized_data = urllib.request.urlopen(url).read()
            data = json.loads(serialized_data)
            items = data['items'][0]
            payload_s = []
           
            for index, book in enumerate(data['items']):
                try: 
                    dict = {}
                    dict['id'] = book['id']
                    dict['title'] = book['volumeInfo']['title']
                    dict['description'] = book['volumeInfo']['description']
                    dict['authors'] = ''.join(book['volumeInfo']['authors'])
                    dict['isbn'] = book['volumeInfo']['industryIdentifiers'][0]['identifier']
                except: 
                    continue
                payload_s.append(dict)
            
    
            print(payload_s[0]['title'])
            return render(request, 'library/addbooklist.html', 
                          {
                              'books': payload_s, 
                          })

            
        return render(request, 'library/addbook.html')
    
def viewBook(request, bookid):
    book = Books.objects.get(bookid=bookid)
    returndate = None
    timeToReturn = None
    fine = None
    try:
        isIssued = record.objects.get(user=request.user, book=book)
        print((isIssued.timeCreated))
        returnDelta = timedelta(days=14)
        print(returnDelta)
        timeToReturn = (isIssued.timeCreated + returnDelta) - datetime.now(timezone.utc)
        returndate = isIssued.timeCreated + returnDelta
        print(timeToReturn.days)
        if(timeToReturn.days < 0):
            if (timeToReturn.days <= 5):
                fine = 20
            elif(timeToReturn.days >5 and timeToReturn.days <= 15):
                fine = 50
            elif(timeToReturn.days > 15):
                fine = 200
        
    except:
        isIssued = None
    return render(request, "library/book.html",{
        'book': book,
        'isIssued': isIssued,
        'timeToReturn' : timeToReturn,
        'returndate': returndate,
        'fine': fine,
    })

@login_required
def issueBook(request):
    print('lol')
    if request.method == "POST":
        if "bookid" in request.POST:
            requestBook = Books.objects.get(bookid = request.POST['bookid'])
            if not requestBook:
                pass
            else:
                newRecord = record()
                newRecord.user = request.user
                newRecord.book = requestBook
                try:
                    newRecord.validate_unique()
                    newRecord.save()
                    messages.info(request, "Book Issued")
                except :
                    messages.info(request, "Book Already Issued")
                return HttpResponseRedirect(reverse('viewBook', kwargs={'bookid': request.POST['bookid']}))

@login_required
def returnBook(request):
    if request.method == "POST":
        if "bookid" in request.POST:
            print(request.POST['bookid'])
            requestBook = Books.objects.get(bookid = request.POST['bookid'])
            requestRecord = record.objects.get(book = requestBook, user = request.user)
            requestRecord.delete()
            messages.info(request, "Book Returned")
            return HttpResponseRedirect(reverse('viewBook', kwargs={'bookid': request.POST['bookid']}))