from datetime import date, timedelta

from django.test import TestCase

from Proveedores.models import Proveedor
from RFQ_Mold.models import RFQ_Mold
from users.models import CustomUser

from .models import Asignacion_Proveedor_Mold
from .services import (
    close_expired_assignments,
    close_rfq_if_all_assignments_answered,
    reopen_assignment_for_extension,
    validate_assignment_can_receive_quote,
)


class AssignmentLifecycleServiceTests(TestCase):
    def setUp(self):
        self.com_user = CustomUser.objects.create_user(
            username='compras',
            email='compras@example.com',
            password='pass12345',
            role='Com',
        )
        self.pro_user = CustomUser.objects.create_user(
            username='proveedor',
            email='proveedor@example.com',
            password='pass12345',
            role='Pro',
        )
        self.proveedor = Proveedor.objects.create(
            id_account=self.pro_user,
            company_name='Proveedor Uno',
            contact_email='proveedor@example.com',
        )
        self.rfq = RFQ_Mold.objects.create(
            created_by=self.com_user,
            due_date=date.today() + timedelta(days=10),
        )

    def create_assignment(self, due_date=None, is_answered=False):
        return Asignacion_Proveedor_Mold.objects.create(
            id_RFQ_Mold=self.rfq,
            id_Proveedor=self.proveedor,
            id_user_comercializacion=self.com_user,
            due_date=due_date or date.today() + timedelta(days=3),
            is_answered=is_answered,
        )

    def test_expired_assignment_is_closed_and_rejects_quotes(self):
        assignment = self.create_assignment(due_date=date.today() - timedelta(days=1))

        can_quote, message = validate_assignment_can_receive_quote(assignment)
        assignment.refresh_from_db()

        self.assertFalse(can_quote)
        self.assertIn('cerrada', message)
        self.assertTrue(assignment.is_closed)

    def test_async_close_expired_assignments_marks_only_unanswered_expired(self):
        expired = self.create_assignment(due_date=date.today() - timedelta(days=1))
        active = self.create_assignment(due_date=date.today() + timedelta(days=1))

        result = close_expired_assignments()
        expired.refresh_from_db()
        active.refresh_from_db()

        self.assertEqual(result['mold_closed'], 1)
        self.assertTrue(expired.is_closed)
        self.assertFalse(active.is_closed)

    def test_extension_reopens_closed_assignment(self):
        assignment = self.create_assignment(due_date=date.today() - timedelta(days=1))
        close_expired_assignments()
        assignment.refresh_from_db()

        reopen_assignment_for_extension(assignment, date.today() + timedelta(days=5))
        assignment.refresh_from_db()

        self.assertFalse(assignment.is_closed)
        self.assertEqual(assignment.due_date, date.today() + timedelta(days=5))

    def test_all_answered_closes_assignments_not_rfq(self):
        first = self.create_assignment(is_answered=True)
        second = self.create_assignment(is_answered=True)

        completed = close_rfq_if_all_assignments_answered(self.rfq)
        self.rfq.refresh_from_db()
        first.refresh_from_db()
        second.refresh_from_db()

        self.assertTrue(completed)
        self.assertFalse(self.rfq.complete)  # cierre formal es manual
        self.assertTrue(first.is_closed)
        self.assertTrue(second.is_closed)
