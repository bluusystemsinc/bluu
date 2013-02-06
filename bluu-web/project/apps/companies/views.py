from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 DeleteView, ListView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user
from braces.views import LoginRequiredMixin
from guardian.mixins import PermissionRequiredMixin

from accounts.forms import BluuUserForm
from bluusites.models import BluuSite
from bluusites.forms import SiteForm
from .models import Company
from .forms import CompanyForm


class CompanyListView(PermissionRequiredMixin, ListView):
    model = Company
    template_name = "companies/company_list.html"
    permission_required = 'companies.browse_companies'

    def get_queryset(self):
        if self.request.user.has_perm('companies.view_company'):
            return super(CompanyListView, self).get_queryset()
        return get_objects_for_user(self.request.user, 'companies.view_company')

    #@method_decorator(login_required)
    #@method_decorator(permission_required('companies.browse_companies'))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyListView, self).dispatch(*args, **kwargs)


class CompanyCreateView(PermissionRequiredMixin, CreateView):
    model = Company
    template_name = "companies/company_create.html"
    form_class = CompanyForm
    permission_required = 'companies.add_company'

    def form_valid(self, form):
        response = super(CompanyCreateView, self).form_valid(form)
        #_create_groups_for_company(self.object)
        messages.success(self.request, _('Company added'))
        return response

    #@method_decorator(login_required)
    #@method_decorator(permission_required('companies.add_company'))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyCreateView, self).dispatch(*args, **kwargs)


class CompanyUpdateView(PermissionRequiredMixin, UpdateView):
    model = Company
    template_name = "companies/company_update.html"
    form_class = CompanyForm
    permission_required = 'companies.change_company'

    def form_valid(self, form):
        response = super(CompanyUpdateView, self).form_valid(form)
        messages.success(self.request, _('Company changed'))
        return response

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_company',
    #        (Company, 'pk', 'pk'), accept_global_perms=True))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyUpdateView, self).dispatch(*args, **kwargs)


@permission_required_or_403('companies.delete_company')
def company_delete(request, pk):
    obj = get_object_or_404(Company, pk=pk)
    obj.delete()
    messages.success(request, _('Company deleted'))
    return redirect('company_list')


class CompanyDeleteView(PermissionRequiredMixin, DeleteView):
    model = Company
    template_name = "companies/company_delete.html"
    permission_required = 'companies.delete_company'

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.delete_company',
    #        (Company, 'pk', 'pk')))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyDeleteView, self).dispatch(*args, **kwargs)


class CompanyAccessListView(PermissionRequiredMixin, DetailView):
    model = Company
    template_name = "companies/company_access_list.html"
    pk_url_kwarg = 'company_pk'
    permission_required = 'companies.change_company'

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_company',
    #        (Company, 'pk', 'pk')))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyAccessListView, self).\
    #            dispatch(*args, **kwargs)


class CompanyAccessCreateView(PermissionRequiredMixin, DetailView):
    model = Company
    template_name = "companies/company_access_create.html"
    pk_url_kwarg = 'company_pk'
    permission_required = 'companies.change_company'

    def get_context_data(self, **kwargs):
        kwargs['form'] = BluuUserForm(self.request.user, None)
        return super(CompanyAccessListView, self).get_context_data(**kwargs)

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_company',
    #        (Company, 'pk', 'pk')))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyAccessManagementView, self).\
    #            dispatch(*args, **kwargs)

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_company',
    #        (Company, 'pk', 'company_pk')))
    #@method_decorator(permission_required('accounts.add_bluusite'))
    def dispatch(self, *args, **kwargs):
        try:
            self.company = \
                    Company.objects.get(pk=kwargs.get('company_pk', None))
        except ObjectDoesNotExist:
            pass
        return super(CompanyAccessCreateView, self).dispatch(*args, **kwargs)


class CompanySiteListView(PermissionRequiredMixin, DetailView):
    model = Company
    template_name = "companies/company_site_list.html"
    pk_url_kwarg = 'company_pk'
    permission_required = 'companies.change_company'

    def get_context_data(self, **kwargs):
        kwargs['form'] = SiteForm()
        return super(CompanySiteListView, self).get_context_data(**kwargs)

    #@method_decorator(login_required)
    #@method_decorator(permission_required('bluusites.browse_bluusites'))
    def dispatch(self, *args, **kwargs):
        return super(CompanySiteListView, self).dispatch(*args, **kwargs)


class CompanySiteCreateView(PermissionRequiredMixin, CreateView):
    model = BluuSite
    template_name = "companies/company_site_create.html"
    form_class = SiteForm
    pk_url_kwarg = 'company_pk'
    permission_required = 'companies.change_company'

    #def get_form_kwargs(self, **kwargs):
        #kwargs = super(CompanySiteCreateView, self).get_form_kwargs(**kwargs)
        #kwargs['user'] = self.request.user
        #return kwargs

    def get_success_url(self):
        return reverse('company_site_list', args=[self.company.pk]) 

    def get_context_data(self, **kwargs):
        context = super(CompanySiteCreateView, self).get_context_data(**kwargs)
        context['company'] = self.company
        return context 

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.company
        self.object.save()
        form.save_m2m()

        messages.success(self.request, _('Site added'))
        return HttpResponseRedirect(self.get_success_url())

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.change_company',
    #        (Company, 'pk', 'company_pk')))
    #@method_decorator(permission_required('accounts.add_bluusite'))
    def dispatch(self, *args, **kwargs):
        try:
            self.company = \
                    Company.objects.get(pk=kwargs.get('company_pk', None))
        except ObjectDoesNotExist:
            pass
        return super(CompanySiteCreateView, self).dispatch(*args, **kwargs)

