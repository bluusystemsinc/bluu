from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.generic import (UpdateView, CreateView, DetailView,
                                  ListView, TemplateView)
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError

from guardian.decorators import permission_required
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from braces.views import (LoginRequiredMixin, PermissionRequiredMixin)

from grontextual.shortcuts import get_objects_for_user
from grontextual.models import UserObjectGroup
from accounts.forms import BluuUserForm
from bluusites.models import BluuSite
from bluusites.forms import SiteForm
from .models import Company
from .forms import CompanyForm, CompanyInvitationForm


class CompanyListView(GPermissionRequiredMixin, ListView):
    model = Company
    template_name = "companies/company_list.html"
    permission_required = 'companies.browse_companies'

    def get_queryset(self):
        if self.request.user.has_perm('companies.view_company'):
            return super(CompanyListView, self).get_queryset()
        return get_objects_for_user(self.request.user, 'companies.view_company')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        companies = self.request.user.can_see_companies(\
                perm='companies.change_company')
        company = companies.get('company', None)
        if company is not None:
            return redirect('company_edit', pk=company.pk)

        return super(CompanyListView, self).dispatch(*args, **kwargs)


class CompanyCreateView(CreateView):
    model = Company
    template_name = "companies/company_create.html"
    form_class = CompanyForm

    def form_valid(self, form):
        response = super(CompanyCreateView, self).form_valid(form)
        #_create_groups_for_company(self.object)
        messages.success(self.request, _('Company added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('companies.add_company'))
    def dispatch(self, *args, **kwargs):
        return super(CompanyCreateView, self).dispatch(*args, **kwargs)


class CompanyUpdateView(UpdateView):
    model = Company
    template_name = "companies/company_update.html"
    form_class = CompanyForm

    def form_valid(self, form):
        response = super(CompanyUpdateView, self).form_valid(form)
        messages.success(self.request, _('Company changed'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('companies.change_company',
                                          (Company, 'pk', 'pk'),
                                           accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyUpdateView, self).dispatch(*args, **kwargs)



@login_required
@permission_required('companies.delete_company', (Company, 'pk', 'pk'),
                     accept_global_perms=True)
def company_delete(request, pk):
    obj = get_object_or_404(Company, pk=pk)
    try:
        obj.delete()
        messages.success(request, _('Company deleted'))
    except ProtectedError:
        messages.error(
               request,
               _('Company cannot be deleted until there are dependent sites. '))

    return redirect('company_list')

"""
class CompanyDeleteView(GPermissionRequiredMixin, DeleteView):
    model = Company
    template_name = "companies/company_delete.html"
    permission_required = 'companies.delete_company'

    #@method_decorator(login_required)
    #@method_decorator(permission_required_or_403('companies.delete_company',
    #        (Company, 'pk', 'pk')))
    #def dispatch(self, *args, **kwargs):
    #    return super(CompanyDeleteView, self).dispatch(*args, **kwargs)
"""

class CompanyAccessListView(TemplateView):
    template_name = "companies/company_access_list.html"
    pk_url_kwarg = 'company_pk'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(Company, pk=pk)

    def get_context_data(self, **kwargs):
        company = self.get_object()
        invitation_form = CompanyInvitationForm()
        return {
            'params': kwargs,
            'company': company,
            'invitation_form': invitation_form
        } 

    @method_decorator(login_required)
    @method_decorator(permission_required('companies.change_company',
                                (Company, 'pk', 'company_pk'),
                                accept_global_perms=True))
    @method_decorator(permission_required('companies.browse_companyaccesses',
                                (Company, 'pk', 'company_pk'),
                                accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyAccessListView, self).dispatch(*args, **kwargs)


class CompanySiteListView(DetailView):
    model = Company
    template_name = "companies/company_site_list.html"
    pk_url_kwarg = 'company_pk'

    def get_context_data(self, **kwargs):
        kwargs['form'] = SiteForm()
        return super(CompanySiteListView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    @method_decorator(permission_required('companies.change_company',
                                           (Company, 'pk', 'company_pk'),
                                           accept_global_perms=True))
    @method_decorator(permission_required('bluusites.browse_bluusites',
                                          accept_global_perms=True ))
    def dispatch(self, *args, **kwargs):
        return super(CompanySiteListView, self).dispatch(*args, **kwargs)


#class CompanySiteCreateView(CreateView):
#    model = BluuSite
#    template_name = "companies/company_site_create.html"
#    form_class = SiteForm
#    pk_url_kwarg = 'company_pk'
#    #permission_required = 'companies.change_company'
#
#    #def get_form_kwargs(self, **kwargs):
#        #kwargs = super(CompanySiteCreateView, self).get_form_kwargs(**kwargs)
#        #kwargs['user'] = self.request.user
#        #return kwargs
#
#    def get_success_url(self):
#        return reverse('company_site_list', args=[self.company.pk]) 
#
#    def get_context_data(self, **kwargs):
#        context = super(CompanySiteCreateView, self).get_context_data(**kwargs)
#        context['company'] = self.company
#        return context 
#
#    def form_valid(self, form):
#        self.object = form.save(commit=False)
#        self.object.company = self.company
#        self.object.save()
#        form.save_m2m()
#
#        messages.success(self.request, _('Site added'))
#        return HttpResponseRedirect(self.get_success_url())
#
#    @method_decorator(login_required)
#    @method_decorator(permission_required_or_403('companies.change_company',
#            (Company, 'pk', 'company_pk')))
#    @method_decorator(permission_required('bluusites.add_bluusite'))
#    def dispatch(self, *args, **kwargs):
#        try:
#            self.company = \
#                    Company.objects.get(pk=kwargs.get('company_pk', None))
#        except ObjectDoesNotExist:
#            pass
#        return super(CompanySiteCreateView, self).dispatch(*args, **kwargs)
