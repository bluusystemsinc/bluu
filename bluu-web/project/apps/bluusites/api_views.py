# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Group
from django.template import Context
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import (login_required, permission_required)
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages

import django_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.parsers import JSONParser
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user


from invitations.models import InvitationKey
from grontextual.models import UserObjectGroup
from accounts.models import BluuUser

from .models import (BluuSite, BluuSiteAccess, Room)
from .forms import SiteInvitationForm


class BluuSiteListJson(BaseDatatableView):
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'first_name', 'last_name', 'city']

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        return self.request.user.get_sites()

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(first_name__istartswith=q) |\
                             Q(last_name__istartswith=q))
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
                    reverse('site_edit', args=(item.pk,)), _('Manage'),
                    reverse('site_delete', args=(item.pk,)), 
                    _('Are you sure you want delete this site?'),
                    _('Delete'))
            json_data.append(
                {
                    "no": no,
                    "first_name": item.first_name,
                    "last_name": item.last_name,
                    "city": item.city,
                    "actions": actions
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403('bluusites.browse_bluusites',
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteListJson, self).dispatch(*args, **kwargs)


class BluuSiteAccessListJson(BaseDatatableView):
    """
    Returns list of users having an access to specified site.
    It's intended to work with Jquery datatable.
    """

    # Defines column names that will be used in sorting.
    # Order is important and should be the same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['email']

    def get_site(self, pk):
        return get_object_or_404(BluuSite, pk=pk)

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(email__istartswith=q))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        self.bluusite = self.get_site(kwargs.get('pk'))

        qs = BluuSiteAccess.objects.filter(site=self.bluusite)
        # number of records before filtering
        total_records = qs.count()
        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def _render_access_level(self, access, current_access):
        """
        Renders cell data determining user's access level to a site.
        Contains links that allow user to change access level. 
        """
        groups = []
        assigned_groups = {}
        if access.invitations.filter(registrant__isnull=True).exists():
            assigned_groups[access.group.name] = {"name": access.group.name,
                                                  "pk": access.group.pk,
                                                  "assigned": True}
        else:
            # if user already has this group
            for uog in UserObjectGroup.objects.get_for_object(access.user, self.bluusite):
                assigned_groups[uog.group.name] = {"name": uog.group.name,
                                                   "pk": uog.group.pk,
                                                   "assigned": True}

        for site_group in settings.SITE_GROUPS:
            group = Group.objects.get(name=site_group)
            if group.name not in assigned_groups.keys():
                groups.append({"pk": group.pk, "name": group.name, "assigned": False})
            else:
                groups.append(assigned_groups.get(site_group))

        t = get_template('bluusites/_site_access_list_cell.html')
        c = Context({
            'current_access': current_access,
            'access': access,
            'groups': groups})
        return t.render(c)

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        try:
            current_access = BluuSiteAccess.objects.get(user=self.request.user,
                                                        site=self.bluusite)
            current_access_pk = current_access.pk
        except BluuSiteAccess.DoesNotExist:
            current_access_pk = -1

        for access in qs:
            rendered_groups = self._render_access_level(access,
                                                        current_access_pk)

            json_data.append(
                {
                    "access":{
                        "no": no,
                        "id": access.pk,
                        "email": access.get_email,
                        "groups": rendered_groups,
                        "invitation": access.invitations.filter(registrant__isnull=True).exists(),
                        "current_user_access_id": current_access_pk
                    }
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403('bluusites.change_bluusite',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('bluusites.browse_bluusiteaccesses',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteAccessListJson, self).dispatch(*args, **kwargs)


class BluuSiteAccessCreateView(generics.CreateAPIView):
    """
    Create access for user to site
    """
    permission_classes = (permissions.IsAuthenticated,)
    model = BluuSite

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404


    def post(self, request, pk, format=None):
        site = self.get_site(pk)
        email = request.DATA.get('email')
        try:
            user = BluuUser.objects.get(email__iexact=email)
        except BluuUser.DoesNotExist:
            user = None
        try:
            if user:
                site_access = BluuSiteAccess.objects.get(user=user, site=site)
                return Response(
                            {
                             'errors': 
                                {'has_access': _('{} already has access'.\
                                        format(email))}
                            },
                            status=status.HTTP_400_BAD_REQUEST)
            elif email:
                site_access = BluuSiteAccess.objects.get(email__iexact=email,
                                                         site=site)
                return Response(
                            {
                             'errors': 
                                {'has_access': _('{} is alread invited'.\
                                        format(email))}
                            },
                            status=status.HTTP_400_BAD_REQUEST)

            form = SiteInvitationForm(request.DATA,
                                      instance=site_access,
                                      request=request,
                                      site=site)
        except BluuSiteAccess.DoesNotExist:
            form = SiteInvitationForm(request.DATA, request=request, site=site)
        
        if form.is_valid():
            access = form.save(commit=False)
            access.site = site
            try:
                user = BluuUser.objects.get(email__iexact=email)
                # user exists, so grant him an access to a company
                access.user = user
                access.email = user.email
                access.save()
                form.save_m2m()

            except BluuUser.DoesNotExist:
                # send invitation
                access.save()
                form.save_m2m()
                invitation = InvitationKey.objects.create_invitation(
                        user=request.user,
                        content_object=access
                        )
                invitation.send_to(access.email)

            return Response({'email': email,
                             'group': request.DATA['group']},
                            status=status.HTTP_201_CREATED)

        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(permission_required_or_403('bluusites.change_bluusite',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('bluusites.add_bluusiteaccess',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteAccessCreateView, self).dispatch(*args, **kwargs)


class BluuSiteAccessUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Change existing access level
    """
    model = BluuSiteAccess

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        site_pk = int(kwargs.get('site_pk'))
        access_pk = int(kwargs.get('pk'))
        try:
            current_access = BluuSiteAccess.objects.get(
                                user=request.user,
                                site__pk=site_pk)
            if current_access.pk == access_pk:
                messages.success(request, _('Site access changed'))
        except BluuSiteAccess.DoesNotExist:
            pass
        return super(BluuSiteAccessUpdateView, self).update(request,
                                                           *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        site_pk = int(kwargs.get('site_pk'))
        access_pk = int(kwargs.get('pk'))
        try:
            # If user removes his own access then there will be a redirection,
            # so we should show information about the operation.
            current_access = BluuSiteAccess.objects.get(
                                user=request.user,
                                site__pk=site_pk)
            if current_access.pk == access_pk:
                messages.success(request, _('Site access removed'))
        except BluuSiteAccess.DoesNotExist:
            pass
        return super(BluuSiteAccessUpdateView, self).delete(request,
                                                            *args, **kwargs)


    @method_decorator(permission_required_or_403('bluusites.change_bluusite',
                                                 (BluuSite, 'pk', 'site_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('bluusites.change_bluusiteaccess',
                                                 (BluuSite, 'pk', 'site_pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(BluuSiteAccessUpdateView, self).dispatch(*args, **kwargs)


class RoomListJson(BaseDatatableView):
    """
    Returns list of rooms assigned to a site.
    It's intended to work with Jquery datatable.
    """

    # Defines column names that will be used in sorting.
    # Order is important and should be the same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'name']

    def get_site(self, pk):
        return get_object_or_404(BluuSite, pk=pk)

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(name__istartswith=q))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        self.bluusite = self.get_site(kwargs.get('site_pk'))

        qs = Room.objects.filter(bluusite=self.bluusite)
        # number of records before filtering
        total_records = qs.count()
        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = qs.count()
        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for room in qs:
            actions = '<a href="{0}">{1}</a> <a href="{2}" onclick="return confirm(\'{3}\')">{4}</a>'.format(
                    reverse('room_edit', args=(room.bluusite_id, room.pk,)), _('Manage'),
                    reverse('room_delete', args=(room.bluusite_id, room.pk,)), 
                    _('Are you sure you want delete this room?'),
                    _('Delete'))

            json_data.append(
                {
                    "room":{
                        "no": no,
                        "name": room.name,
                        "actions": actions
                    }
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403(
        'bluusites.change_bluusite',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    @method_decorator(permission_required_or_403(
        'bluusites.browse_rooms',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(RoomListJson, self).dispatch(*args, **kwargs)
