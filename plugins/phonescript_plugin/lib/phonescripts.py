from operator import itemgetter
from sunlight.services.congress import Congress
from sunlight import config, errors
from itertools import chain

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from plugins.location_plugin.models import Location
from plugins.phonescript_plugin.models import (PhoneScript, ScriptMatcher, Legislator,
    TypeChoices)

# TODO: for the love of god, pick "rep" or "leg" as shorthand and stick with it

#####################################
### Run when user accesses action ###
#####################################

### Get representatives/legislators

def get_user_reps_from_location(location):
    # TODO: add reps to Location object, so they don't need to be looked up each time?
    congress_api = Congress(use_https=False)
    try:
        legislators = congress_api.locate_legislators_by_lat_lon(location.lat, location.lon)
        return legislators
    except errors.SunlightException:
        print("Failure to get legislators")
        return None
    return None

def get_user_legislators_given_location_string(location):
    legs = []
    for rep in get_user_reps_from_location(location):
        leg = Legislator.objects.get(bioguide_id=rep['bioguide_id'])
        legs.append(leg)
    return legs

def get_user_legislators_given_location_object(location):
    legs = []
    senators = Legislator.objects.filter(state=location.state, title="Sen")
    reps = Legislator.objects.filter(state=location.state, district=location.get_district_number(), title="Rep")
    return list(chain(senators, reps))

def get_user_legislators(location):
    if location.__class__.__name__ == Location:
        legs = get_user_legislators_given_location_object(location)
    else:
        legs = get_user_legislators_given_location_string(location)
    return legs

def get_reps_from_select(lookup):
    legs = []
    # Try state
    senators = Legislator.objects.filter(state=lookup, title="Sen")
    if senators:
        return senators
    # Try district
    try:
        state, district = lookup.split("-")
        reps = Legislator.objects.filter(Q(state=state, title="Sen") | Q(state=state, district=district, title="Rep"))
        if reps:
            return reps
    except:
        return

### Get scripts

def get_constituent_scripts(action, legs):
    return [leg.get_script_dict_given_action(action) for leg in legs
        if leg.get_script_dict_given_action(action) is not None]

def get_universal_scripts(action):
    scripts = []
    phonescript_objects = PhoneScript.objects.filter(action=action)
    for script in phonescript_objects:
        universal_scripts = script.get_universal_scripts()
        if universal_scripts:
            scripts += universal_scripts
    return scripts

def remove_duplicate_scripts(constituent_scripts, universal_scripts):
    scripts = list(constituent_scripts)
    for u_script in universal_scripts:
        no_conflict = True
        for index, c_script in enumerate(constituent_scripts):
            if u_script['rep'] == c_script['rep']:
                if u_script['priority'] > c_script['priority']:
                    # replace script if priority of universal script is higher
                    scripts[index] = u_script
                    scripts[index]['constituent'] = True
                no_conflict = False
                break
        if no_conflict:
            scripts.append(u_script)
    return scripts

def get_all_scripts(action, location=None, legs=[]):
    legs = get_user_legislators(location) if not legs else legs
    constituent_scripts = get_constituent_scripts(action, legs)
    universal_scripts = get_universal_scripts(action)
    scripts = remove_duplicate_scripts(constituent_scripts, universal_scripts)
    return sorted(scripts, key=itemgetter('priority'), reverse=True)

def get_default_scripts(action):
    '''Called by view, gets defaults when user is not logged in or has no location specified'''
    scripts = []
    default_script = PhoneScript.objects.filter(action=action, script_type="default")
    if default_script:
        temp_script = default_script.first().get_default_script_with_no_rep_data()
        scripts.append(temp_script)
    scripts += get_universal_scripts(action)
    return sorted(scripts, key=itemgetter('priority'), reverse=True)

### Misc

def get_user_status(user):
    '''Returns either the location, or False + an explanation for the missing location'''
    if not user.is_authenticated:
        return False, "Anon"
    ctype = ContentType.objects.get_for_model(user.profile)
    location = Location.objects.filter(content_type=ctype, object_id=user.profile.pk).first()
    if not location or not location.state or not location.district:
        return False, "Data Missing"
    return location, []

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
            sm = ScriptMatcher.objects.create(action=action, legislator=leg)
            script = get_constituent_script_for_leg(leg, action)
            sm.script = script
            sm.save()
    return True # Return true if successful

def update_all_script_matches(action):
    matches = ScriptMatcher.objects.filter(action=action)
    for match in matches:
        match.refresh_script()
