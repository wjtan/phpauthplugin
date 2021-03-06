# -*- coding: utf-8 -*-

# Copyright (c) 2008 John Hampton <pacopablo@pacopablo.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Sponsored by Cobra <http://cobra-language.com>

from trac.core import Component, implements
from trac.db.api import DatabaseManager
from trac.config import Option
from acct_mgr.api import IPasswordStore

from phpbb.functions import phpbb_check_hash
import bcrypt
from time import time

class PhpBBAuthStore(Component):
    """ IPasswordStore implementation for authentication against PhpBB3 """

    implements(IPasswordStore)

    # This is here so that the account manager configuration page will pick 
    # it up.
    database = Option('account-manager', 'phpbb_database', None, 
                      'Database URI for the phpBB database to auth '
                      'against')

    table_prefix = Option('account-manager', 'phpbb_table_prefix', 'phpbb_',
                          'Prefix for phpBB table names.  This should be '
                          'everything before "user" including an underscore '
                          'if present.')

    def config_key(self):
        """ Deprecated """

    def get_users(self, populate_session=True):
        """ Pull list of current users from PhpBB3 """
        #cnx = PhpDatabaseManager(self.env).get_connection()
        #cur = cnx.cursor()
        #cur.execute('SELECT username, user_email, user_lastvisit'
        #            '  FROM %susers '
        #            ' WHERE user_type <> 2' % self.table_prefix)
        #userinfo = [u for u in cur]
        #cnx.close()
        #if populate_session:
        #    self._populate_user_session(userinfo)
        #return [u[0] for u in userinfo]
        # Too many users, do not bother to load them
        return []

    def has_user(self, user):
        """ Check for a user in PhpBB3 """
        cnx = PhpDatabaseManager(self.env).get_connection()
        cur = cnx.cursor()
        cur.execute('SELECT username FROM %susers WHERE user_type <> 2'
                    ' AND username = %%s' % self.table_prefix, (user,))
        result = [u for u in cur]
        cnx.close()
        return result and True or False

#    def set_password(self, user, password):
#        """ Set the password for the selected user. """
#        # Implement later

    def check_password(self, user, password):
        """ Checks the password for the user against PhpBB3"""
        hashed = self._get_pwhash(user)
        if not hashed:
            return False
        self._populate_user_session(self._get_userinfo(user))
        
        if hashed.startswith('$2a$') or hashed.startswith('$2y$'):
                hashed = hashed.encode('utf-8')
                return bcrypt.hashpw(password.encode('utf-8'), hashed) == hashed
        else:
	        return phpbb_check_hash(password, hashed)
        
        return check

    def delete_user(self, user):
        """ Delete the user """
        # Imlement later
        return False

    def _get_pwhash(self, user):
        """ Return the password hash from the database """
        cnx = PhpDatabaseManager(self.env).get_connection()
        cur = cnx.cursor()
        cur.execute('SELECT user_password'
                    '  FROM %susers'
                    ' WHERE user_type <> 2'
                    '   AND username = %%s' % self.table_prefix, (user,))
        result = cur.fetchone()
        pwhash = result and result[0] or None
        cnx.close()
        return pwhash

    def _get_userinfo(self, user):
        """ Pull user info from TG """
        cnx = PhpDatabaseManager(self.env).get_connection()
        cur = cnx.cursor()
        cur.execute('SELECT username, user_email, user_lastvisit'
                    '  FROM %susers '
                    ' WHERE username = %%s' % self.table_prefix, (user,))
        userinfo = [u for u in cur]
        cnx.close()
        return userinfo

    def _populate_user_session(self, userinfo):
        """ Create user session entries and populate email and last visit """

        # Kind of ugly.  First try to insert a new session record.  If it
        # fails, don't worry, means it's already there.  Second, insert the
        # email address session attribute.  If it fails, don't worry, it's
        # already there.
        cnx = self.env.get_db_cnx()
        for uname, email, lastvisit in userinfo:
            try:
                cur = cnx.cursor()
                cur.execute('INSERT INTO session (sid, authenticated, '
                            'last_visit) VALUES (%s, 1, %d)',
                            (uname, int(time())))
                cnx.commit()
            except:
                cnx.rollback()
            try:
                cur = cnx.cursor()
                cur.execute("INSERT INTO session_attribute"
                            "    (sid, authenticated, name, value)"
                            " VALUES (%s, 1, 'email', %s)",
                            (uname, email))
                cnx.commit()
            except:
                cnx.rollback()
            continue
        cnx.close()
         


class PhpDatabaseManager(DatabaseManager):
    """ Class providing access to the PHP databse """

    connection_uri = Option('account-manager', 'phpbb_database', None, 
                            'Database URI for the phpBB database to auth ' \
                            'against')

    
