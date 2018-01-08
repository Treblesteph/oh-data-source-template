# Open Humans Data Source template and working demo

> Work through this guide to add a data source to Open Humans

## Table of Contents

- [About this repo](#about-this-repo)
  - [Introduction](#introduction)
  - [Workflow overview](#workflow-overview)
  - [How does an Open Humans data source work?](#how-does-an-open-humans-data-source-work)
- [Setting up local environment](#setting-up-local-environment)
  - [Installing Foreman](#installing-foreman)
  - [Installing RabbitMQ](#installing-rabbitmq)
  - [Python](#Python)
  - [pip](#pip)
  - [Virtual environments](#virtual-environments)


## About this repo

### Introduction

This repository is a template for, and working example of an Open Humans data source. If you want to add a data source to Open Humans, we strongly recommend following the steps in this document to work from this template repo.

### Workflow overview

- First get this demo project working. Detailed instructions can be found below, but this involves the following steps:
  - set up local environment
  - clone this template repo to your own machine
  - create a project on OH
  - try out adding dummy data as a user
- When you have successfully created an Open Humans project and added dummy data using this template, you can start to edit the code to to add your desired data source
  - the template text in `index.html` can be edited for your specific project, but mostly this file can remain as it is, to enable user authentication
  - data should be added after user is directed back from Open Humans to `complete.html`
  - we recommend starting by looking at the function `add_data_to_open_humans` in the `tasks.py` file

Maybe note here about future updates to versions??

### How does an Open Humans data source work?

This template is a [Django](https://www.djangoproject.com/)/[Celery](http://www.celeryproject.org/) app that enables an Open Humans member to add dummy data to an Open Humans project. The user arrives on the landing page (`index.html`), and clicks a button which takes them to Open Humans where they can log in (and create an account if necessary). Once logged in to the Open Humans site, the user clicks another button to authorize this app to add data to their Open Humans account, then they return to this app (to `complete.html`) which notifies them that their data has been added and provides a link to the project summary page in Open Humans.

*** screenshots of steps

*** detail here about how all this works (eg. code workflow?) or actually better after setting up?

## Setting up local environment

### Installing foreman

[Foreman](https://ddollar.github.io/foreman/) is a manager for running [procfile-based applications](https://devcenter.heroku.com/articles/procfile). It will no longer be required in future versions of this code since latest versions of Heroku now have a built-in manager.

To install Foreman, you can use `gem install foreman`. If you have trouble with this or do not have a Ruby gem installer, you can follow the Foreman installation instructions [here](https://theforeman.org/manuals/1.16/index.html#3.InstallingForeman).

### Installing RabbitMQ

[RabbitMQ](http://www.rabbitmq.com) is an open source [message broker](https://en.wikipedia.org/wiki/Message_broker) used by this application.

To install RabbitMQ you can follow [https://www.rabbitmq.com/download.html](these instructions), or if you are using a Mac and have Homebrew installed, you can simply type `brew install rabbitmq`.

### Python

For the current version of this template, you will need [Python 2](https://www.python.org/downloads/). We are working on an updated version to run on Python 3.

You will need to ensure that the `python` alias points to Python 2 and not Python 3. You can do this by adding this line `alias python=python3` to your `.bashrc` file.

### pip

[pip](https://pypi.python.org/pypi/pip) is a package management system used to install and manage software packages written in Python. It is available [here](https://pip.pypa.io/en/stable/installing/).

### Virtual environments







### Open Humans authorization

The `complete` function view in `oh_data_source.views` handles receiving
a code from Open Humans, exchanging it for a token, using the token to
retrieve project member ID, and stores this in the `OpenHumansMember` model.

### Asynchronous tasks

The `oh_data_source.celery` sets up asynchronous tasks for the app. This is
used to asynchronously run `xfer_to_open_humans` in `oh_data_source.tasks`.

#### Why asynchonous?

Sometimes it takes a long time. This is bad, the web app will not process
other requests.

### Upload to Open Humans

Template code for uploading an example file to a member account, as well as
demo code for file deletion.

## Local development instructions

Django, and thus this project are built on top of `python2.7`, if you are using `python3` as your default system, you will most definitely need a `virtualenv` to work with this code.

### Local requirements.

1. Foreman https://github.com/ddollar/foreman (This package may be installed with a simple `gem install foreman`)
2. RabbitMQ https://www.rabbitmq.com/download.html
3. pip https://pip.pypa.io/en/stable/installing/

### Install Python 2.7 requirements.

**It is Strongly recommend you use [virtualenv](https://virtualenv.pypa.io/en/stable/).**
**Be advised you need to use a name other than the default `.env` for the python environment; we suggest `.env_$YOURPROJECT`**

To create your 'virtualenv' run:

  `virtualenv -v --python=python2.7 .env_$YOURPROJECT`

  The two flags we are using `-v` makes the setup verbose, allowing easier debugging.

  The second flag `--python=python2.7` guarantees that no matter how many versions of python you have on your system the 'virtualenv' will be built with the 'Django' standard `python2.7`.

To activate your 'virtualenv' you need to run:

  `source .env_$YOURPROJECT/bin/activate`

Next install all of the required python dependancies with:

  `pip install -r requirements.txt`

---

### Set up `.env` for `foreman`

Copy `env.example` to `.env`.

This file contains secrets and other configurations for running the app.
When you use foreman to run this app, it will load `.env` to be environment
variables.
**Keep your version SECRET! Never commit it to git.**

### Install `RabbitMQ` for your system

Documentation for supported systems includes [Linux (apt&rpm), OS X/macOS, and Other Unixes (including BSDs), as well as Windows](https://www.rabbitmq.com/platforms.html)

### Make sure that `RabbitMQ` is started

This is distribution dependent, both in syntax and name.
- With the very popular Ubuntu and other Debian based systems, it will likely be started for you after you install the package, but can also start it manually with: `sudo rabbitmq-server start`
- With Homebrew on OS X/macOS run `brew services rabbitmq start`
- [RabbitMQ](https://www.rabbitmq.com/) has it's control system similar to `apachectl`, The documentation is online if you would like to learn more about [rabbitmqctl](https://www.rabbitmq.com/man/rabbitmqctl.1.man.html)
If you have other questions please refer to your [distribution reference page at `RabbitMQ`](https://www.rabbitmq.com/platforms.html)

### Create Open Humans project

You need to create an OAuth2 project in Open Humans. Start here:
https://www.openhumans.org/direct-sharing/projects/manage/

This is what members join and authorize. Some recommended settings:
1. **Fill out the "Description of data you plan to upload".** This identifies
  your project as a data source. If it's left blank, Open Humans assumes
  your project doesn't plan to add data.
2. **Set the enrollment URL to http://127.0.0.1:5000**
  **The default development setup automatically sets the Redirect URL to http://127.0.0.1:5000/complete**

---

Once the project is created, click on the project's name in your [project
management page](https://www.openhumans.org/direct-sharing/projects/manage/).
This will show the project's information.

Get the `Activity page`, `Client ID` and `Client secret` and set these in
your `.env`. The ID and secret identify and authorizes your app. You'll use
these to get user authorization and manage user data.

**Keep your Client secret private.** Secret data should not be committed to a
repository. In Heroku, this data is set as environment variables. Locally,
you can use a custom `.env`.

### Initialize the database and static assets.

Note: Django will use SQLite3 for local development unless you set
`DATABASE_URL` in your `.env`.

In the project directory, run the `migrate` command with foreman:
`foreman run python manage.py migrate`

In the project directory, run the `collectstatic` command with foreman:
`foreman run python manage.py collectstatic`
**You will receive a warning message similar to:**
```
You have requested to collect static files at the destination
location as specified in your settings:

    development:~/your_project/staticfiles

This will overwrite existing files!
Are you sure you want to do this?
```

This is normal! You **WILL** want to overwrite the files, theres is likely no folder even created yet, so nothing stored there currently in any case.

---

### Run.

You can now start `foreman` in the foreground with: `foreman start`
   Note you will receive the warning: `warnings.warn('Using settings.DEBUG leads to a memory leak, never '`. This is normal, and sadly part of the debugging process of Django.

If you're curious as to the root cause of this [StackOverflow has a full writeup](http://stackoverflow.com/questions/4806314/disable-django-debugging-for-celery)

Now point your browser to (http://127.0.0.1:5000/) you should be greated with a fairly generic openhumans page, with some of your `project` information that you added in the `foreman` .env file.

---

## Heroku deployment notes

Heroku has a lot of features and documentation. The notes below can
help you get started &ndash; you should feel free to explore more!

### Prerequisites and local requirements

1. Create a Heroku account
2. Install the Heroku Commant Line Interface (formally "Heroku Toolbelt"):
https://devcenter.heroku.com/articles/heroku-cli

### Log in and create your app

It's common for the app to have the same name as the project slug. The name
matters if you plan to use Heroku's default domain, which is free (e.g. `https://your-app-name.herokuapp.com`).

1. `heroku login`
2. `heroku apps:create your-app-name`

### Configure and add add-ons

Find your app in the Heroku Dashboard:  https://dashboard.heroku.com/apps

Go to **"Resources tab"** and add:
1. **CloudAMQP** (Little Lemur: Free)
2. **Heroku Postgres** (Hobby Dev: Free)

Go to **"Settings tab"** and add environment variables (as with `.env`):
1. **OH_CLIENT_ID**
2. **OH_CLIENT_SECRET**
3. **OH_ACTIVITY_PAGE**
4. **APP_BASE_URL** (e.g. `https://your-app-name.herokuapp.com` &ndash; no trailing dash!)
5. **SECRET_KEY**
7. **DEBUG** = true when needed

### Push your code.

Run this to initialize and update your code in Heroku:
`git push heroku master`

### Watch logs.

`heroku logs -t`
