from tags.models import Tag
from django.forms import MultipleChoiceField

def get_tags_from_valid_form(form):
    topic_tags = form.cleaned_data.pop('topic_tags')
    type_tags = form.cleaned_data.pop('type_tags')
    goal_tags = form.cleaned_data.pop('goal_tags')
    tags = topic_tags + type_tags + goal_tags
    return tags, form

def add_tags_to_object(object, tags):
    new_tags = set([Tag.objects.get(pk=tag) for tag in tags])
    old_tags = set(object.tags.all())
    for tag in new_tags.difference(old_tags): # for new tags
        object.tags.add(tag)
    for tag in old_tags.difference(new_tags): # for tags no longer there
        object.tags.remove(tag)

def add_tag_fields_to_form(form_fields, instance, formtype):
    '''Adds type, topic and goal fields to an Action, Slate or Profile form'''

    form_fields['type_tags'] = MultipleChoiceField(label="Types of action", required=False,
        choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="type")],
        help_text="Don't see the type of action you need?  Request a new action type <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")

    form_fields['topic_tags'] = MultipleChoiceField(label="Topics", required=False,
        choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="topic")],
        help_text="Don't see the topic you need?  Request a new topic <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")

    form_fields['goal_tags'] =  MultipleChoiceField(label="Goals", required=False,
        choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="goal")],
        help_text="Don't see the goal you need?  Request a new goal <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")

    if formtype != "create":
        form_fields['type_tags'].initial = [tag.pk for tag in instance.tags.filter(kind="type")]
        form_fields['topic_tags'].initial = [tag.pk for tag in instance.tags.filter(kind="topic")]
        form_fields['goal_tags'].initial = [tag.pk for tag in instance.tags.filter(kind="goal")]

    return form_fields
