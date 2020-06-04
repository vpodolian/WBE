import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm, RenewBookModelForm
from .models import Book, Author, BookInstance, Genre

# Вписал отдельно переменную, чтоб сослаться на нее в тестах
init_author_date_of_death = datetime.date.today() + datetime.timedelta(days=1)


# @permission_required('catalog.can_mark_returned')
# @login_required
def index(request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()


    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits,
                 },
    )


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, pk):
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")



        return render(
            request,
            'catalog/book_detail.html',
            context={'book': book_id, }
        )


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, pk):

        author_id = get_object_or_404(Book, pk=pk)

        return render(
            request,
            'catalog/author_detail.html',
            context={'author': author_id, }
        )


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):

    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_librarian.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)


    if request.method == 'POST':

        form = RenewBookModelForm(request.POST)


        if form.is_valid():

            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': init_author_date_of_death, }

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_edit_author'
    model = Book
    fields = '__all__'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_edit_author'
    model = Book
    fields = '__all__'


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    success_url = reverse_lazy('books')


