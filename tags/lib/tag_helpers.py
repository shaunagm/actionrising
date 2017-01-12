from tags.models import Tag

def get_tags_from_valid_form(form):
    topic_tags = form.cleaned_data.pop('topic_tags')
    type_tags = form.cleaned_data.pop('type_tags')
    goal_tags = form.cleaned_data.pop('goal_tags')
    tags = topic_tags + type_tags + goal_tags
    return tags, form

def add_tags_to_object(object, tags):
    if object.__class__.__name__ == "Action":
        for tag in tags:
            tag_object = Tag.objects.get(pk=tag)
            object.action_tags.add(tag_object)
    if object.__class__.__name__ == "Slate":
        for tag in tags:
            tag_object = Tag.objects.get(pk=tag)
            object.slate_tags.add(tag_object)
    if object.__class__.__name__ == "Profile":
        for tag in tags:
            tag_object = Tag.objects.get(pk=tag)
            object.profile_tags.add(tag_object)
