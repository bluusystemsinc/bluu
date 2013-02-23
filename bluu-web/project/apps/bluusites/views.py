from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 DeleteView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin

from grontextual.shortcuts import get_objects_for_user
from accounts.forms import BluuUserForm
from accounts.models import BluuUser
from .forms import SiteInvitationForm
from .models import BluuSite
from .forms import SiteForm


class SiteListView(TemplateView):
    template_name = "bluusites/site_list.html"

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.browse_bluusites', 
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        sites = self.request.user.can_see_sites(perm='bluusites.change_bluusite')
        site = sites.get('bluusite', None)
        if site is not None:
            return redirect('site_edit', pk=site.pk)

        return super(SiteListView, self).dispatch(*args, **kwargs)


class SiteCreateView(CreateView):
    model = BluuSite
    template_name = "bluusites/site_create.html"
    form_class = SiteForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SiteCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SiteCreateView, self).form_valid(form)
        messages.success(self.request, _('Site added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.add_bluusite'))
    def dispatch(self, *args, **kwargs):
        return super(SiteCreateView, self).dispatch(*args, **kwargs)


class SiteUpdateView(UpdateView):
    model = BluuSite
    template_name = "bluusites/site_update.html"
    form_class = SiteForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SiteUpdateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SiteUpdateView, self).form_valid(form)
        messages.success(self.request, _('Site changed'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.change_bluusite',
                                          (BluuSite, 'pk', 'pk'),
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(SiteUpdateView, self).dispatch(*args, **kwargs)


class SiteAccessListView(TemplateView):
    template_name = "bluusites/site_access_list.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk', None)
        return get_object_or_404(BluuSite, pk=pk)

    def get_context_data(self, **kwargs):
        bluusite = self.get_object()
        invitation_form = SiteInvitationForm()
        return {
            'params': kwargs,
            'bluusite': bluusite,
            'invitation_form': invitation_form
        }

    @method_decorator(permission_required('bluusites.change_bluusite',
                                (BluuSite, 'pk', 'pk'),
                                accept_global_perms=True))
    @method_decorator(permission_required('bluusites.browse_bluusiteaccesses',
                                          (BluuSite, 'pk', 'pk'),
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(SiteAccessListView, self).dispatch(*args, **kwargs)


@permission_required('bluusites.delete_bluusite', (BluuSite, 'pk', 'pk'))
def site_delete(request, pk):
    obj = get_object_or_404(BluuSite, pk=pk)
    obj.delete()
    messages.success(request, _('Site deleted'))
    return redirect('site_list')


#class SiteDeleteView(DeleteView):
#    model = BluuSite
#    template_name = "bluusites/site_delete.html"
#
#    @method_decorator(login_required)
#    @method_decorator(permission_required('bluusites.delete_bluusite'))
#    def dispatch(self, *args, **kwargs):
#        return super(SiteDeleteView, self).dispatch(*args, **kwargs)
#

class SiteUserListView(ListView):
    model = BluuUser
    template_name = "bluusites/siteuser_list.html"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        self.site = get_object_or_404(BluuSite, pk=pk)
        return super(SiteUserListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model._default_manager.filter(site=self.site)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SiteUserListView, self).get_context_data(**kwargs)
        context['site'] = self.site
        return context

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.browse_bluuusers'))
    def dispatch(self, *args, **kwargs):
        return super(SiteUserListView, self).dispatch(*args, **kwargs)


class SiteUserCreateView(CreateView):
    model = BluuUser
    template_name = "bluusites/siteuser_create.html"
    form_class = BluuUserForm

    def get_success_url(self):
        pk = self.kwargs.get('pk', None)
        return reverse_lazy('site_users', args=(pk,))

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(self.request.user, self.site, **self.get_form_kwargs())

    def form_valid(self, form):
        response = super(SiteUserCreateView, self).form_valid(form)
        messages.success(self.request, _('User added'))
        return response

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(SiteUserCreateView, self).get_context_data(**kwargs)
        context['site'] = self.site
        return context

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.add_bluuusers'))
    def dispatch(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        self.site = get_object_or_404(BluuSite, pk=pk)

        return super(SiteUserCreateView, self).dispatch(*args, **kwargs)


class SiteUserUpdateView(UpdateView):
    model = BluuUser
    template_name = "bluusites/siteuser_update.html"
    form_class = BluuUserForm
    pk_url_kwarg = 'upk'

    def get_success_url(self):
        pk = self.kwargs.get('pk', None)
        return reverse_lazy('site_users', args=(pk,))

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(self.request.user, self.site, **self.get_form_kwargs())

    def form_valid(self, form):
        response = super(SiteUserUpdateView, self).form_valid(form)
        messages.success(self.request, _('User changed'))
        return response

    def get_context_data(self, **kwargs):
        context = super(SiteUserUpdateView, self).get_context_data(**kwargs)
        context['site'] = self.site
        return context

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.change_bluuuser'))
    def dispatch(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        self.site = get_object_or_404(BluuSite, pk=pk)
        return super(SiteUserUpdateView, self).dispatch(*args, **kwargs)


@permission_required('accounts.delete_bluuuser')
def site_user_delete(request, pk, site_id):
    obj = get_object_or_404(BluuUser, pk=pk)
    site = get_object_or_404(BluuSite, pk=site_id)
    # TODO: validate if user can delete this user!!!

    obj.delete()
    messages.success(request, _('Bluuuser deleted'))
    return redirect('site_users', pk=site.pk)

