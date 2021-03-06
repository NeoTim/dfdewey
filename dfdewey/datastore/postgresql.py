# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""PostgreSQL datastore."""

import logging

import psycopg2
from psycopg2 import extras

# Setup logging
postgresql_logger = logging.getLogger('postgresql')
postgresql_logger.addHandler(logging.NullHandler())
postgresql_logger.setLevel(logging.WARNING)


class PostgresqlDataStore(object):
  """Implements the datastore."""

  def __init__(
      self,
      host='127.0.0.1',
      port=5432,
      db_name='dfdewey',
      autocommit=False):
    """Create a PostgreSQL client."""
    super(PostgresqlDataStore, self).__init__()
    self.db = psycopg2.connect(
        database=db_name,
        user='dfdewey',
        password='password',
        host=host,
        port=port)
    if autocommit:
      self.db.set_isolation_level(
          psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    self.cursor = self.db.cursor()

  def switch_database(
      self, host='127.0.0.1', port=5432, db_name='dfdewey', autocommit=False):
    """Connects to a different database.

    Args:
      host: Hostname or IP address of the PostgreSQL server
      port: Port of the PostgreSQL server
      db_name: Name of the database to connect to
      autocommit: Flag to set up the database connection as autocommit
    """
    self.db.commit()
    self.db.close()
    self.db = psycopg2.connect(
        database=db_name,
        user='dfdewey',
        password='password',
        host=host,
        port=port)
    if autocommit:
      self.db.set_isolation_level(
          psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    self.cursor = self.db.cursor()

  def table_exists(self, table_name, table_schema='public'):
    """Check if a table exists in the database.

    Args:
      table_name: Name of the table
      table_schema: Table schema if different from 'public'

    Returns:
      True if the table already exists, otherwise False
    """
    self.cursor.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = '{0:s}' AND table_name = '{1:s}'""".format(
            table_schema, table_name))

    return self.cursor.fetchone()

  def value_exists(self, table_name, column_name, value):
    """Check if a value exists in a table.

    Args:
      table_name: Name of the table
      column_name: Name of the column
      value: Value to query for

    Returns:
      True if the value exists, otherwise False
    """
    self.cursor.execute("""
        SELECT 1 from {0:s}
        WHERE {1:s} = '{2:s}'""".format(
            table_name, column_name, value))

    return self.cursor.fetchone()

  def execute(self, command):
    """Execute a command in the PostgreSQL database.

    Args:
      command: The SQL command to be executed
    """
    self.cursor.execute(command)

  def bulk_insert(self, table_spec, rows):
    """Execute a bulk insert into a table.

    Args:
      table_spec: String in the form 'table_name (col1, col2, ..., coln)'
      rows: Array of value tuples to be inserted
    """
    extras.execute_values(
        self.cursor,
        'INSERT INTO {0:s} VALUES %s'.format(table_spec),
        rows)

  def query(self, query):
    """Query the database.

    Args:
      query: SQL query to execute

    Returns:
      Rows returned by the query
    """
    self.cursor.execute(query)

    return self.cursor.fetchall()

  def query_single_row(self, query):
    """Query the database for a single row.

    Args:
      query: SQL query to execute

    Returns:
      Single row returned by the query
    """
    self.cursor.execute(query)

    return self.cursor.fetchone()

  def __del__(self):
    """Finalise a PostgreSQL client."""
    if self.db:
      self.db.commit()
      self.db.close()
