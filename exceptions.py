#!/usr/bin/python3


class BadKeyValuePair(Exception):
  """
  Bad config exception. This runs when the key and/or value is wrong
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)


class KeyReuse(Exception):
  """
  Tried to Redeclare a key and value pair
  """
  def __init__(self, error_args):
    Exception.__init__(self, error_args)
