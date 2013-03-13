from django.core.urlresolvers import reverse
from django.views.generic import (DetailView, RedirectView)
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin

from bluusites.models import BluuSite


class DashboardView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        sites = self.request.user.get_sites()
        if sites.exists():
            self.url = reverse('bluusite_dashboard', kwargs={'site_slug':sites[0].slug})

        return super(DashboardView, self).get_redirect_url(*args, **kwargs)

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteDashboardView, self).dispatch(*args, **kwargs)

