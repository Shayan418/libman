from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    path("addbook", views.addBook, name="addBook"),
    path("book/<str:bookid>", views.viewBook, name="viewBook"),
    path("book/issueBook/", views.issueBook, name="issueBook"),
    path("book/returnBook/", views.returnBook, name="returnBook"),
]