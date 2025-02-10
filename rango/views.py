from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    # Query the databse for a list of all categories currently stored
    # order by number of likes indesc. order
    # Retrieve top 5 only -- or all if less than 5
    # place the list in oout context_dict dict
    # that will be passed to template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create context dict. whch we can pass to template rendering engine
    context_dict = {}

    try:
        # Try find category name slug with given name
        # If it doesn't exists then the .get() method raises a DoesNotExist exception
        # The .get() method returns one model instance or excpetion
        category = Category.objects.get(slug = category_name_slug)

        # Retrieve all associated pages, filter() returns a list of page obj. or empty list
        pages = Page.objects.filter(category=category)

        # Add result list to template context under name pages
        context_dict['pages'] = pages

        # Add category object from database to the context dict. 
        # We use this in the template to verify the category exists
        context_dict['category'] = category

    except Category.DoesNotExist:
        # Get here if specified category doesnt exist
        # Don't do anything - template will display the "no category" message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render the response and return it to the client
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form  = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # have we been provided with a valid form
        if form.is_valid():
            # Save name to category 
            form.save(commit=True)

            # Then redirect user back to index view
            return redirect('/rango/')
        else:
            # Supplied form contained errors - just print to terminal
            print(form.errors)
        
    # Will handle the bad form, new form or no form in suplied cases
    # Render form with error messages - if any
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # Cannot add page to a non-existant Category
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs = {'category_name_slug':
                                                  category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context=context_dict)