from django.conf.urls import patterns, include, url
#from shop import urls as shop_urls
#from stables_shop.views import NoShippingAddressCheckoutSelectionView, InfoView, ParticipationPaymentRedirect
#from stables_shop.views import ParticipationPayment, ParticipationPaymentSuccess
#from stables_shop.views import ParticipationPaymentNotify, ParticipationPaymentFailure

#from stables_shop.views import ShopRedirectView
from django.http import HttpResponse
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from .forms import EmailAuthenticationForm

admin.autodiscover()

#from rest_framework import routers
#from stables.api import ParticipationViewSet

#router = routers.DefaultRouter()
#router.register(r'participations', ParticipationViewSet)

urlpatterns = patterns('',
    # Examples:
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'authentication_form': EmailAuthenticationForm }, name='login'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    #url(r'^api-help/', 'views.api', name='api-help'),
    #url(r'^shopper/pay/(?P<id>\d+)$', ParticipationPaymentRedirect.as_view(), name='shop-pay'),
    #rl(r'^shopper/pay/(?P<hash>\w+)$', ParticipationPayment.as_view(), name='shop-pay'),
    #rl(r'^shopper/pay/(?P<hash>\w+)/success$', ParticipationPaymentSuccess.as_view(), name='shop-pay-success'),
    #rl(r'^shopper/pay/(?P<hash>\w+)/notify$', ParticipationPaymentNotify.as_view(), name='shop-pay-notify'),
    #rl(r'^shopper/pay/(?P<hash>\w+)/failure$', ParticipationPaymentFailure.as_view(), name='shop-pay-failure'),
    #rl(r'^shopper/checkout/$', NoShippingAddressCheckoutSelectionView.as_view()),
    #rl(r'^shopper/info/$', InfoView.as_view(), name='shop-info'),
    #url(r'^shopper/', include(shop_urls)),
    #url(r'^shop/$', ShopRedirectView.as_view(), name='shop-in'),
    url(r'^s/', include('stables_shop.urls')),
    url(r'^cal/', include('schedule.urls')),
    url(r'^', include('stables.urls')),

    #url(r'^comments/', include('fluent_comments.urls')),
    # url(r'^openshift/', include('openshift.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url('^admin/', include(admin.site.urls)),

    #url(r'^api/', include(router.urls)),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

from django.conf import settings
urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    'document_root': settings.MEDIA_ROOT}))
