from typing import Dict

import yaml
from yaml import Dumper, Node, Loader

# turn off aliasing globally -- this makes things harder to read and doesn't
# really have any performance difference; the only implication this has is that
# we can't "couple" different keycodes under the same command, which is fine
Dumper.ignore_aliases = lambda *args: True


class YamlSerializable:
    """
    A custom implementation of representers and constructors for YAML objects
    that is slightly different from the yaml.YamlObject class. In YamlObject,
    all of the object's keys are exposed, including internal/private ones.

    In this representation, the class can explicitly state which keys to
    serialize by implementing to_yaml_dict(). Note that the output dict should
    be passable (as kwargs) to the class's constructor to fully reconstruct
    the object.

    In other words, instead of automatically exposing all of the member
    variables, we only expose the constructor parameters necessary to
    reconstruct the object.
    """

    def __init__(self, **kwargs):
        """
        Set up YAML representer and constructor for this class.
        """
        yaml.add_representer(self.__class__, self._yaml_representer)
        yaml.add_constructor(f'!{self.__class__.__name__}',
                             self._yaml_constructor)

    def _to_yaml_dict(self) -> Dict:
        """
        Returns a dict representing the current object. Note that the keys
        of this dict should include the named parameters of the constructor
        :return:    dictionary representing the object
        """
        ...

    def _yaml_representer(self,
                          dumper: Dumper,
                          data: 'YamlSerializable') -> Node:
        """
        Implementation of representer for pyyaml. Represents the object as
        as dict defined by to_yaml_dict
        :param dumper:  YAML dumper
        :param data:    representable object
        :return:        YAML mapping representing object
        """
        return dumper.represent_mapping(f'!{self.__class__.__name__}',
                                        data._to_yaml_dict())

    def _yaml_constructor(self,
                          loader: Loader,
                          node: Node) -> 'YamlSerializable':
        """
        Implementation of constructor for pyyaml. Constructs the object by
        passing in the YAML representation (a YAML mapping) as kwargs to
        the constructor.
        :param loader:  YAML loader
        :param node:    YAML mapping representing object
        :return:        object from YAML
        """
        return self.__class__(**loader.construct_mapping(node, deep=True))
