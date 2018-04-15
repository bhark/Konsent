# Konsent

## About

> It's about time that we rethink the way we make decisions collectively. Konsent is my suggestion for an alternative to moderation, an alternative to hierarchy and unequal freedom. Konsent is a platform designed to help groups make decisions without hierarchy and representatives, built on anarchist values.

Here's a brief explanation of the concept:

When you register a new account, you link the account to a community, using a password provided to you by the community members. Once registered, you are given the ability to post new issues as well as participate in solving existing issues.

When a new issue is posted by a member of the union, it goes through three phases before being marked as solved. Here's a brief explanation of the three phases:

- Phase 1: Other members of the union can vote for issues they feel are relevant. When an issue has been voted for by half of the community, it will progress to phase 2.

- Phase 2: The community may suggest what they feel would be an appropriate solution to the issue at hand. They may also vote for other solutions that they agree with. After one day, the issue will progress to phase 3, bringing the solution with the most votes along with it.

- Phase 3: Community-members may veto the solution if they feel that the solution is deeply disturbing, and can in no way benefit the greater good of the community. If a community-member decides to veto a solution, he will have to provide a reason for the veto. The name of the member who vetoed will be visible to every community-member. If no veto has been put in place after one day, the issue will be marked as solved, and the solution will be carried out.

The concept of Konsent is just as much under development as the code-base, and everything is potentially subject to change. If you have any ideas on how we could improve the concept, share them in a new post on /f/konsent.

## Installation

If you want to give Konsent a try on your local machine, here's how it's done. There's a setup script included, if it doesn't work properly you'll want to install manually.

**Automatic Installation**

- Install Python 3.

- Clone Konsent using git, `git clone https://github,cm/dellitsni/Konsent/` or download and unzip somewhere safe.

- Install dependencies by running `python setup.py install`.

- Start your MySQL/MariaDB server and create a new database called `konsent`.

- Populate the database by running `python konsent createdb`.

**Manual Installation**

- Install Python 3.

- Clone Konsent using git, `git clone https://github.com/dellitsni/Konsent/` or download and unzip somewhere safe.

- Use `pip` to install the dependencies: `pip install flask flask-mysqldb flaks-sqlalchemy wtforms bcrypt flask-login`. 

- Install `konsent` as a module by running `pip install konsent` in Konsent's parent folder. If you want to develop on Konsent, add the `-e` flag.

- Start your MySQL/MariaDB server and create a new database called `konsent`.

- Populate the database by running `python konsent createdb`.

**Running Konsent after installation**

Konsent has a few optional parameters. Execute from base directory using: `python konsent runserver -d [DATABASE NAME] -p [DATABASE PASSWORD] -H [DATABASE HOST] -u [DATABASE USER]`

## How to contribute

You don't have to know anything about programming or the likes to contribute to Konsent - developing the concept further is currently just as important. Concept development happens on [/f/Konsent](https://raddle.me/f/Konsent). Discussion happens both on GitHub and Raddle.

Contributing to the code-base is easy if you know Python and the basics of Git, and there's lots to be done. Simply install all the dependencies, as explained in the chapter above, grab your favorite code editor, take a look at the open issues and fire away. We're following the branching model explained [here](https://nvie.com/posts/a-successful-git-branching-model/) loosely. We're following the [PEP8](https://pep8.org/) style guide.

If you're planning to participate regularly and want to introduce yourself and get to know the others, you can do so on [our Raddle forum](https://raddle.me/f/Konsent).

You can ship your changes pretty much however you want, although a good old pull-request is preferred. Alternatively, contact [dellitsni](https://raddle.me/u/dellitsni) or one of the other developers on [raddle.me](https://raddle.me).
