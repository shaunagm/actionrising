# Contributing to ActionRising

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

This guide is a reference for contributors to the project. There’s a lot of information in it, so please don’t hesitate to ask for help! If you’re new to the project, don’t worry - you don’t have to understand the whole process at once. Reach out to the project leads and we’ll help you walk through it, answer your questions, and remind you gently if you miss anything.

The best way to keep in touch with the community is via the [ActionRising Slack](https://actionrising.slack.com/). Request an invite from actionrisingsite@gmail.com and come say hello! Current project leads/mentors are:

  * Shauna (@shauna on Slack, @shaunagm on Github)
  * Presley (@presley on Slack, @presleyp on Github)

If you find any mistakes in this guide, or have suggestions for improvement, please feel free to submit a pull request!

#### Table Of Contents

[Overview](#overview)

[Ways to Contribute](#ways-to-contribute)
  * [I want to report a bug](#i-want-to-report-a-bug)
  * [I want to request a feature](#i-want-to-request-a-feature)
  * [I want to make a (non-urgent) change](#i-want-to-make-a-non-urgent-change)
  * [I want to fix an urgent bug](#i-want-to-fix-an-urgent-bug)
  * [I want to improve the documentation](#i-want-to-improve-the-documentation)        

[Guides](#guides)
  * [Styleguides](#styleguides)
    * [Git Commit Messages](#git-commit-messages)
    * [Documentation Styleguide](#documentation-styleguide)
  * [Admin Guides](#admin-gudies)
    * [Release Guide](#release-guide)
    * [Hotfix Guide](#hotfix-guide)
  * [Miscellaneous Guides](#miscellaneous-guides)
    * [Guidelines for Reporting a Bug](#guidelines-for-reporting-a-bug)
    * [Guidelines for Requesting a Feature](#guidelines-for-requesting-a-feature)
    * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Overview

Note: by participating in our community, you implicitly agree to abide by our [Contributor Code of Conduct](http://contributor-covenant.org/version/1/2/0/).

The ActionRising community coordinates development in a few major ways:  

Most ideas for new features, user feedback, and bugs get added as issues to our [issue tracker](https://github.com/shaunagm/actionrising/issues). Don’t be afraid to add your ideas as a new issue!  Community admins review issues as they’re added. If there’s an important bug, we’ll label it as urgent and try to fix it right away.  Otherwise, it’ll probably sit around for a little while as folks discuss it. Eventually it will get an ‘accepted’ label, or it will be labeled ‘rejected’ and closed.

Every month or so, we get together to plan out the next [milestone](https://github.com/shaunagm/actionrising/milestones). These meetings are announced on the Slack and on the [contributor slate](https://actionrising.com/slates/slate/contribute-to-actionrising). During these meetings we touch base on what our priorities are, as specified in our [project roadmap](https://github.com/shaunagm/actionrising/wiki/ActionRising-Roadmap-(v.-2)).  With an eye to our priorities, we go through existing issues and grab the ones we think we’ll get to in the next month.  Sometimes we’ll add new issues as well!  We put those issues in the ‘to do’ section of our project kanban board.

The [kanban board](https://github.com/shaunagm/actionrising/projects/7) is another major tool for keeping track of who is doing what. Regardless of whether you participate in the milestone process, if you’re working on an issue, you should make sure it’s on the kanban board. You should also use the kanban board to find people whose work might conflict with yours and check in wit them.  See ["I want to make a (non-urgent) change"](#i-want-to-make-a-non-urgent-change) for details.

We use [this git branching model](http://nvie.com/posts/a-successful-git-branching-model/) for our workflow. Quick summary: we have two main branches, `master` and `develop`. `Master` is the branch that’s live on our production site. `Develop` has all the accepted features & bugfixes we want to eventually merge into `master`. Periodically (we aim for once a week) we make a release, merge  develop into master, and push those changes to the product site.  It’s more complicated than that, but you don't have to sweat the details. Just follow the instructions below for various kinds of contributions and, of course, you can always ask for help.

## Ways to Contribute

Pick one of the headings below to find out how to contribute. Want to do something else? Let us know! We’ll help you _and_ update this guide, which we want to cover all situations.

#### I want to report an issue

Before submitting a bug report, do a quick search in [the issue tracker](https://github.com/shaunagm/actionrising/issues) to see if the problem has already been reported. If it has, add a comment to the existing issue instead of opening a new one. If not, you can open a new issue. Please try to follow our [guidelines for reporting a bug](#guidelines-for-reporting-a-bug).  

If you're unsure of whether or not you've got a bug, feel free to ask for help on Slack.

#### I want to request a feature

Before submitting a feature request, do a quick search in [the issue tracker](https://github.com/shaunagm/actionrising/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one. If not, you can make a new issue. Please try to follow our [guidelines for requesting a feature](#guidelines-for-requesting-a-feature).  

If you have any questions, or want to talk about potential features more informally, feel free to bring it up on Slack.

#### I want to make a (non-urgent) change

Before making a change, you’ll want to check in with the community. To do this, look at the __in progress__ and __code review__ columns of the [kanban board](https://github.com/shaunagm/actionrising/projects/7) to see if anyone else is doing work that might overlap with what yours. If you find anyone, reach out to make sure your work doesn’t conflict! The best way to do this is to @ them on the issue you’re addressing or on an empty pull request. When in doubt, just @ everyone who has an issue in the ‘in progress’ and ‘code review’ columns. You should also always make sure to @ shauna, the project owner.  (A lot of small changes will just be @ing Shauna, which is totally fine.)

Once you get the go-ahead to start developing, you’ll want to make a feature branch:

`git checkout -b feature-myfeaturename develop`

(It's not really important what you call your feature branch, but if you remember to prefix it with feature- it makes our housekeeping a little easier.)

When your work is done, you can then submit a pull request against the `develop` branch (__not__ against `master`).  To do this, use the following command to push to the repository: `git push origin feature-myfeaturename`.  Then, you can use the Github interface to create a pull request. We've set up the repo to create pull requests against `develop` by default. Once you've created your pull request, request a review from Shauna, as well as any other contributors who have asked to be kept in the loop about your contribution.

If `develop` has changed while you were making your feature, you may need to "rebase" your branch.  This is especially likely for large changes that are done over days or weeks.  To rebase, do the following:

    `git fetch origin            # Gets most recent version from origin`
    `git rebase origin/develop   # Rebases onto develop branch`

For big changes, you may want to test on [stage](https://act-now-staging.herokuapp.com/). You can ask Shauna or Presley to do this for you, or if you think you’ll be sticking around and contributing again, we can set up a staging ground (“sandbox”) for you.

_If you run into trouble while working on an issue, please reach out via the slack and by mentioning people using @ in the Github issue you're working on.  You can also ask an admin to add a [blocked label](https://github.com/shaunagm/actionrising/labels/status%3A%20blocked)
to your issue.  This will make it easier for people to notice that you're stuck, and help you._

#### I want to fix an urgent bug

Sometimes, a change can’t wait to go through the above process. It needs to be fixed right away.

If you find an urgent bug, report the issue on Github and @ Shauna on the issue.  In order to get her attention quickly, please also ping her on Slack if you can.  

If you want to go ahead and fix the bug, make a hotfix branch:

`git checkout -b hotfix-mybugname master`

If you’re a regular contributor with your own sandbox, you can test your changes there.  Once you’re ready, submit a pull request against `master` (__not__ `develop`):

    `git fetch origin            # Gets most recent version from origin`
    `git rebase origin/master    # Rebases onto master branch`

(There won't usually be any changes to master for you to worry about with a hotfix, but it's a good habit to have, and there might be changes if multiple people are working on hotfixes simultaneously.)

Shauna will test first against stage, and then, if that looks good, push it live to production.  She’ll also take care of merging your hotfix into `develop` as well.  

Our practice is, when we find a bug, to make sure we add the tests that would have caught it.  So, many bugs will get a [tests label](https://github.com/shaunagm/actionrising/labels/tests) and remain open in the issue tracker after they've been fixed. You are very welcome to write and add these tests, which can be contributed as part of the hotfix (if you write them at the same time as your fix) or as part of a regular contribution (if you write the tests later).  You can also leave them for another community member to write if you only have time to do the fix itself.

#### I want to improve the documentation

We don’t yet have a documentation structure set up, so the best way to get involved with this is to @ shauna on slack, and we can chat about where we are in the process and how you can help.

## Guides

### Styleguides

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally

#### Documentation Styleguide

* Use Sphinx.
* Use ReStructuredText or [Markdown](https://daringfireball.net/projects/markdown).

### Admin Guides

#### Release Guide

_Note: this is based off of [this guide](http://nvie.com/posts/a-successful-git-branching-model/)._

Once you're ready to make a new release, create a branch with the new version number. We use 1.2 as an example version number.

`git checkout -b release-1.2 develop`

Bugfixes for issues found during release testing may be added to this branch, but new features must go to `develop`.

The release should be tested with the automated test suite (both unit and functional) and should also be tested manually on stage.  Once the tests pass, continue:

`git checkout master`
`git merge --no-ff release-1.2`
`git tag -a 1.2`

This merges the release into master and tags it with the release #.  It can then be pushed
to production (Heroku).

The release may include bug fixes, and needs to be merged back into develop as well:

`git checkout develop`
`git merge --no-ff release-1.2`

If merge conflicts are introduced, fix them and commit. Finally, delete the release branch:

`git branch -d release-1.2`

#### Hotfix Guide

_Note: this is based off of [this guide](http://nvie.com/posts/a-successful-git-branching-model/)._

We start by assuming a hotfix has been made according to [the above instructions](#i-want-to-fix-an-urgent-bug).  A fix has been made using a branch labeled hotfix-* that has been merged into master.  

Push the change to stage and, if it works, onto production.  If this does not successfully fix the issue, repeat above processes with new hotfix branches based off of master.  

Once the issue is successfully resolved, merge the hotfixes into the current `release` branch, if one exists, or if not, onto `develop`:

    `git checkout release-1.2` OR `git checkout develop`
    `git merge --no-ff hotfix-*`

Finally, delete the branch:

`git branch -d hotfix-*`

### Miscellaneous Guides

##### Guidelines for Reporting a Bug

Explain the problem and include additional details to help maintainers
reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details
  as possible. For example, start by explaining how you started ActionRising,
  e.g. which command exactly you used in the terminal, or how you started
  otherwise. When listing steps, **don't just say what you did, but explain
  how you did it**
* **Provide specific examples to demonstrate the steps**. Include links to
  files, or copy/pasteable snippets, which you use in those examples. If
  you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point
  out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the
  described steps and clearly demonstrate the problem.
* **If you're reporting that ActionRising crashed**, include a crash report
  with a stack trace from the operating system.
* **If the problem wasn't triggered by a specific action**, describe what you
  were doing before the problem happened and share more information using the
  guidelines below.

Provide more context by answering these questions:

* **Can you reproduce the problem?**
* **Did the problem start happening recently** (e.g. after updating to a new
  version of ActionRising) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem
  in an older version of ActionRising?** What's the most recent version in
  which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how
  often the problem happens and under which conditions it normally happens.
* If the problem is related to working with files (e.g. opening and editing files),
  **does the problem happen for all files and projects or only some?** Does
  the problem happen only when working with local or remote files (e.g. on
  network drives), with files of a specific type (e.g. only JavaScript or
  Python files), with large files or files with very long lines, or with files
  in a specific encoding? Is there anything else special about the files you
  are using?

Include details about your configuration and environment:

* **What's the name and version of the OS you're using**?
* **Which packages do you have installed?** You can get that list by running
  `pip list`.

#### Guidelines for Requesting a Feature

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/).
Create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as
  many details as possible.
* **Provide specific examples to demonstrate the steps**. Include
  copy/pasteable snippets which you use in those examples, as
  [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected
  to see instead** and why.
* **Include screenshots and animated GIFs** which help you demonstrate the
  steps.
* **Explain why this enhancement would be useful** to most users.
* **Specify which version of ActionRising you're using.**.
* **Specify the name and version of the OS you're using.**

#### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and
pull requests.  We are not terribly consistent about using labels, but we try.
If you have a request for a new label, ask in the #general channel in Slack.

__Issue domain/type__:
* [Architecture](https://github.com/shaunagm/actionrising/labels/architecture): how the codebase is constructed
* [Design](https://github.com/shaunagm/actionrising/labels/design): user experience and how the site appears
* [DevOps](https://github.com/shaunagm/actionrising/labels/devops): dependencies, settings, integrations, etc
* [Docs](https://github.com/shaunagm/actionrising/labels/docs): documentation
* [Tests](https://github.com/shaunagm/actionrising/labels/tests): testing of any kind

__Category of issue__:
* [Bug](https://github.com/shaunagm/actionrising/labels/bug): errors and problems
* [Enhancement](https://github.com/shaunagm/actionrising/labels/enhancement): improvements and new features

__State of issue__:
* Statuses:
  * [Triage](https://github.com/shaunagm/actionrising/labels/status%3A%20triage): needs someone to put it in one of the other statuses
  * [Accepted](https://github.com/shaunagm/actionrising/labels/status%3A%20accepted): we are working on or plan to work on this issue
  * [Blocked](https://github.com/shaunagm/actionrising/labels/status%3A%20blocked): someone is working on this and needs help!
  * [Declined](https://github.com/shaunagm/actionrising/labels/status%3A%20declined): we have decided not to work on this issue
* Priority:
  * [Urgent](https://github.com/shaunagm/actionrising/labels/priority%3A%20urgent)
  * [High](https://github.com/shaunagm/actionrising/labels/priority%3A%20high)
  * [Low](https://github.com/shaunagm/actionrising/labels/priority%3A%20low)

__Misc Labels__:
* [Refactoring](https://github.com/shaunagm/actionrising/labels/refactoring): for issues that
primarily deal with refactoring (rewriting and hopefully improving) part of the codebase
* [hypothetically-bite-sized](https://github.com/shaunagm/actionrising/labels/hypothetically%20bite-sized): should be a small task to work on (warning: it may be more complicated than it looks!)
* [Needs more thought](https://github.com/shaunagm/actionrising/labels/needs%20more%20thought): a proposed feature or change that needs continued thought & discussion

*This Contributing guide is inspired by the `CONTRIBUTING.md` developed by the
Atom community.*
