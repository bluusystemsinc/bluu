from random import choice
from string import letters
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.messages.api import get_messages
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 TemplateView, DeleteView, ListView
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from registration.backends import get_backend
from accounts.forms import ProfileForm, AccountForm, BluuUserForm

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from accounts.models import Company, Site, BluuUser
from accounts.forms import CompanyForm, SiteForm
#from forms import UserForm, UserProfileForm
from django.contrib.auth import get_user_model

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user, assign


def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None):

    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        data = request.POST.copy() # so we can manipulate data
        form = form_class(data, files=request.FILES)
        if form.is_valid():
            # random username
            form.cleaned_data['username'] = ''.join([choice(letters) for i in xrange(30)])
            new_user = backend.register(request, **form.cleaned_data)
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(request, new_user)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)


class AccountUpdateView(UpdateView):
    template_name='accounts/account_change_form.html'
    form_class = AccountForm

    def get_success_url(self):
        messages.success(self.request, _('Account changed!'))
        return reverse('account_edit')

    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)

class AccountDeleteView(DeleteView):
    model = get_user_model()
    template_name='accounts/account_confirm_delete.html'
    context_object_name='account'
    success_url = '/'

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, _('User account removed!'))
        return '/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccountDeleteView, self).dispatch(*args, **kwargs)


class UserProfileCreateView(CreateView):
    template_name = 'profiles/create_profile.html'
    #model = UserProfile

    def dispatch(self, request, *args, **kwargs):
        try:
            profile_obj = request.user.get_profile()
            return HttpResponseRedirect(reverse('profiles_edit_profile'))
        except ObjectDoesNotExist:
            pass
        return super(UserProfileCreateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        kwargs = self.get_form_kwargs()
        kwargs['initial'].update({'email':self.request.user.email})
        return form_class(**kwargs)

    def get_success_url(self):
        return reverse('profiles_edit_profile')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, _('User Profile added!'))
        return HttpResponseRedirect(self.get_success_url())

    def get_form_class(self):
        return ProfileForm


