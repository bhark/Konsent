# Konsent

## About

> It's about time that we rethink the way we make decisions collectively. Konsent is my suggestion for an alternative to moderation, an alternative to hierarchy and unequal freedom. Konsent is a platform designed to help groups make decisions without hierarchy and representatives, built on anarchist values.

The concept works roughly like this:

- All members of the community can post "issues". Simple posts with a title and a body, which point out something they would like to be solved. An example could be a proposal to ban a certain community member.

- When an issue is posted, it goes to phase one. There are three phases; when an issue has progressed through all three phases, it will have been solved, and the solution will have been either carried out or dismissed. Here's a short explanation of each phase:

- Phase 1: A filtering process. Every member of the community can vote directly for the issues they feel are relevant. Members cannot downvote issues. When half (adjust if needed) of the community-members have voted on an issue, it progresses to phase 2. This way, important issues are solved faster than lesser important issues.

- Phase 2: Time to solve the issue. Every member of the community can suggest solutions to the issue. Members can vote on the solution they like the most. After one day (again, adjust if needed), the solution with the most votes progresses to phase 3.

- Phase 3: Achieving concensus. The solution sits here without doing anything for one day (adjust if needed). If nothing happens during this resting period, the solution is carried through. During this period, every member of the community (perhaps only members with a certain reputation when it comes to online communities, to avoid trolls and griefers) can place a "veto", much like in ancient Greece. For physical communities, users can place as many vetoes as they want; for online communities, every user should probably have a fixed amount of vetoes (i think two or three per month would be a good fit). When a solution is vetoed, the vetoing community member will have to give an acceptable reason for the veto, and all other members of the community will be able to see the reason given and by who the solution was vetoed. It is of course required that members of the community adapt the mindset of concensus decision-making: cut some here, give some there. Can't always have it exactly your way if we are to respect the opinions of every member of the community.

- In the case of online communities, users could have the option to vote on banning another member from partaking in decision-making. This could be used to avoid trolls and such.

Konsent was originally designed for physical communities, such as a student council, and needs some work before it's ready for online communities, since online communities are typically very open to new members, and doesn't have the same integrity as a physical community.

## Installation

Konsent is written in Python, using Flask. Before you can run Konsent on your own machine, three things need to be configured:

- The MySQL database. Simply import the database schema from `konsent.sql` and change the database credentials on the first lines of `flask_app.py`. This can be done in PHPMyAdmin simply by clicking `import` and choosing `konsent.sql`, or using the MySQL command line: `mysql -u <username> -p konsent < konsent.sql`

- Install Python. Konsent is written in Python 2.7, which can be installed from [the official Python website](https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz).

- Install the required Python packages. The easiest way to install Python packages is with Pip, which comes with Python 2.7 by default. The packages required to run Konsent are: `flask, flask-mysqldb, wtforms, passlib, functools, datetime`. To install with pip: `pip install datetime flask flask-mysqldb wtforms passlib functools`. Some of these packages may already be installed, if so, just skip those.

When everything is ready to go, open up a command line (terminal, konsole, command prompt or something along those lines - depends on your OS), `git clone` this repository, `cd` to the repository and start `flask_app.py` using Python: `python flask_app.py`. If you want to adjust some settings (such as the resting time for a post in phase 2 and 3), you can do so on one of the first lines in `flask_app.py`.

## How to contribute

You don't have to know anything about programming or the likes to contribute to Konsent - developing the concept further is currently just as important. In the future, discussion and concept development will probably happen on the subraddle /f/konsent, on Raddle.me. Until then we can use GitHub's issues.

Contributing to the code-base is easy if you know Python and the basics of Git, and there's lots to be done. Simply install all the dependencies, as explained in the chapter above, grab your favorite code editor, take a look at the open issues and fire away. We're following the branching model explained [here](https://nvie.com/posts/a-successful-git-branching-model/) loosely.

You can ship your changes pretty much however you want, although a good old pull-request is preferred.
