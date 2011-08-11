pyramid_errmail
===============

Overview
--------

A package which sends email when an exception occurs in your Pyramid
application.

.. warning:: This package currently will not work with any released Pyramid;
   it requires the Pyramid trunk (aka "1.2dev").

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_errmail

Setup
-----

Once ``pyramid_errmail`` is installed, you must use the ``config.include``
mechanism to include it into your Pyramid project's configuration.  In your
Pyramid project's ``__init__.py``:

.. code-block:: python
   :linenos:

   config = Configurator(.....)
   config.include('pyramid_errmail')

Alternately you can use the ``pyramid.includes`` configuration value in your
``.ini`` file:

.. code-block:: ini
   :linenos:

   [app:myapp]
   pyramid.includes = pyramid_errmail

Using
-----

When this utility is configured into a Pyramid application, whenever it
catches an exception, an email will be sent to one or more email addresses
with the traceback associated with that exception.

This package uses the :term:`pyramid_mailer` package to send mail.  It uses
the mailer settings from that package to determine the SMTP host and port,
and other mailout-related configuration.  See the documentation for that
package for detailed settings.  In general, however, you can usually get away
with only specifying ``mail.host`` and ``mail.port`` in your configuration:

.. code-block:: ini
   :linenos:

   [app:myapp]
   mail.host = 25
   mail.port = localhost

:mod:`pyramid_errmail`` has some of its own knobs, in the form of
configuration settings which are meant to be placed in the application
section of your Pyramid's ``.ini`` file.

``pyramid_errmail.catchall``

   If this value is ``true``, catch and report all errors, even those that
   might later be caught by a Pyramid exception view.  Otherwise, only
   exceptions that are not caught by a Pyramid exception view are emailed.

``pyramid_errmail.sender``

   The email address of the sender.  If this setting is not set, a default
   sender address will be used.

``pyramid_errmail.recipients``

    A carriage-return-separated list of recipients for the error emails.  If
    this setting is not set, no email will be sent.

``pyramid_errmail.subject``

    The subject line of each email.  If this setting is not set, the subject
    line will consist of the hostname, the exception title, and the date in
    the format ``${hostname}: ${exception} (${localtime})``.  You can use the
    following values the subject value: ``${localtime}``, ``${gmtime}``,
    ``${hostname}``, and ``${exception}``.  They will be replaced with the
    local time, the Zulu time, the system's hostname, and an exception
    representation respectively.

Explicit "Tween" Configuration
------------------------------

Note that the error mailer is implemented as a Pyramid :term:`tween`, and it
can be used in the explicit tween list if its implicit position in the tween
chain is incorrect (see the output of ``paster ptweens``)::

   [app:myapp]
   pyramid.tweens = someothertween
                    pyramid.tweens.excview_tween_factory
                    pyramid_errmail.errmail_tween_factory

It usually belongs directly above the "MAIN" entry in the ``paster ptweens``
output, and will attempt to sort there by default as the result of having
``include('pyramid_errmail')`` invoked.

More Information
----------------

.. toctree::
   :maxdepth: 1

   api.rst
   glossary.rst


Reporting Bugs / Development Versions
-------------------------------------

Visit http://github.com/Pylons/pyramid_errmail to download development or
tagged versions.

Visit http://github.com/Pylons/pyramid_errmail/issues to report bugs.

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
