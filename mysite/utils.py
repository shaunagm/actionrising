PRIVACY_CHOICES = (
    ('pub', 'Visible to Public'),
    ('sit', 'Visible Sitewide'),
    ('fol', 'Visible to Buddies and Those You Follow'),
    ('bud', 'Visible to Buddies'),
    ('you', 'Only Visible to You'),
    ('inh', 'Inherit'),
)

STATUS_CHOICES = (
    ('cre', 'In creation'),
    ('rea', 'Open for action'),
    ('fin', 'Finished'),
    ('wit', 'Withdrawn'),
)

INDIVIDUAL_STATUS_CHOICES = (
    ('sug', 'Suggested to you'),
    ('ace', 'Accepted'),
    ('don', 'Done'),
    ('wit', 'Rejected'),
)

PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('med', 'Medium'),
    ('hig', 'High'),
    ('eme', 'Emergency'),
)
