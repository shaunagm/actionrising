# Contributing to ActionRising

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to ActionRising, which
is hosted in the [ActionRising Organization](https://github.com/shaunagm/actionrising)
on GitHub. These are just guidelines for the community. Use your best
judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[What should I know before I get started?](#what-should-i-know-before-i-get-started)
  * [Code of Conduct](#code-of-conduct)
  * [ActionRising and Packages](#actionrising-and-packages)
  * [ActionRising Design Decisions](#design-decisions)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## What should I know before I get started?

### Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report
unacceptable behavior to the maintainers.

### ActionRising and Packages

ActionRising is an open source project to help communities share information
and coordinate helpful action within their community.

ActionRising is developed using Django.

### Design Decisions

When we make a significant decision in how we maintain the project and what
we can or cannot support, we will document it in the
[ActionRising repository](https://github.com/shaunagm/actionrising). If you
have a question around how we do things, check to see if it is documented
there. If it is *not* documented there, please open a new issue and ask your
question.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ActionRising.
Following these guidelines helps maintainers and the community understand
your report :pencil:, reproduce the behavior :computer: :computer:, and find
related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report)
as you might find out that you don't need to create one. When you are
creating a bug report, please
[include as many details as possible](#how-do-i-submit-a-good-bug-report). 
Fill out an issue report as thoroughly as possible.

#### Before Submitting A Bug Report

* **Check the documentation.** You might be able to find the cause of the
problem and fix things yourself. Most importantly, check if you can reproduce
the problem in the latest version of ActionRising

* **Perform a search of the issues** to see if the problem has already been
reported. If it has, add a comment to the existing issue instead of opening a
new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/).
Create an issue on the ActionRising repository.

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

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for
ActionRising, including completely new features and minor improvements to
existing functionality. Following these guidelines helps maintainers and the
community understand your suggestion :pencil: and find related
suggestions :mag_right:.

Before creating enhancement suggestions, please check
[this list](#before-submitting-an-enhancement-suggestion) as you might find
out that you don't need to create one. When you are creating an enhancement
suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion).
Fill in an issue, including the steps that you imagine you would take if the
feature you're requesting existed.

#### Before Submitting An Enhancement Suggestion

* **Check the documentation** for tips — you might discover that the enhancement
  is already available.
* **Perform a [cursory search](https://github.com/issues?q=+is%3Aissue+user%3Aactionrising)**
  to see if the enhancement has already been suggested. If it has, add a
  comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

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

### Your First Code Contribution

Unsure where to begin contributing to Atom? You can start by looking through
the issues

### Pull Requests

* Fill in [the required template](PULL_REQUEST_TEMPLATE.md)
* Include screenshots and animated GIFs in your pull request whenever possible.
* Document new code based on the
  [Documentation Styleguide](#documentation-styleguide)
* End files with a newline.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally

### Documentation Styleguide

* Use Sphinx.
* Use ReStructuredText or [Markdown](https://daringfireball.net/projects/markdown).


## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and
pull requests. Please open an issue if you have suggestions for new labels.

*This Contributing guide is inspired by the `CONTRIBUTING.md` developed by the
Atom community.*