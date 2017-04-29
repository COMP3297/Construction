from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^$', views.featured, name='featured'),
    url(r'^games/(?P<game_id>\d+)/$', views.games, name='games'),
    url(r'^purchase/(?P<game_id>\d+)/$', views.purchase, name='purchase'),
    url(r'^deleteGame/(?P<game_id>\d+)/(?P<cart_id>\d+)/$', views.deleteGame, name='deleteGame'),
    url(r'^purchaseAll$', views.purchaseAll, name='purchaseAll'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^browse/(?P<tag_id>\d+)/$', views.browseBy, name='browseBy'),
    url(r'^tag/(?P<game_id>\d+)/$', views.tagedit, name='tagedit'),
    url(r'^add_tag/(?P<game_id>\d+)/$',views.addtag, name = 'addtag'),
    url(r'^login/$', auth_views.login, name='login'),      #https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    ]

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'


urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns+=staticfiles_urlpatterns()
