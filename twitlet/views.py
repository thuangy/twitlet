from django.shortcuts import get_object_or_404, render

from django import forms

from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Tweetlet, UserProfile
from .forms import UserForm, UserProfileForm, TweetletForm

#curr_user = ""
class IndexView(generic.ListView):
    latest_tweetlet_list = Question.objects.order_by('-pub_date')[:10]
    template_name = 'twitlet/index.html'
    #context_object_name = 'latest_question_list'
    context_object_name = 'latest_tweetlet_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        """return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]"""
        return Tweetlet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'twitlet/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'twitlet/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'twitlet/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('twitlet:results', args=(question.id,)))


def register(request):
    # Like before, get the request's context.
    #context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            print("valid")
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            """if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']"""

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    """return render_to_response(
            'twitlet/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)"""
    return render(request,
            'twitlet/register.html',
            {'user_form': user_form, 'registered': registered})


def user_login(request):
    # Like before, obtain the context for the user's request.
    #context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                #curr_user = username
                return HttpResponseRedirect('/twitlet/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Twitlet account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        #return render_to_response('rango/login.html', {}, context)
        return render(request, 'twitlet/login.html', {})

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/twitlet/')

@login_required
def make_tweetlet(request):
    # A HTTP POST?
    if request.method == 'POST':
        #form = TweetletForm(data=request.POST, initial={'user': request.user.username})
        form = TweetletForm(data=request.POST)
        #form = temp.save(commit=False)
        #form.user = UserProfile.objects.get(user=request.user).username
        #form.user = request.user.username
        #form.fields['user'].initial = request.user.username
        #form.user = forms.CharField(widget=forms.HiddenInput(), initial=curr_user)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            temp = form.save(commit=True)
            temp.user = request.user.username
            temp = temp.save()

            # Now call the index() view.
            # The user will be shown the homepage.
            return HttpResponseRedirect('/twitlet/')
            #return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = TweetletForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    #return index(request)
    return render(request, 'twitlet/make_tweetlet.html', {'form': form})


#def index(request):
    """latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'twitlet/index.html', context)"""

    #latest_tweetlet_list = Question.objects.order_by('-pub_date')[:10]
    #context = {'latest_tweetlet_list': latest_tweetlet_list}
    #return render(request, 'twitlet/index.html', context)

"""def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})"""


