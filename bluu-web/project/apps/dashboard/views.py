from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import (DetailView, RedirectView, TemplateView)
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django import http

from guardian.decorators import permission_required
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin

from bluusites.models import BluuSite


class DashboardView(TemplateView, RedirectView):
    template_name = "dashboard/dashboard.html"

    def get_redirect_url(self, *args, **kwargs):
        last_site = self.request.session.get('last_dashboard_site', None)
        if last_site is not None:
            try:
                BluuSite.objects.get(slug=last_site)
            except:
                last_site = None

        if not last_site:
            sites = self.request.user.get_sites()
            if sites.exists():
                last_site = sites[0].slug

        self.url = reverse('bluusite_dashboard', 
                           kwargs={'site_slug': last_site})

        return super(DashboardView, self).get_redirect_url(*args, **kwargs)

    def get(self, request, *args, **kwargs):

        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return http.HttpResponsePermanentRedirect(url)
            else:
                return http.HttpResponseRedirect(url)
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context) 

        return http.HttpResponseGone() 

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)


class BluuSiteDashboardView(DetailView):
    template_name = "dashboard/dashboard.html"
    model = BluuSite
    slug_url_kwarg = 'site_slug'

    def get_context_data(self, *args, **kwargs):
        kwargs['sites'] = self.request.user.get_sites()
        return super(BluuSiteDashboardView, self).get_context_data(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.session['last_dashboard_site'] = self.object.slug
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context) 


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteDashboardView, self).dispatch(*args, **kwargs)

