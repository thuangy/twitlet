from django.contrib import admin
from .models import Choice, Question, UserProfile, Tweetlet

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]

"""class TweetletAdmin(admin.ModelAdmin):
    list_display = ['message', 'pub_date', 'user']


    def save_model(self, request, tweetlet, form, change):
          tweetlet.user = request.user.username
          tweetlet.save()"""

admin.site.register(UserProfile)
admin.site.register(Tweetlet)
admin.site.register(Question, QuestionAdmin)
