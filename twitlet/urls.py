from django.conf.urls import url

from . import views

from django.conf import settings

from django.conf.urls.static import static

app_name = 'twitlet'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^make_tweetlet/$', views.make_tweetlet, name='make_tweetlet'), # NEW MAPPING!
    url(r'^my_tweetlets/$', views.view_tweetlets.as_view(), name='view_tweetlets'), # NEW MAPPING!
    #url(r'^tweetlet/(?P<tweetlet_name_slug>[\w\-]+)/$', views.category, name='category'),)
	#url(r'^static/(?P.*)$', {'document_root': settings.STATIC_ROOT}, prefix='django.views.static.serve'),
]

"""urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)"""

#urlpatterns += staticfiles_urlpatterns()

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
