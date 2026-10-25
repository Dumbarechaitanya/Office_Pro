"""
Leave business rules, kept free of Django/ORM code so they are easy to unit-test.

Approval flows (decided by LeaveType.approval_type):

* none   - "No Validation": the request is approved automatically when it is submitted.
* single - "By Time Off Officer" (default): ONE approval by the reporting manager / L1 / L2
           approver or a Time Off officer.
* double - "By Approver and Officer": TWO steps.
             step 1  Level-1 approver (reporting manager) or an officer
             step 2  Level-2 executive approver or an officer -- a *different* person than step 1
           An Administrator may complete both steps at once (override).

Nobody can approve or refuse their own request, and only requests that are still waiting
('confirm') can be approved or refused -- a refused request can no longer be re-approved.
"""
from datetime import timedelta
from decimal import Decimal, InvalidOperation

FLOW_NONE = 'none'
FLOW_SINGLE = 'single'
FLOW_DOUBLE = 'double'

PENDING_STATUSES = ('confirm', 'Pending')


def normalize_approval_type(value):
    """Map the stored approval_type (code or human label) to one of the FLOW_* constants."""
    v = (value or '').strip().lower().replace('_', ' ')
    if v in ('no validation', 'none'):
        return FLOW_NONE
    if v in ('both', 'by approver and officer') or ('approver' in v and 'officer' in v):
        return FLOW_DOUBLE
    return FLOW_SINGLE


# --------------------------------------------------------------------------- dates / duration
def count_working_days(start, end, holiday_dates=(), weekend_days=(5, 6)):
    """Number of working days in [start, end], skipping weekends and the given holiday dates."""
    if end < start:
        return 0
    holiday_dates = set(holiday_dates)
    days = 0
    d = start
    while d <= end:
        if d.weekday() not in weekend_days and d not in holiday_dates:
            days += 1
        d += timedelta(days=1)
    return days


def resolve_duration(start, end, client_duration, holiday_dates=()):
    """
    The server decides the duration -- never trust the browser.
      * single day  -> 0.5 (half day) or 1 is accepted from the form, anything else is rejected
      * several days -> number of working days in the range
    Returns (Decimal duration | None, error | None).
    """
    working = count_working_days(start, end, holiday_dates)
    if working == 0:
        return None, 'The selected dates contain no working days (weekends and holidays are excluded).'
    if start == end:
        try:
            requested = Decimal(str(client_duration))
        except (InvalidOperation, TypeError, ValueError):
            return None, 'Invalid duration.'
        if requested not in (Decimal('0.5'), Decimal('1'), Decimal('1.0'), Decimal('0.50'), Decimal('1.00')):
            return None, 'A single-day request can only be a half day (0.5) or a full day (1).'
        return requested, None
    return Decimal(working), None


def validate_leave_request(start, end, today, *, can_backdate=False, overlap_exists=False,
                           requires_allocation=False, available_balance=None, duration=None):
    """Returns a list of human readable errors (empty list == valid)."""
    errors = []
    if end < start:
        errors.append('The end date cannot be before the start date.')
        return errors
    if start < today and not can_backdate:
        errors.append('Back-dated leave is not allowed. Ask an administrator to approve past-dated leave.')
    if overlap_exists:
        errors.append('You already have a pending or approved leave request that overlaps these dates.')
    if requires_allocation and available_balance is not None and duration is not None:
        if Decimal(duration) > Decimal(available_balance):
            errors.append(f'Insufficient leave balance: {available_balance} day(s) available, {duration} requested.')
    return errors


# --------------------------------------------------------------------------- approval decisions
class Decision:
    """Outcome of an approve/refuse attempt."""
    def __init__(self, error=None, new_status=None, stage=None):
        self.error = error          # message to show, or None
        self.new_status = new_status  # 'validate' | 'refuse' | 'confirm' (waiting for step 2)
        self.stage = stage          # 'first' | 'final' | 'refuse' | None

    def __repr__(self):
        return f'Decision(error={self.error!r}, new_status={self.new_status!r}, stage={self.stage!r})'


def decide(*, action, status, flow, first_approved, actor_is_self, actor_is_l1, actor_is_l2,
           actor_is_officer, actor_is_admin, actor_is_first_approver=False):
    """
    Decide what an approve ('validate') / 'refuse' click does.  Pure function -> unit-testable.
    """
    if status not in PENDING_STATUSES:
        return Decision(error='This request has already been processed and can no longer be changed.')
    if actor_is_self:
        return Decision(error='You cannot approve or refuse your own request.')
    if action not in ('validate', 'refuse'):
        return Decision(error='Unknown action.')

    authorised = actor_is_l1 or actor_is_l2 or actor_is_officer or actor_is_admin
    if not authorised:
        return Decision(error='Permission Denied: you may only approve leave for employees under your supervision.')

    if action == 'refuse':
        return Decision(new_status='refuse', stage='refuse')

    # ---- action == 'validate'
    if flow in (FLOW_NONE, FLOW_SINGLE):
        return Decision(new_status='validate', stage='final')

    # flow == FLOW_DOUBLE
    if actor_is_admin:
        return Decision(new_status='validate', stage='final')   # admin override
    if not first_approved:
        if actor_is_l1 or actor_is_officer:
            return Decision(new_status='confirm', stage='first')
        return Decision(error='Waiting for first-level approval by the reporting manager.')
    # second step
    if actor_is_first_approver:
        return Decision(error='The final approval must be given by a different person than the first-level approver.')
    if actor_is_l2 or actor_is_officer:
        return Decision(new_status='validate', stage='final')
    return Decision(error='Waiting for final approval by the Level-2 (executive) approver or a Time Off officer.')
