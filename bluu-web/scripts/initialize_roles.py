from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# content types
user_type = ContentType.objects.get(app_label="accounts",
                                        model="bluuuser")
company_type = ContentType.objects.get(app_label="companies",
                                        model="company")
companyaccess_type = ContentType.objects.get(app_label="companies",
                                        model="companyaccess")
site_type = ContentType.objects.get(app_label="bluusites",
                                        model="bluusite")
siteaccess_type = ContentType.objects.get(app_label="bluusites",
                                        model="bluusiteaccess")


# permissions
perm_browse_users = Permission.objects.get(content_type=user_type,
                                                  codename=u"browse_bluuusers")
perm_add_user = Permission.objects.get(content_type=user_type,
                        codename=u"add_bluuuser")
perm_change_user = Permission.objects.get(content_type=user_type,
                        codename=u"change_bluuuser")
perm_delete_user = Permission.objects.get(content_type=user_type,
                        codename=u"delete_bluuuser")

perm_browse_companies = Permission.objects.get(content_type=company_type,
                        codename=u"browse_companies")
perm_view_company = Permission.objects.get(content_type=company_type,
                        codename=u"view_company")
perm_add_company = Permission.objects.get(content_type=company_type,
                        codename=u"add_company")
perm_change_company = Permission.objects.get(content_type=company_type,
                        codename=u"change_company")
perm_delete_company = Permission.objects.get(content_type=company_type,
                        codename=u"delete_company")

perm_browse_companyaccesses = Permission.objects.get(content_type=companyaccess_type,
                        codename=u"browse_companyaccesses")
perm_add_companyaccess = Permission.objects.get(content_type=companyaccess_type,
                        codename=u"add_companyaccess")
perm_change_companyaccess = Permission.objects.get(content_type=companyaccess_type,
                        codename=u"change_companyaccess")
perm_delete_companyaccess = Permission.objects.get(content_type=companyaccess_type,
                        codename=u"delete_companyaccess")

perm_browse_sites = Permission.objects.get(content_type=site_type,
                                                  codename=u"browse_bluusites")
perm_view_site = Permission.objects.get(content_type=site_type,
                                                  codename=u"view_bluusite")
perm_add_site = Permission.objects.get(content_type=site_type,
                        codename=u"add_bluusite")
perm_change_site = Permission.objects.get(content_type=site_type,
                        codename=u"change_bluusite")
perm_delete_site = Permission.objects.get(content_type=site_type,
                        codename=u"delete_bluusite")

perm_browse_bluusiteaccesses = Permission.objects.get(content_type=siteaccess_type,
                        codename=u"browse_bluusiteaccesses")
perm_add_bluusiteaccess = Permission.objects.get(content_type=siteaccess_type,
                        codename=u"add_bluusiteaccess")
perm_change_bluusiteaccess = Permission.objects.get(content_type=siteaccess_type,
                        codename=u"change_bluusiteaccess")
perm_delete_bluusiteaccess = Permission.objects.get(content_type=siteaccess_type,
                        codename=u"delete_bluusiteaccess")

def run():
    """We're going to have TestCenter Admin and Group Admin roles.
    TestCenter Admin is allowed to do anything, while Group Admin can only
    create normal applicant accounts inside his entity and assign
    tests to them.
    """
    # create Bluu role
    bluu_group = Group.objects.get_or_create(name=u'Bluu')[0]

    # assign permissions to TestCenter Admin
    bluu_group.permissions.clear()

    bluu_group.permissions = [
        perm_browse_users,
        perm_add_user,
        perm_change_user,
        perm_delete_user,

        perm_browse_companies,
        perm_view_company,
        perm_add_company,
        perm_change_company,
        perm_delete_company,

        perm_browse_companyaccesses,
        perm_add_companyaccess,
        perm_change_companyaccess,
        perm_delete_companyaccess,
        
        perm_browse_sites,
        perm_view_site,
        perm_add_site,
        perm_change_site,
        perm_delete_site,

        perm_browse_bluusiteaccesses,
        perm_add_bluusiteaccess,
        perm_change_bluusiteaccess,
        perm_delete_bluusiteaccess,
    ]

    # create Dealer role
    """
    Dealer role is intended to be used only in context of specific objects
    like company or site. 
    Example:
    In context of company A user XYZ is a Dealer
    """
    dealer_group = Group.objects.get_or_create(name=u'Dealer')[0]

    # assign permissions to Dealer
    dealer_group.permissions.clear()

    dealer_group.permissions = [
        perm_change_user,

        perm_browse_companies,
        perm_view_company,
        perm_change_company,

        perm_browse_companyaccesses,
        perm_add_companyaccess,
        perm_change_companyaccess,
        perm_delete_companyaccess,
        
        perm_browse_sites,
        perm_view_site,
        perm_add_site,
        perm_change_site,
        perm_delete_site,

        perm_browse_bluusiteaccesses,
        perm_add_bluusiteaccess,
        perm_change_bluusiteaccess,
        perm_delete_bluusiteaccess,
    ]

    # create Technician role
    """
    Technician role is intended to be used only in context of specific objects
    like company or site. 
    Example:
    In context of company A user XYZ is a Technician
    """
    technician_group = Group.objects.get_or_create(name=u'Technician')[0]

    # assign permissions to Technician
    technician_group.permissions.clear()

    technician_group.permissions = [
        perm_change_user,

        perm_browse_companies,
        perm_view_company,

        perm_browse_sites,
        perm_view_site,
        perm_add_site,
        perm_change_site,
        perm_delete_site,

        perm_browse_bluusiteaccesses,
        perm_add_bluusiteaccess,
        perm_change_bluusiteaccess,
        perm_delete_bluusiteaccess,
    ]

    # create Company Employee role
    """
    Company Employee role is intended to be a global role
    """
    company_employee_group = Group.objects.get_or_create(name=u'Company Employee')[0]

    # assign permissions to Company Employee
    company_employee_group.permissions.clear()

    company_employee_group.permissions = [
        perm_browse_companies,
        perm_browse_sites,
        perm_add_site,
        #perm_view_site,
        #perm_change_site,
        #perm_delete_site,
    ]

    # create Master User role
    """
    Master User role is intended to be used only in context of specific objects
    like company or site. 
    Example:
    In context of site A user XYZ is a Master User
    """
    masteruser_group = Group.objects.get_or_create(name=u'Master User')[0]

    # assign permissions to Master User
    masteruser_group.permissions.clear()

    masteruser_group.permissions = [
        perm_change_user,

        perm_browse_sites,
        perm_view_site,
        perm_change_site,

        perm_browse_bluusiteaccesses,
        perm_add_bluusiteaccess,
        perm_change_bluusiteaccess,
        perm_delete_bluusiteaccess,
        ]

    """
    User role is intended to be used only in context of specific objects
    like company or site. 
    Example:
    In context of site A user XYZ is a User
    """
    user_group = Group.objects.get_or_create(name=u'User')[0]

    # assign permissions to User
    user_group.permissions.clear()

    user_group.permissions = [
        perm_change_user,

        perm_browse_sites,
        perm_view_site,
    ]

