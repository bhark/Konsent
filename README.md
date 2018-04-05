# Konsent

## About

> It's about time that we rethink the way we make decisions collectively. Konsent is my suggestion for an alternative to moderation, an alternative to hierarchy and unequal freedom. Konsent is a platform designed to help groups make decisions without hierarchy and representatives, built on anarchist values.

Here's a brief explanation of the concept:

When you register a new account, you link the account to a community, using a password provided to you by the community members. Once registered, you are given the ability to post new issues as well as participate in solving existing issues.

When a new issue is posted by a member of the union, it goes through three phases before being marked as solved. Here's a brief explanation of the three phases:

    Phase 1: Other members of the union can vote for issues they feel are relevant. When an issue has been voted for by half of the community, it will progress to phase 2.

    Phase 2: The community may suggest what they feel would be an appropriate solution to the issue at hand. They may also vote for other solutions that they agree with. After one day, the issue will progress to phase 3, bringing the solution with the most votes along with it.

    Phase 3: Community-members may veto the solution if they feel that the solution is deeply disturbing, and can in no way benefit the greater good of the community. If a community-member decides to veto a solution, he will have to provide a reason for the veto. The name of the member who vetoed will be visible to every community-member. If no veto has been put in place after one day, the issue will be marked as solved, and the solution will be carried out.

The concept of Konsent is just as much under development as the code-base, and everything is potentially subject to change. If you have any ideas on how we could improve the concept, share them in a new post on /f/konsent.

## Installation

Konsent is written in Python, using Flask. Before you can run Konsent on your own machine, three things need to be configured:

- The MySQL database. Simply import the database schema from `konsent.sql` and change the database credentials on the first lines of `flask_app.py`. This can be done in PHPMyAdmin simply by clicking `import` and choosing `konsent.sql`, or using the MySQL command line: `mysql -u <username> -p konsent < konsent.sql`

- Install Python. Konsent is written in Python 3, which can be installed from [the official Python website](https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz).

- Install the required Python packages. The easiest way to install Python packages is with Pip, which comes with Python by default. The packages required to run Konsent are: `flask, flask-mysqldb, wtforms, passlib, functools, datetime`. To install with pip: `pip install datetime flask flask-mysqldb wtforms passlib functools`. Some of these packages may already be installed, if so, just skip those.

When everything is ready to go, open up a command line (terminal, konsole, command prompt or something along those lines - depends on your OS), `git clone` this repository, `cd` to the repository and start `flask_app.py` using Python: `python flask_app.py`. If you want to adjust some settings (such as the resting time for a post in phase 2 and 3), you can do so on one of the first lines in `flask_app.py`.

## How to contribute

You don't have to know anything about programming or the likes to contribute to Konsent - developing the concept further is currently just as important. In the future, discussion and concept development will probably happen on the subraddle /f/konsent, on Raddle.me. Until then we can use GitHub's issues.

Contributing to the code-base is easy if you know Python and the basics of Git, and there's lots to be done. Simply install all the dependencies, as explained in the chapter above, grab your favorite code editor, take a look at the open issues and fire away. We're following the branching model explained [here](https://nvie.com/posts/a-successful-git-branching-model/) loosely. We're following the [PEP8](https://pep8.org/) style guide.

You can ship your changes pretty much however you want, although a good old pull-request is preferred.

## Changelog

### v. 2.0a

- Got rid of "display name" and made some rules for usernames

- Buffed up password storing security (replaced hashlib with bcrypt)

- Implemented CSRF (Cross-site request forgery) protection

- Added automated testing

- Enforced better passwords

- Refactored everything to comply with PEP8

- Restructured the whole project

- Switched to ORM (SQLAlchemy)

- Smashed a ton of bugs
