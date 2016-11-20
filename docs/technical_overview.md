# Technical overview

This project uses Django 1.10.3.

- The site uses Postgres for its database.
- Unit tests use the Django test runner `python manage.py test`.
- Functional tests use Selenium.

## Project Structure

Directories:

- `mysite`: contains the main Django project and landing page
- `profiles`: Django app for user profiles
- `actions`: Django app for actions that users can add or select
- `functional_tests`: Tests using Selenium

## Data models

`actions`:
- `Action`: a task that the user can do
- `ActionTopic`: helper model used by Action
- `ActionType`: helper model used by Action
- `Slate`: a collection of actions a user can take on a particular cause
- `SlateActionRelationship`: defines relationship between a slate
   and an action

`profiles`:
- `Profile`: user information
- `Relationship`: basic data for all relationships
- `ProfileActionRelationship`: defines relationship between a profile
   and an action
- `PrivacyDefaults`: default privacy for a profile

## Glossary

- action: a task that the user can do to help change the world
- profile: information about a user
- slate: 
- slug: used when creating a URL to access a particular page or function
