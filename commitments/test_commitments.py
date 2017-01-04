import datetime, pytz
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from django.utils import timezone
from django.contrib.auth.models import User
from commitments.models import Commitment
from commitments.forms import CommitmentForm
from profiles.models import ProfileActionRelationship, Relationship
from actions.models import Action

###################
### Test models ###
###################

class TestCommitmentMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile,
            action=self.action)
        self.commitment = Commitment.objects.create(profile=self.buffy.profile,
            action=self.action)

    def test_days_past_start(self):
        self.assertEqual(self.commitment.days_past_start(), 0)
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=14)
        self.commitment.save()
        self.assertEqual(self.commitment.days_past_start(), 14)

    def test_days_given(self):
        self.assertEqual(self.commitment.days_given(), 51)
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=10)
        self.commitment.save()
        self.assertEqual(self.commitment.days_given(), 51)  # Changing start time shouldn't change days given
        self.commitment.tries = 1
        self.commitment.save()
        self.assertEqual(self.commitment.days_given(), 37)

    def test_reopen_active_commitment_as_active(self):
        self.commitment.status = "clo"
        self.commitment.save()
        self.commitment.reopen()
        self.assertEqual(self.commitment.status, "active")

    def test_reopen_waiting_commitment_as_waiting(self):
        self.commitment.status = "clo"
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=10)
        self.commitment.save()
        self.commitment.reopen()
        self.assertEqual(self.commitment.status, "waiting")

    def test_reopen_expired_commitment_as_expired(self):
        self.commitment.status = "clo"
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=80)
        self.commitment.save()
        self.commitment.reopen()
        self.assertEqual(self.commitment.status, "expired")

    def test_set_to_active_if_ready(self):
        self.assertEqual(self.commitment.status, "waiting")
        self.commitment.set_to_active_if_ready()
        self.assertEqual(self.commitment.status, "active")

    def test_dont_set_to_active_if_not_ready(self):
        self.assertEqual(self.commitment.status, "waiting")
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=10)
        self.commitment.save()
        self.commitment.set_to_active_if_ready()
        self.assertEqual(self.commitment.status, "waiting")

    def test_calculate_notification_dates(self):
        date1 = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=7)
        date2 = date1 + datetime.timedelta(days=7)
        date3 = date2 + datetime.timedelta(days=7)
        self.assertEqual(self.commitment.calculate_notification_dates(),
            [date1.date(), date2.date(), date3.date()])

    def test_calculate_notification_dates_with_alt_start_and_tries(self):
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=10)
        self.commitment.tries = 2
        self.commitment.save()
        date1 = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=10) + datetime.timedelta(days=7)
        date2 = date1 + datetime.timedelta(days=7)
        self.assertEqual(self.commitment.calculate_notification_dates(), [date1.date(), date2.date()])

    def test_get_buddies(self):
        self.assertFalse(self.commitment.get_buddies())
        willow = User.objects.create(username="thewitch", email="willow@willow.com")
        giles = User.objects.create(username="giles", email="giles@giles.com")
        self.commitment.buddies = "[u'" + str(willow.profile.pk) + "', u'" + str(giles.profile.pk) + "']"
        self.commitment.save()
        self.assertEqual(self.commitment.get_buddies(), [willow.profile, giles.profile])

    def test_get_offsite_buddies(self):
        self.assertFalse(self.commitment.get_offsite_buddies())
        self.commitment.offsite_buddies = "[buffy@buffy.com,faith@faith.com]"
        self.commitment.save()
        self.assertEqual(self.commitment.get_offsite_buddies(), ['buffy@buffy.com', 'faith@faith.com'])

    def test_collect_buddy_info(self):
        self.assertFalse(self.commitment.collect_buddy_info())
        # Add on-site buddies
        willow = User.objects.create(username="thewitch", email="willow@willow.com")
        giles = User.objects.create(username="giles", email="giles@giles.com")
        self.commitment.buddies = "[u'" + str(willow.profile.pk) + "', u'" + str(giles.profile.pk) + "']"
        # Add off-site buddies
        self.commitment.offsite_buddies = "[buffy@buffy.com,faith@faith.com]"
        self.commitment.save()
        # Tests
        self.assertEqual(self.commitment.collect_buddy_info(), [
            { 'email': None, 'user': willow.profile },
            { 'email': None, 'user': giles.profile },
            { 'email': 'buffy@buffy.com', 'user': None },
            { 'email': 'faith@faith.com', 'user': None}])

    def test_hold_accountable(self):
        self.commitment.hold_accountable()
        self.assertEqual(len(mail.outbox), 0)
        # Add on-site buddies
        willow = User.objects.create(username="thewitch", email="willow@willow.com")
        giles = User.objects.create(username="giles", email="giles@giles.com")
        self.commitment.buddies = "[u'" + str(willow.profile.pk) + "', u'" + str(giles.profile.pk) + "']"
        # Add off-site buddies
        self.commitment.offsite_buddies = "[buffy@buffy.com,faith@faith.com]"
        self.commitment.save()
        self.commitment.hold_accountable()
        self.assertEqual(len(mail.outbox), 4)

    def test_hold_accountable_if_time(self):
        # Add some buddies
        self.commitment.offsite_buddies = "[buffy@buffy.com,faith@faith.com]"
        self.commitment.save()
        # It's not time yet
        self.commitment.hold_accountable_if_time()
        self.assertEqual(len(mail.outbox), 0)
        # Set it so we're a week after start emails
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=7)
        self.commitment.save()
        self.commitment.hold_accountable_if_time()
        self.assertEqual(len(mail.outbox), 2)
        # Set it to far in the past, and test that status turns to expired and doesn't send emails
        mail.outbox = [] # clear
        self.commitment.start_emails = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=80)
        self.commitment.save()
        self.commitment.hold_accountable_if_time()
        self.assertEqual(self.commitment.status, "expired")
        self.assertEqual(len(mail.outbox), 0)

##################
### Test forms ###
##################

class TestCommitmentForm(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        Relationship.objects.create(person_A=self.buffy.profile, person_B=self.faith.profile)

    def test_initialize_create_form(self):
        initial_form = CommitmentForm(user=self.buffy, action=self.action)
        self.assertEqual(initial_form.profile, self.buffy.profile)
        self.assertEqual(initial_form.action, self.action)
        self.assertEqual(initial_form.fields['buddies'].choices, [(self.faith.pk, self.faith.profile)])

    def test_initialize_update_form(self):
        Commitment.objects.create(profile=self.buffy.profile, action=self.action)
        initial_form = CommitmentForm(user=self.buffy, action=self.action)
        self.assertEqual(initial_form.profile, self.buffy.profile)
        self.assertEqual(initial_form.action, self.action)
        self.assertEqual(initial_form.fields['buddies'].choices, [(self.faith.pk, self.faith.profile)])