class UserProfileUpdateView(UpdateView):
    template_name = 'profiles/edit_profile.html'
    #model = UserProfile

    def dispatch(self, request, *args, **kwargs):
        try:
            profile_obj = request.user.get_profile()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('profiles_create_profile'))
        kwargs['pk'] = profile_obj.pk
        return super(UserProfileUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('profiles_edit_profile')

    def form_valid(self, form):
        messages.success(self.request, _('User Profile changed!'))
        return super(UserProfileUpdateView, self).form_valid(form)

    def get_form_class(self):
        return ProfileForm


class CompanyListView(ListView):
    model = Company
    template_name = "accounts/company_list.html"

    def get_queryset(self):
        if self.request.user.has_perm('accounts.view_company'):
            return super(CompanyListView, self).get_queryset()
        return get_objects_for_user(self.request.user, 'accounts.view_company')

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.browse_companies'))
    def dispatch(self, *args, **kwargs):
        return super(CompanyListView, self).dispatch(*args, **kwargs)


class CompanyCreateView(CreateView):
    model = Company
    template_name = "accounts/company_create.html"
    form_class = CompanyForm

    def form_valid(self, form):
        response = super(CompanyCreateView, self).form_valid(form)
        #_create_groups_for_company(self.object)
        messages.success(self.request, _('Company added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.add_company'))
    def dispatch(self, *args, **kwargs):
        return super(CompanyCreateView, self).dispatch(*args, **kwargs)


class CompanyUpdateView(UpdateView):
    model = Company
    template_name = "accounts/company_update.html"
    form_class = CompanyForm

    def form_valid(self, form):
        response = super(CompanyUpdateView, self).form_valid(form)
        messages.success(self.request, _('Company changed'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('accounts.change_company',
            (Company, 'pk', 'pk'), accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyUpdateView, self).dispatch(*args, **kwargs)


@permission_required_or_403('accounts.delete_company')
def company_delete(request, pk):
    obj = get_object_or_404(Company, pk=pk)
    obj.delete()
    messages.success(request, _('Company deleted'))
    return redirect('company-list')


class CompanyDeleteView(DeleteView):
    model = Company
    template_name = "accounts/company_delete.html"

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('accounts.delete_company',
            (Company, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(CompanyDeleteView, self).dispatch(*args, **kwargs)


class CompanyAccessManagementView(DetailView):
    model = Company
    template_name = "accounts/company_access.html"

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('accounts.change_company',
            (Company, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(CompanyAccessManagementView, self).\
                dispatch(*args, **kwargs)


class CompanySitesManagementView(DetailView):
    model = Company
    template_name = "accounts/company_sites_management.html"

    def get_context_data(self, **kwargs):
        kwargs['form'] = SiteForm()
        return super(CompanySitesManagementView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.browse_sites'))
    def dispatch(self, *args, **kwargs):
        return super(CompanySitesManagementView, self).dispatch(*args, **kwargs)


class SiteListView(ListView):
    model = Site
    template_name = "accounts/site_list.html"

    def get_queryset(self):
        if self.request.user.has_perm('accounts.view_site'):
            return super(SiteListView, self).get_queryset()
        return get_objects_for_user(self.request.user, 'accounts.view_site')

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.browse_sites'))
    def dispatch(self, *args, **kwargs):
        return super(SiteListView, self).dispatch(*args, **kwargs)


class SiteCreateView(CreateView):
    model = Site
    template_name = "accounts/site_create.html"
    form_class = SiteForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SiteCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SiteCreateView, self).form_valid(form)
        #_create_groups_for_site(self.object)
        messages.success(self.request, _('Site added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.add_site'))
    def dispatch(self, *args, **kwargs):
        return super(SiteCreateView, self).dispatch(*args, **kwargs)


class SiteUpdateView(UpdateView):
    model = Site
    template_name = "accounts/site_update.html"
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
    @method_decorator(permission_required('accounts.change_site'))
    def dispatch(self, *args, **kwargs):
        return super(SiteUpdateView, self).dispatch(*args, **kwargs)


class SiteAccessManagementView(DetailView):
    model = Site
    template_name = "accounts/site_access.html"

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('accounts.change_site',
            (Site, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(SiteAccessManagementView, self).\
                dispatch(*args, **kwargs)


@permission_required('accounts.delete_site')
def site_delete(request, pk):
    obj = get_object_or_404(Site, pk=pk)
    obj.delete()
    messages.success(request, _('Site deleted'))
    return redirect('site-list')


class SiteDeleteView(DeleteView):
    model = Site
    template_name = "accounts/site_delete.html"

    @method_decorator(login_required)
    @method_decorator(permission_required('accounts.delete_site'))
    def dispatch(self, *args, **kwargs):
        return super(SiteDeleteView, self).dispatch(*args, **kwargs)


class SiteUserListView(ListView):
    model = BluuUser
    template_name = "accounts/siteuser_list.html"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        self.site = get_object_or_404(Site, pk=pk)
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
    template_name = "accounts/siteuser_create.html"
    form_class = BluuUserForm

    def get_success_url(self):
        pk = self.kwargs.get('pk', None)
        return reverse_lazy('site-users', args=(pk,))

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
        self.site = get_object_or_404(Site, pk=pk)

        return super(SiteUserCreateView, self).dispatch(*args, **kwargs)


class SiteUserUpdateView(UpdateView):
    model = BluuUser
    template_name = "accounts/siteuser_update.html"
    form_class = BluuUserForm
    pk_url_kwarg = 'upk'

    def get_success_url(self):
        pk = self.kwargs.get('pk', None)
        return reverse_lazy('site-users', args=(pk,))

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
        self.site = get_object_or_404(Site, pk=pk)
        return super(SiteUserUpdateView, self).dispatch(*args, **kwargs)


@permission_required('accounts.delete_bluuuser')
def site_user_delete(request, pk, site_id):
    obj = get_object_or_404(BluuUser, pk=pk)
    site = get_object_or_404(Site, pk=site_id)
    # TODO: validate if user can delete this user!!!

    obj.delete()
    messages.success(request, _('Bluuuser deleted'))
    return redirect('site-users', pk=site.pk)



