#!/usr/bin/python3


class BadAPMode(Exception):
  """
  Used a bad DHCP range
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class BadKeyValuePair(Exception):
  """
  Bad config option. This runs when the key and/or value is wrong
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class BadInterface(Exception):
  """
  Bad interface option. This interface doesn't exist or is invalid
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class KeyReuse(Exception):
  """
  Tried to Redeclare a key and value pair
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class MalformedDHCP(Exception):
  """
  Used a bad DHCP range
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class IncorrectArguments(Exception):
  """
  Bad number of arguments used
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)
