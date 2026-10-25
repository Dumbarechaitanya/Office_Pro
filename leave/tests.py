from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from leave import workflow as wf


class ApprovalTypeTests(SimpleTestCase):
    def test_normalisation(self):
        self.assertEqual(wf.normalize_approval_type('no_validation'), wf.FLOW_NONE)
        self.assertEqual(wf.normalize_approval_type('No Validation'), wf.FLOW_NONE)
        self.assertEqual(wf.normalize_approval_type('both'), wf.FLOW_DOUBLE)
        self.assertEqual(wf.normalize_approval_type('By Approver and Officer'), wf.FLOW_DOUBLE)
        self.assertEqual(wf.normalize_approval_type('officer'), wf.FLOW_SINGLE)
        self.assertEqual(wf.normalize_approval_type('By Time Off Officer'), wf.FLOW_SINGLE)
        self.assertEqual(wf.normalize_approval_type(None), wf.FLOW_SINGLE)


class DurationTests(SimpleTestCase):
    MON, FRI, SAT, SUN, NEXT_MON = date(2026, 11, 2), date(2026, 11, 6), date(2026, 11, 7), date(2026, 11, 8), date(2026, 11, 9)

    def test_weekends_are_excluded(self):
        self.assertEqual(wf.count_working_days(self.MON, self.NEXT_MON), 6)   # Mon-Fri + next Mon
        self.assertEqual(wf.count_working_days(self.SAT, self.SUN), 0)

    def test_holidays_are_excluded(self):
        self.assertEqual(wf.count_working_days(self.MON, self.FRI, {date(2026, 11, 4)}), 4)

    def test_browser_cannot_inflate_a_multi_day_duration(self):
        duration, err = wf.resolve_duration(self.MON, self.FRI, '999')
        self.assertIsNone(err)
        self.assertEqual(duration, Decimal(5))     # server value wins

    def test_single_day_accepts_half_or_full_only(self):
        self.assertEqual(wf.resolve_duration(self.MON, self.MON, '0.5')[0], Decimal('0.5'))
        self.assertEqual(wf.resolve_duration(self.MON, self.MON, '1')[0], Decimal('1'))
        for bad in ('0', '-1', '30', 'abc', None, '0.3'):
            self.assertIsNotNone(wf.resolve_duration(self.MON, self.MON, bad)[1], bad)

    def test_weekend_only_range_is_rejected(self):
        self.assertIsNotNone(wf.resolve_duration(self.SAT, self.SUN, '1')[1])


class ValidationTests(SimpleTestCase):
    TODAY = date(2026, 11, 2)

    def test_end_before_start(self):
        self.assertTrue(wf.validate_leave_request(date(2026, 11, 5), date(2026, 11, 3), self.TODAY))

    def test_backdated_blocked_unless_admin(self):
        past = date(2026, 10, 1)
        self.assertTrue(wf.validate_leave_request(past, past, self.TODAY))
        self.assertFalse(wf.validate_leave_request(past, past, self.TODAY, can_backdate=True))

    def test_today_is_allowed(self):
        self.assertFalse(wf.validate_leave_request(self.TODAY, self.TODAY, self.TODAY))

    def test_overlap(self):
        d = date(2026, 11, 10)
        self.assertTrue(wf.validate_leave_request(d, d, self.TODAY, overlap_exists=True))

    def test_insufficient_balance(self):
        d = date(2026, 11, 10)
        errs = wf.validate_leave_request(d, d, self.TODAY, requires_allocation=True,
                                         available_balance=Decimal('0.5'), duration=Decimal('1'))
        self.assertTrue(errs)
        ok = wf.validate_leave_request(d, d, self.TODAY, requires_allocation=True,
                                       available_balance=Decimal('2'), duration=Decimal('1'))
        self.assertFalse(ok)

    def test_balance_ignored_when_type_needs_no_allocation(self):
        d = date(2026, 11, 10)
        self.assertFalse(wf.validate_leave_request(d, d, self.TODAY, requires_allocation=False,
                                                   available_balance=Decimal('0'), duration=Decimal('5')))


