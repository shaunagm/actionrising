import mock
from django.test import TestCase

from actions.models import Action
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType

from plugins.phonescript_plugin.models import (PhoneScript, Legislator, ScriptMatcher,
    TypeChoices)
from plugins.phonescript_plugin.lib import phonescripts
from plugins.location_plugin.models import Location

###################
### Test Models ###
###################

class TestLegislatorModels(TestCase):

    def setUp(self):
        self.testing_user = User.objects.create(username="testing_user")
        self.leg = Legislator.objects.create(bioguide_id="M000133", first_name="Edward",
            last_name="Markey", party="d", title="sen", phone="202-224-2742", state="MA")
        self.action = Action.objects.create(title="ActionX", creator=self.testing_user)
        self.constituent_phonescript = PhoneScript.objects.create(action=self.action,
            content="Constituent script for ActionX", script_type=TypeChoices.constituent, party="d")

    def test_get_script_given_action_with_default(self):
        # With no matched script and no default specified, return nothing
        script = self.leg.get_script_given_action(self.action)
        self.assertEqual(script, None)
        # With default created + no script matched, should return default
        default_phonescript = PhoneScript.objects.create(action=self.action,
            content="Default script for ActionX", script_type=TypeChoices.default)
        script = self.leg.get_script_given_action(self.action)
        self.assertEqual(script, default_phonescript)
        # Match a script, return that
        sm = ScriptMatcher.objects.create(action=self.action, legislator=self.leg, script=self.constituent_phonescript)
        script = self.leg.get_script_given_action(self.action)
        self.assertEqual(script, self.constituent_phonescript)

class TestPhoneScriptModels(TestCase):

    def setUp(self):
        Legislator.objects.create(bioguide_id="M000133", first_name="Edward", last_name="Markey",
            party="d", title="sen", phone="202-224-2742", state="MA")
        Legislator.objects.create(bioguide_id="W000802", first_name="Sheldon", last_name="Whitehouse",
            party="d", title="sen", phone="202-224-292", state="RI")
        Legislator.objects.create(bioguide_id="C001071", first_name="Bob", last_name="Corker",
            party="", title="sen", phone="202-224-3344", state="TN")
        Legislator.objects.create(bioguide_id="C001037", first_name="Michael", last_name="Capuano",
            party="d", title="rep", phone="202-225-5111", state="MA", district="7")
        Legislator.objects.create(bioguide_id="L000562", first_name="Stephen", last_name="Lynch",
            party="d", title="rep", phone="202-225-8273", state="MA", district="8")
        Legislator.objects.create(bioguide_id="L000491", first_name="Frank", last_name="Lucas",
            party="r", title="rep", phone="202-225-5565", state="OK", district="3")
        self.testing_user = User.objects.create(username="testing_user")
        self.action = Action.objects.create(title="ActionX", creator=self.testing_user)

    def test_get_default_script_with_no_rep_data(self):
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.default)
        default_script = phonescript.get_default_script_with_no_rep_data()
        self.assertEqual(default_script['script_type'], 'default')
        self.assertEqual(default_script['content'], 'Phonescript for ActionX')

    def test_get_default_script_with_no_rep_data_wrong_type(self):
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.constituent)
        default_script = phonescript.get_default_script_with_no_rep_data()
        self.assertEqual(default_script, None)

    def test_set_always_reps(self):
        rep_pks = [int(leg.pk) for leg in Legislator.objects.all()[:2]]
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.constituent)
        phonescript.set_always_reps(rep_pks)
        self.assertEqual(phonescript.get_always_reps(), rep_pks)

    def test_get_universal_scripts(self):
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.universal)
        rep_pks = [int(leg.pk) for leg in Legislator.objects.all()[:2]]
        phonescript.set_always_reps(rep_pks)
        universal_scripts = phonescript.get_universal_scripts()
        self.assertEqual(len(universal_scripts), 2)
        self.assertEqual(universal_scripts[0]['script_type'], 'universal')

    def test_does_rep_meet_conditions_party_and_title(self):
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.constituent, rep_type="sen", party="d")
        dem_senator = Legislator.objects.get(last_name="Markey")
        self.assertEqual(phonescript.does_rep_meet_conditions(dem_senator), True)
        rep_senator = Legislator.objects.get(last_name="Corker")
        self.assertEqual(phonescript.does_rep_meet_conditions(rep_senator), False)
        dem_rep = Legislator.objects.get(last_name="Capuano")
        self.assertEqual(phonescript.does_rep_meet_conditions(dem_rep), False)
        rep_rep = Legislator.objects.get(last_name="Lucas")
        self.assertEqual(phonescript.does_rep_meet_conditions(rep_rep), False)

    def test_does_rep_meet_conditions_position(self):
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.constituent, position="for")
        markey = Legislator.objects.get(last_name="Markey")
        sm = ScriptMatcher.objects.create(action=self.action, legislator=markey, position="for")
        self.assertEqual(phonescript.does_rep_meet_conditions(markey), True)
        corker = Legislator.objects.get(last_name="Corker")
        ScriptMatcher.objects.create(action=self.action, legislator=corker, position="against")
        self.assertEqual(phonescript.does_rep_meet_conditions(corker), False)
        # Change phonescript to all, Corker should now meet conditions
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.constituent, position="all")
        self.assertEqual(phonescript.does_rep_meet_conditions(markey), True)
        self.assertEqual(phonescript.does_rep_meet_conditions(corker), True)

    def test_delete_script(self):
        pass

