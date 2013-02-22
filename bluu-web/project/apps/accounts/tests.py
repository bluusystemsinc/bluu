from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign
from django.contrib.auth.models import Group

from .models import BluuUser
from companies.models import Company

class AccountsTestCase(WebTest):

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.user1 = G(BluuUser, username='test1')
        
        self.user2 = G(BluuUser, username='test2',
                       groups=[Group.objects.get(name='Bluu')])

        self.user3 = G(BluuUser, username='test3')
        assign('companies.browse_companies', self.user3)
        assign('companies.view_company', self.user3, self.company1)

    def testDefaultGroupAssignment(self):
        BluuUser.objects.create_user(username="x", email="x@example.com",
                                     password="x")
        group = Group.objects.get(name=u'Base User')
        u = BluuUser.objects.get(username="x")
        self.assertTrue(group in u.groups.all())
    
    def testUserAdd(self):
        group = Group.objects.get(name=u'Base User')

        res = self.app.get(reverse('bluuuser_add'), user='test2')
        form = res.form
        form['username'] = 'x'
        form['email'] = 'x@example.com'
        form['password1'] = 'pass'
        form['password2'] = 'pass'
        #form['groups'] = [group.pk]
        form['first_name'] = 'first name'
        form['last_name'] = 'last name'
        form_res = form.submit().follow()

        assert "User added" in form_res
        self.assertTrue(BluuUser.objects.filter(username='x').exists())
        user = BluuUser.objects.get(username='x')
        self.assertTrue(group in user.groups.all())
