from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from home.models import Profile, Expense
from django.utils import timezone

class ExpenseAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.client.login(username='testuser', password='pass1234')

    def test_registration(self):
        response = self.client.post(reverse('reg'), {
            'username': 'newuser',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        response = self.client.post(reverse('login'), {'login': 'testuser', 'password': 'pass1234'})
        self.assertEqual(response.status_code, 302)

    def test_add_expense(self):
        response = self.client.post(reverse('home'), {
            'text': 'Test expense',
            'amount': '50',
            'expense_type': 'Negative',
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expense.objects.filter(user=self.user, name='Test expense').exists())

    def test_delete_expense(self):
        expense = Expense.objects.create(user=self.user, name='Delete me', amount=30, expense_type='Negative')
        response = self.client.get(reverse('delete_transaction', args=[expense.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expense.objects.filter(id=expense.id).exists())
