"""
Les tests de l'application usermanagement
"""

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


class StatusTest(TestCase):

    def setUp(self):
        self.client = Client()


    def test_public(self):
        urls = [{'url':'/user/login/',
                 'template':'user/login.html',
                 'status':200
                },
                {'url':'/user/logout/',
                 'template':'user/login.html',
                 'status':302},
                 {'url':'/user/profile/',
                  'template':'user/login.html',
                  'status':302}
                     ]
        for elem in urls:
            response = self.client.get(elem['url'])
            self.assertEqual(response.status_code,elem['status'])
            response = self.client.get(elem['url'],follow=True)
            self.assertEqual(response.templates[0].name, elem['template'])

    def test_create_user(self):
         response = self.client.post('/user/create_account/',{
                 'username':'john',
                 'password1':'trytoguess',
                 'password2':'trytoguess'
                 },follow=True)
         self.assertEqual(response.templates[0].name,'user/succes.html')
         user = User.objects.get(username="john")
         self.assertEqual(user.username,"john")

    def test_login(self):
        self.test_create_user()
        response = self.client.post('/user/login/',{
                'username':'john',
                'password':'trytoguess'
                },follow=True)
        self.assertEqual(response.templates[0].name,'user/profile.html')
