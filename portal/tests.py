from django.test import TestCase
from portal.models import Application, Portal, Server


class ServerTestCase(TestCase):
    def setUp(self):
        Server.objects.create(name='Test Server', ip='127.0.0.1', environment='develop')

    def test_local_server_exists(self):
        server = Server.objects.get(ip='127.0.0.1')
        self.assertEqual('127.0.0.1', server.ip)