def decide(**over):
    base = dict(action='validate', status='confirm', flow=wf.FLOW_SINGLE, first_approved=False,
                actor_is_self=False, actor_is_l1=False, actor_is_l2=False, actor_is_officer=False,
                actor_is_admin=False, actor_is_first_approver=False)
    base.update(over)
    return wf.decide(**base)


class ApprovalDecisionTests(SimpleTestCase):
    def test_cannot_approve_own_request_even_as_admin(self):
        d = decide(actor_is_self=True, actor_is_admin=True, actor_is_officer=True)
        self.assertIsNotNone(d.error)
        self.assertIsNotNone(decide(action='refuse', actor_is_self=True, actor_is_l1=True).error)

    def test_processed_requests_cannot_be_changed_again(self):
        for status in ('validate', 'refuse', 'Approved', 'Rejected'):
            self.assertIsNotNone(decide(status=status, actor_is_officer=True).error, status)
        # in particular: a refused request can no longer be re-approved
        self.assertIsNotNone(decide(status='refuse', actor_is_admin=True).error)

    def test_unauthorised_user_is_denied(self):
        self.assertIsNotNone(decide().error)

    def test_single_step_flow(self):
        for kw in ({'actor_is_l1': True}, {'actor_is_l2': True}, {'actor_is_officer': True}):
            d = decide(**kw)
            self.assertIsNone(d.error)
            self.assertEqual((d.new_status, d.stage), ('validate', 'final'))

    def test_auto_approval_flow_uses_single_step_rules(self):
        self.assertEqual(decide(flow=wf.FLOW_NONE, actor_is_l1=True).new_status, 'validate')

    def test_refuse_by_any_authorised_approver_at_any_stage(self):
        for kw in ({'actor_is_l1': True}, {'actor_is_l2': True}, {'actor_is_officer': True}):
            d = decide(action='refuse', flow=wf.FLOW_DOUBLE, first_approved=True, **kw)
            self.assertEqual((d.new_status, d.stage), ('refuse', 'refuse'))

    # ----- two-level flow
    def test_double_first_step_only_records_first_approval(self):
        d = decide(flow=wf.FLOW_DOUBLE, actor_is_l1=True)
        self.assertEqual((d.new_status, d.stage), ('confirm', 'first'))   # still waiting!

    def test_double_l2_cannot_skip_the_first_step(self):
        d = decide(flow=wf.FLOW_DOUBLE, actor_is_l2=True)
        self.assertIsNotNone(d.error)

    def test_double_final_step_by_l2(self):
        d = decide(flow=wf.FLOW_DOUBLE, first_approved=True, actor_is_l2=True)
        self.assertEqual((d.new_status, d.stage), ('validate', 'final'))

    def test_double_l1_cannot_give_the_final_approval(self):
        d = decide(flow=wf.FLOW_DOUBLE, first_approved=True, actor_is_l1=True)
        self.assertIsNotNone(d.error)

    def test_double_same_person_cannot_do_both_steps(self):
        d = decide(flow=wf.FLOW_DOUBLE, first_approved=True, actor_is_officer=True,
                   actor_is_first_approver=True)
        self.assertIsNotNone(d.error)

    def test_double_officer_can_finish_after_someone_else_did_step_one(self):
        d = decide(flow=wf.FLOW_DOUBLE, first_approved=True, actor_is_officer=True)
        self.assertEqual(d.stage, 'final')

    def test_double_admin_override_completes_in_one_go(self):
        d = decide(flow=wf.FLOW_DOUBLE, actor_is_admin=True)
        self.assertEqual((d.new_status, d.stage), ('validate', 'final'))


class LeaveViewSecurityTests(SimpleTestCase):
    """Fix #6: approvals are POST-only (no state change through a GET link)."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_request_action_rejects_get(self):
        from leave.views import leave_request_action
        for path_action in ('validate', 'refuse'):
            request = self.factory.get(f'/time-off/request/1/action/?action={path_action}')
            with patch('leave.views.get_object_or_404') as lookup:
                response = leave_request_action(request, 1)
            self.assertEqual(response.status_code, 405)
            lookup.assert_not_called()

    def test_allocation_action_rejects_get(self):
        from leave.views import leave_allocation_action
        request = self.factory.get('/time-off/allocation/1/action/?action=validate')
        self.assertEqual(leave_allocation_action(request, 1).status_code, 405)
