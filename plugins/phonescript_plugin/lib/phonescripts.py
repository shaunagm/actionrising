from operator import itemgetter
from sunlight.services.congress import Congress
from sunlight import config, errors

from django.contrib.contenttypes.models import ContentType
from plugins.location_plugin.models import Location
from plugins.phonescript_plugin.models import PhoneScript, ScriptMatcher, Legislator

# TODO: for the love of god, pick "rep" or "leg" as shorthand and stick with it

#####################################
### Run when user accesses action ###
#####################################

### Get representatives/legislators

def get_reps_from_location(location):
    # TODO: add reps to Location object, so they don't need to be looked up each time?
    congress_api = Congress(use_https=False)
    try:
        legislators = congress_api.locate_legislators_by_lat_lon(location.lat, location.lon)
        return legislators
    except errors.SunlightException:
        print("Failure to get legislators")
        return None
    return None

def get_legislators_given_location(location):
    legs = []
    for rep in get_reps_from_location(location):
        leg = Legislator.objects.get(bioguide_id=rep['bioguide_id'])
        legs.append(leg)
    return legs

def get_reps_from_select(lookup):
    '''Note that the lookup query can only match the state or the district'''
    legs = []
    # Try state
    senators = Legislator.objects.filter(state=lookup, title="Sen")
    if senators:
        return senators
    # Try district
    try:
        state, district = lookup.split("-")
        reps = Legislator.objects.filter(state=state, district=district)
        if reps:
            return reps
    except:
        return

### Get scripts

def get_universal_scripts(action):
    scripts = []
    phonescript_objects = PhoneScript.objects.filter(action=action, script_type="universal")
    for script in phonescript_objects:
        scripts += script.get_universal_scripts()
    return scripts

def get_default_scripts(action):
    scripts = []
    default_script = PhoneScript.objects.filter(action=action, script_type="default")
    if default_script:
        temp_script = default_script.first().get_default_script_with_no_rep_data()
        scripts.append(temp_script)
    scripts += get_universal_scripts(action)
    return sorted(scripts, key=itemgetter('priority'))

def get_all_scripts(action, location=None, legs=[]):
    scripts = []
    if not legs:
        legs = get_legislators_given_location(location)
    for leg in legs:
        script = leg.get_script_dict_given_action(action)
        if script:
            scripts.append(script)
    scripts += get_universal_scripts(action)
    # TODO: handle duplications between universal and constituent scripts
    # TODO: Switch priority choices to enum
    return sorted(scripts, key=itemgetter('priority'))

### Misc

def get_user_status(user):
    if not user.is_authenticated():
        return "Anon", False
    ctype = ContentType.objects.get_for_model(user.profile)
    location = Location.objects.filter(content_type=ctype, object_id=user.profile.pk).first()
    if not location or not location.state or not location.district:
        return "Data Missing", False
    return True, location

###############################
### Run when action is made ###
###############################

def create_legislators():
    congress_api = Congress(use_https=False)
    try:
        leg_dict = {}
        legislators = congress_api.legislators(per_page="all")
        for leg in legislators:
            Legislator.objects.create(bioguide_id=leg['bioguide_id'],
                first_name=leg['first_name'], last_name=leg['last_name'],
                title=leg['title'], phone=leg['phone'], state=leg['state'],
                district=leg['district'], party=leg['party'])
    except errors.SunlightException:
        print("Failure to get legislators")
        return None
    return Legislator.objects.all()

def get_legislators():
    legislator_objects = Legislator.objects.all()
    if len(legislator_objects) == 0:
        return create_legislators()
    else:
        return legislator_objects

def get_constituent_script_for_leg(leg, action):
    chosen_script = None
    for script in PhoneScript.objects.filter(action=action, script_type="constituent"):
        if script.does_rep_meet_conditions(leg):
            if not chosen_script:
                chosen_script = script
            else:
                if script.priority > chosen_script.priority:
                    chosen_script = script
    return chosen_script

def create_initial_script_matches(action):
    # When an action is first created, does the initial script matching
    # Called in PhoneScriptCreateView, right before redirect to success_url
    # NOTE: This only matches *constituent* scripts
    legislators = get_legislators()
    matches = ScriptMatcher.objects.filter(action=action)
    if matches:
        print("Unexpected script matches already exist: ", matches)
        return False
    else:
        for leg in legislators:
            script = get_constituent_script_for_leg(leg, action)
            ScriptMatcher.objects.create(action=action, legislator=leg, script=script)
    return True # Return true if successful
