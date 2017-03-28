from django.test import TestCase
from persomaker.models import Character
# Create your tests here.
class PersomakerModelsCharacterTestcases(TestCase):
    def setUp(self):
        Character.objects.create(name="lion",)
    def test_character_create(self):
        testcharacter = Character.objects.get(name ='lion')
        self.assertEqual(testcharacter.name, "lion")
