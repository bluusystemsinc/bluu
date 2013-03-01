from random import choice
from string import letters
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views.generic import (UpdateView, CreateView,
                                 DeleteView, ListView, DetailView)
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user, assign
from registration.backends import get_backend
from braces.views import LoginRequiredMixin
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from braces.views import PermissionRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from .forms import AccountForm, BluuUserForm
from .models import BluuUser


class BluuUserListView(GPermissionRequiredMixin, ListView):
    model = BluuUser
    template_name = "accounts/user_list.html"
    permission_required = 'accounts.browse_bluuusers'

    def get_queryset(self):
        return self.model.app_users.all()
        # if user has a global permission view_bluuuser then show all users
        # except anonymous and admins
        #if self.request.user.has_perm('accounts.view_bluuuser'):
        # else show ony user's he has granted direct permission
        #return get_objects_for_user(self.request.user, 'accounts.view_bluuuser')

    #@method_decorator(login_required)
    #@method_decorator(permission_required('accounts.browse_bluuusers'))
    #def dispatch(self, *args, **kwargs):
    #    return super(BluuUserListView, self).dispatch(*args, **kwargs)


class BluuUserListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = 'accounts.browse_bluuusers'
    order_columns = ['id', BluuUser.USERNAME_FIELD, 'last_name', 'email',\
                     'is_active']

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        return BluuUser.app_users.all()

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(username__istartswith=q) |\
                             Q(first_name__istartswith=q) |\
                             Q(last_name__istartswith=q) |\
                             Q(email__istartswith=q)
                             )
        return qs
 
    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for item in qs:
            actions = '<a href="{0}">{1}</a> <a href="{2}" onclick="return confirm(\'{3}\')">{4}</a>'.format(
                    reverse('bluuuser_edit', kwargs={'username': item.username}), _('Edit'),
                    reverse('bluuuser_delete', kwargs={'username': item.username}), 
                    _('Are you sure you want delete this user?'),
                    _('Delete'))

            json_data.append(
                {
                    "no": no,
                    "username": item.get_username(),
                    "full_name": item.get_full_name(),
                    "email": item.email,
                    "is_active": item.is_active and _('active') or _('inactive'),
                    "actions": actions,
                }
            )
            no += 1
        return json_data


class BluuUserCreateView(PermissionRequiredMixin, CreateView):
    model = BluuUser
    template_name = "accounts/user_create.html"
    form_class = BluuUserForm
    permission_required = 'accounts.add_bluuuser'

    def form_valid(self, form):
        response = super(BluuUserCreateView, self).form_valid(form)
        messages.success(self.request, _('User added'))
        return response

    #@method_decorator(login_required)
    #@method_decorator(permission_required('accounts.add_bluuuser'))
    #def dispatch(self, *args, **kwargs):
    #    return super(BluuUserCreateView, self).dispatch(*args, **kwargs)


class BluuUserUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edit Bluuuser
    We have to use braces.PermissionRequiredMixin here, because we
    check global permission to change_bluuuser.
    """
    model = BluuUser
    template_name = "accounts/user_update.html"
    form_class = BluuUserForm
    permission_required = 'accounts.change_bluuuser'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return self.model.app_users.all()

    def form_valid(self, form):
        response = super(BluuUserUpdateView, self).form_valid(form)
        messages.success(self.request, _('User changed'))
        return response

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_bluuuser',
    #        (BluuUser, 'pk', 'pk'), accept_global_perms=True))
    #def dispatch(self, *args, **kwargs):
    #    return super(BluuUserUpdateView, self).dispatch(*args, **kwargs)


@permission_required_or_403('accounts.delete_bluuuser')
def bluuuser_delete(request, username):
    obj = get_object_or_404(BluuUser, username=username)
    obj.delete()
    messages.success(request, _('User deleted'))
    return redirect('bluuuser_list')


class AccountUpdateView(UpdateView):
    """
    Updates user account data
    """
    template_name='accounts/account_change_form.html'
    form_class = AccountForm

    def get_success_url(self):
        messages.success(self.request, _('Account changed!'))
        return reverse('account_edit')

    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)


class BluuUserSitesView(PermissionRequiredMixin, DetailView):
    """
    Shows sites assigned to user
    We have to use braces.PermissionRequiredMixin here, because we
    check global permission to change_bluuuser.
    """
    model = BluuUser
    context_object_name = 'bluuuser'
    template_name = "accounts/user_sites.html"
    permission_required = 'accounts.change_bluuuser'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super(BluuUserSitesView, self).get_context_data(**kwargs)
        user = self.get_object() 
        context['bluusites'] = user.get_sites()
        return context


class BluuUserCompaniesView(PermissionRequiredMixin, DetailView):
    """
    Shows sites assigned to user
    We have to use braces.PermissionRequiredMixin here, because we
    check global permission to change_bluuuser.
    """
    model = BluuUser
    context_object_name = 'bluuuser'
    template_name = "accounts/user_companies.html"
    permission_required = 'accounts.change_bluuuser'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super(BluuUserCompaniesView, self).get_context_data(**kwargs)
        user = self.get_object() 
        context['companies'] = user.get_companies()
        return context



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


class AccountDeleteView(DeleteView):
    model = get_user_model()
    template_name='accounts/account_confirm_delete.html'
    context_object_name='account'
    success_url = '/'

    def get_queryset(self):
        return BluuUser.objects.filter(pk=self.request.user.pk)

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

