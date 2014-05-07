# -*- coding: utf-8 -*-
"""
saplugin is a CherryPy plugin for SQLAlchemy.  See the
documentation in pycrust.satool for instructions.

"""
#
# This file is based on Sylvain Hellegouarch's post:
# http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html
#
# All credit goes to Sylvain for this.
#
import cherrypy, logging
from cherrypy.process import plugins
from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import scoped_session, sessionmaker
from pycrust.saquery import AugmentedQuery

__all__ = ['SAEnginePlugin']

class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus, connection_string=None):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.

        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.connection_string = connection_string
        self.session = scoped_session(sessionmaker(autoflush=True,
                                                   autocommit=False,
                                                   query_cls=AugmentedQuery))

    def start(self):
        self.bus.log('Starting up DB access')
        self.sa_engine = create_engine(self.connection_string, echo=False)
        self.bus.subscribe("bind-session", self.bind)
        self.bus.subscribe("commit-session", self.commit)

    def stop(self):
        self.bus.log('Stopping down DB access')
        self.bus.unsubscribe("bind-session", self.bind)
        self.bus.unsubscribe("commit-session", self.commit)
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self):
        """
        Whenever this plugin receives the 'bind-session' command, it applies
        this method and to bind the current session to the engine.

        It then returns the session to the caller.
        """
        self.session.configure(bind=self.sa_engine)
        return self.session

    def commit(self):
        """
        Commits the current transaction or rollbacks if an error occurs.

        In all cases, the current session is unbound and therefore
        not usable any longer.
        """

        try:
            self.session.commit()
        # an attempt was made to commit with nothing to commit
        except InvalidRequestError as e:
            self.bus.log("Attempt to commit with nothing to commit!  Message: {}".format(e),
                         level=logging.INFO)
            self.session.rollback()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.remove()

