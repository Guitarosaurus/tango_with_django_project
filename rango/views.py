from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

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

    # Call the helper function to handle the cookies
    visitor_cookie_handler(request)

    # Obtain our Response object early so we can add cookie information.
    response = render(request, 'rango/index.html', context=context_dict)
    # Return response back to the user, updating any cookies that need changed.
    return response

    # return render(request, 'rango/index.html', context=context_dict)

def about(request):
    visitor_cookie_handler(request)

    context_dict = {}
    context_dict['visits'] = request.session['visits']
    
    return render(request, 'rango/about.html', context=context_dict)

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

@login_required
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

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # Cannot add page to a non-existent Category
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

def register(request):
    # Boolean value for telling the template whether reg. was successful.
    # Initially False, Code changes value to True when reg. successful.
    registered = False

    # If HTTP post we are interested in processing form data
    if request.method == 'POST':
        # Grab info from raw form info.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST) 

        # If both forms valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save user's form data to database
            user = user_form.save()

            # hash pasword with set_password method
            # Once hashed can update User Obj.
            user.set_password(user.password)
            user.save()

            # Now looking at UserProfile Instance
            # Since we need to set user attrib. we set commit = False. 
            # Delays saving the model until ready - avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did user provide profile picture? If so get from form and put in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now save UserProfile model instance
            profile.save()

            # update variable to indicate that template registration was successful
            registered = True
        else:
            # Invalid form/forms - mistakes or something else
            # print problems to terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so render form using two ModelForm Instances
        # Forms will be blank ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render template depending on context
    return render(request, 'rango/register.html', 
                  context={'user_form' : user_form,
                           'profile_form': profile_form,
                           'registered': registered})

def user_login(request):
    # if request is HTTP POST, try to pull out the relevant info.
    if request.method == 'POST':
        # gather the username and password provided by user.
        # info obtained from login frame
        # We use request.POST.get('<variable') as it return None if the value does not exist
        username = request.POST.get('username')
        password = request.POST.get('password') 

        # Use DJango's machinery to attempt to see if username/password
        # combination is valid - a User object is returned if it is
        user = authenticate(username=username, password=password)

        # if we have User obj, the details are correct.
        # if None, no user with matching credentials was found
        if user:
            # Is the account active? Could have been disabled.
            if user.is_active:
                # If account is valid and active, we can log user in.
                # We'll send user back to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # inactive account was used- no logging in
                return HttpResponse("Your Rango account is disabled.")
        else:
            # bad login details were provided. So can't log user in
            print(f"invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
        
    # Request is not HTTP POST, so display login form.
    # Scenario would most likely be a HTTP GET
    else:
        # no context variables to pass template sys, hence blank dict. obj.
        return render(request, 'rango/login.html')
    
# Use the login_required() decorator to ensure only those loggin in can access the view
@login_required
def user_logout(request):
    # Since we know user is logged in, we can just log them out.
    logout(request)
    # Take user back to homepage
    return redirect(reverse('rango:index'))

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# Cookies helper function
def visitor_cookie_handler(request):
    # Get no. of visits to the site
    # We use COOKIES.get() funct. to obtain visits cookiee
    # If cookie exists, value returned is casted to an int
    # if cookie doesn't exit, then default value of 1 is used
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # If its been more than a day since last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count 
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val