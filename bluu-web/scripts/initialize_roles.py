from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# content types
user_type = ContentType.objects.get(app_label="accounts",
                                        model="bluuuser")

company_type = ContentType.objects.get(app_label="accounts",
                                        model="company")
contract_type = ContentType.objects.get(app_label="accounts",
                                        model="contract")


# permissions
perm_add_user = Permission.objects.get(content_type=user_type,
                        codename=u"add_bluuuser")
perm_change_user = Permission.objects.get(content_type=user_type,
                        codename=u"change_bluuuser")
perm_delete_user = Permission.objects.get(content_type=user_type,
                        codename=u"delete_bluuuser")
perm_browse_user = Permission.objects.get(content_type=user_type,
                                                  codename=u"browse_bluuusers")

perm_manage_dealers = Permission.objects.get(
                        content_type=user_type,
                        codename=u"manage_dealers")

perm_add_company = Permission.objects.get(content_type=company_type,
                        codename=u"add_company")
perm_change_company = Permission.objects.get(content_type=company_type,
                        codename=u"change_company")
perm_delete_company = Permission.objects.get(content_type=company_type,
                        codename=u"delete_company")
perm_browse_companies = Permission.objects.get(content_type=company_type,
                                                  codename=u"browse_companies")

perm_add_contract = Permission.objects.get(content_type=contract_type,
                        codename=u"add_contract")
perm_change_contract = Permission.objects.get(content_type=contract_type,
                        codename=u"change_contract")
perm_delete_contract = Permission.objects.get(content_type=contract_type,
                        codename=u"delete_contract")
perm_browse_contract = Permission.objects.get(content_type=contract_type,
                                                  codename=u"browse_contracts")


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
        perm_add_user,
        perm_change_user,
        perm_delete_user,
        perm_browse_user,
        perm_manage_dealers,
        perm_add_company,
        perm_change_company,
        perm_delete_company,
        perm_browse_companies]

    # create Dealer role
    dealer_group = Group.objects.get_or_create(name=u'Dealer')[0]

    # assign permissions to Dealer
    dealer_group.permissions.clear()

    dealer_group.permissions = [
        perm_add_user,
        perm_change_user,
        perm_delete_user,
        perm_browse_user]

    # create Master User role
    masteruser_group = Group.objects.get_or_create(name=u'Master User')[0]

    # assign permissions to Master User
    masteruser_group.permissions.clear()

    masteruser_group.permissions = [
        perm_add_user,
        perm_change_user,
        perm_delete_user,
        perm_browse_user]

    print u'Done!'