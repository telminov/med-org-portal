import json
from unittest import mock

from django.contrib.auth.models import Permission as AuthPermission
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from mis.org import Org
from core.tests.base import BaseTestCase
from core import models

User = get_user_model()


class TestEdit(BaseTestCase):
    view = 'core:user_edit'
    permission = 'auth.change_user'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

        self.permission_group = AuthGroup.objects.create(name='Testing permission group')
        self.auth_permission = AuthPermission.objects.get(id=1)
        self.permission_group.permissions.add(self.auth_permission)

        self.test_user = User.objects.create(
            username='new_user',
            password='123456'
        )

    def get_url_kwargs(self):
        return {'pk': self.test_user.id}

    @mock.patch.object(Org, 'get')
    def test_add(self, mock_org):
        mock_org.return_value = Org(id=1, name='test org')
        response = self.client.get(self.get_url())
        self.check_response(response)
        self.assertEqual(response.context_data['object'], self.test_user)

        params = {
            'username': 'NewUser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@tes.ru',
            'is_active': True,
            'new_password': '123456',
            'groups': self.permission_group.id,
            'orgs': ["1", "5", "8"]
        }
        response = self.client.post(self.get_url(), params)
        self.check_response(response, status=302)
        self.assertEqual(response.url, reverse_lazy('core:user'))

        user = User.objects.get(id=self.test_user.id)
        self.assertEqual(user.username, params['username'])
        self.assertEqual(user.core.org_ids, json.dumps(params['orgs']))