class TestScriptMatcherModels(TestCase):

    def test_refresh_script(self):
        pass

    def test_update_script_matcher_when_position_changes(self):
        pass

################
### Test lib ###
################

class TestPhoneScriptLib(TestCase):

    def setUp(self):
        self.testing_user = User.objects.create(username="testing_user")
        self.action = Action.objects.create(title="ActionX", creator=self.testing_user)
        self.user_with_location = User.objects.create(username="glorificus")
        # Update location for user
        ctype = ContentType.objects.get_for_model(self.user_with_location.profile)
        self.location = Location.objects.get(content_type=ctype, object_id=self.user_with_location.profile.pk)
        self.location.location = "Somerville, MA"
        self.location.save()

    def test_get_legislators(self):
        leg = Legislator.objects.all()
        self.assertEqual(len(leg), 0)
        leg = phonescripts.get_legislators()
        self.assertEqual(len(leg), 537)

    def test_get_constituent_script_for_leg(self):
        phonescripts.get_legislators()
        phonescript = PhoneScript.objects.create(action=self.action, content="High priority phonescript for ActionX",
            script_type=TypeChoices.constituent, party="d")
        markey = Legislator.objects.get(last_name="Markey")
        self.assertEqual(phonescripts.get_constituent_script_for_leg(markey, self.action), phonescript)

    def test_get_constituent_script_for_leg_with_different_priorities(self):
        phonescripts.get_legislators()
        phonescript1 = PhoneScript.objects.create(action=self.action, content="Low priority phonescript for ActionX",
            script_type=TypeChoices.constituent, party="d", priority="1")
        phonescript2 = PhoneScript.objects.create(action=self.action, content="High priority phonescript for ActionX",
            script_type=TypeChoices.constituent, party="d", priority="3")
        phonescript3 = PhoneScript.objects.create(action=self.action, content="Med priority phonescript for ActionX",
            script_type=TypeChoices.constituent, party="d", priority="2")
        markey = Legislator.objects.get(last_name="Markey")
        self.assertEqual(phonescripts.get_constituent_script_for_leg(markey, self.action), phonescript2)

    def test_create_initial_script_matches(self):
        script_for_dems = PhoneScript.objects.create(action=self.action, content="Dem script for ActionX",
            script_type=TypeChoices.constituent, party="d", priority="1")
        script_for_sens = PhoneScript.objects.create(action=self.action, content="Senator script for ActionX",
            script_type=TypeChoices.constituent, rep_type="sen", priority="3")
        default_script = PhoneScript.objects.create(action=self.action, content="Default script for ActionX",
            script_type=TypeChoices.default)
        created = phonescripts.create_initial_script_matches(self.action)
        self.assertEqual(created, True)
        self.assertEqual(len(ScriptMatcher.objects.filter(action=self.action)), 537)

    def test_update_all_script_matches(self):
        pass

    def test_get_user_status(self):
        # Test logged out user
        location, status = phonescripts.get_user_status(AnonymousUser())
        self.assertFalse(location)
        self.assertEqual(status, "Anon")
        # Test logged in user with no location
        location, status = phonescripts.get_user_status(self.testing_user)
        self.assertFalse(location)
        self.assertEqual(status, "Data Missing")
        # Test logged in user with location
        location, status = phonescripts.get_user_status(self.user_with_location)
        self.assertEqual(location.__class__.__name__, "Location")

    def test_get_constituent_scripts(self):
        pass

    def test_remove_duplicate_scripts(self):
        # Setup!
        phonescripts.get_legislators() # Start by populating legislators
        dem_phonescript = PhoneScript.objects.create(action=self.action, content="Dem script for ActionX",
            script_type=TypeChoices.constituent, party="d", priority="1") # Should match all three of the user's reps
        phonescripts.create_initial_script_matches(self.action)
        # Get constituent scripts for user
        legs = phonescripts.get_user_legislators_given_location_object(self.location)
        constituent_scripts = phonescripts.get_constituent_scripts(self.action, legs)
        self.assertEqual(len(constituent_scripts), 3)
        # Add in a universal script that covers one of the user's reps
        phonescript = PhoneScript.objects.create(action=self.action, content="Phonescript for ActionX",
            script_type=TypeChoices.universal)
        markey = Legislator.objects.get(last_name="Markey")
        corker = Legislator.objects.get(last_name="Corker")
        rep_pks = [int(leg.pk) for leg in Legislator.objects.filter()]
        phonescript.set_always_reps([int(markey.pk), int(corker.pk)])
        universal_scripts = phonescripts.get_universal_scripts(self.action)
        self.assertEqual(len(universal_scripts), 2)
        # Setup done, now to actually test!
        scripts = phonescripts.remove_duplicate_scripts(constituent_scripts, universal_scripts)
        self.assertEqual(len(scripts), 4)
        markey_script = [script for script in scripts if script['rep'] == markey][0]
        self.assertEqual(markey_script['script_type'], 'universal')

##################
### Test forms ###
##################

##################
### Test views ###
##################
