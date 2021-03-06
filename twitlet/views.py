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

import random

#curr_user = ""
class IndexView(generic.ListView):
    latest_tweetlet_list = Question.objects.order_by('-pub_date')[:10]
    template_name = 'twitlet/index.html'
    #context_object_name = 'latest_question_list'
    context_object_name = 'latest_tweetlet_list'

    #user_tweetlets = Question.objects.filter(user = request.user)

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        """return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]"""
        return Tweetlet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]
        #return Tweetlet.objects.filter(user=self.request.user)

    #user_tweetlets = get_queryset


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

#@login_required
class view_tweetlets(generic.ListView):
    model = Tweetlet
    #user_tweetlets = Tweetlet.objects.order_by('-pub_date')[:10]
    template_name = 'twitlet/my_tweetlets.html'
    context_object_name = 'user_tweetlets'
    def get_queryset(self):
        #return Tweetlet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]
        return Tweetlet.objects.filter(user=self.request.user).order_by('-pub_date')


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

def make_tweetlet(request):
    # A HTTP POST?



    new_tweetlet = bot_tweetlet(request)
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
            if not request.user.username:
                temp.user = "Anonymous"
            else:
                temp.user = request.user.username
            temp = temp.save()

            # Now call the index() view.
            # The user will be shown the homepage.
            return HttpResponseRedirect('/twitlet/')
            #return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    elif request.is_ajax:
        form = TweetletForm()
        new_tweetlet = bot_tweetlet(request)

    else:
        # If the request was not a POST, display the form to enter details.
        form = TweetletForm()

    """if request.POST.get('bot_tweetlet'):
        print("button clicked!")
        form.message = new_tweetlet
    else:
        print("NO CLICK")"""
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    #return index(request)
    return render(request, 'twitlet/make_tweetlet.html', {'form': form, 'new_tweetlet': new_tweetlet, 'clicked': False})


def bot_tweetlet(request):
    if request.user.username:
        tweetlets = Tweetlet.objects.filter(user=request.user)
    else:
        tweetlets = Tweetlet.objects.all()

    if (tweetlets.exists()):
        if len(tweetlets) > 3:
            most_used = {}

            greetings = {}
            nouns = {}
            verbs = {}
            extras = {}


            for t in tweetlets:
                wordnum = 0
                message_length = len(t.message.split())
                for word in t.message.split(" "):
                    if word.isdigit():
                        wordnum += 1
                        continue

                    if not word[:-1].isalnum():
                        wordnum += 1
                        continue

                    if wordnum == 0:
                        if not word[-1].isalpha():
                            if word in greetings:
                                greetings[word] += 1
                            else:
                                greetings[word] = 1
                        else:
                            cword = word.lower()
                            if cword in nouns:
                                nouns[cword] += 1
                            else:
                                nouns[cword] = 1
                    else:
                        if word[0].isupper():
                            if word in nouns:
                                nouns[word] += 1
                            else:
                                nouns[word] = 1

                    if wordnum == 1:
                        if word in verbs:
                            verbs[word] += 1
                        else:
                            verbs[word] = 1

                    if wordnum == message_length - 1:
                        if word in extras:
                            extras[word] += 1
                        else:
                            extras[word] = 1





                    if word in most_used:
                        most_used[word] += 1
                    else:
                        most_used[word] = 1



                    wordnum += 1

            count = 0
            new_tweetlet = ""
            """for w in sorted(most_used, key=most_used.get, reverse=True):
                if (w.isdigit()):
                    continue
                if (count == 0):
                    if (not w[0].isupper()):
                        new_tweetlet += w[0].upper()
                        new_tweetlet += w[1:]
                    else:
                        new_tweetlet += w
                elif (count <= 5):
                    new_tweetlet += w
                if (not new_tweetlet[-1].isalpha()):
                    new_tweetlet = new_tweetlet[:-1]
                new_tweetlet += " "
                count += 1"""

            if len(list(greetings.keys())) > 0:
                greeting = random.choice(list(greetings.keys()))
                print()
                if not greeting[0].isupper():
                    new_tweetlet += greeting[0].upper()
                    new_tweetlet += greeting[1:]
                else:
                    new_tweetlet += greeting

                new_tweetlet += " "

            if len(list(nouns.keys())) > 0:
                new_tweetlet += random.choice(list(nouns.keys()))

                new_tweetlet += " "

            if len(list(verbs.keys())) > 0:
                new_tweetlet += random.choice(list(verbs.keys()))

                new_tweetlet += " "

            #new_tweetlet += random.choice(["the", "a"])

            #new_tweetlet += " "

            if len(list(extras.keys())) > 0:
                new_tweetlet += random.choice(list(extras.keys()))

            print(new_tweetlet)
            return new_tweetlet
        else:
            return "Try something unexpected!"
    #else:
        #return "Try something unexpected!"

def change_message(form, message):
    form.fields["message"].initial = message



"""@login_required
class view_tweetlets(generic.DetailView):
    model = Tweetlet
    #user_tweetlets = Tweetlet.objects.order_by('-pub_date')[:10]
    template_name = 'twitlet/my_tweetlets.html'
    context_object_name = 'user_tweetlets'
    def get_queryset(self):
        #return Tweetlet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]
        return Tweetlet.objects.filter(user=self.request.user)

def view_tweetlets(request):
    return Tweetlet.objects.filter(user=request.user)"""



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


