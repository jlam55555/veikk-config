from abc import ABCMeta
from typing import Dict

import yaml
from yaml import Dumper, Node, Loader

# turn off aliasing globally -- aliasing makes things harder to read and doesn't
# really have any performance difference; the only implication this has is that
# we can't "couple" different keycodes under the same command, which is fine
Dumper.ignore_aliases = lambda *args: True


class YamlRegisterable(type, metaclass=ABCMeta):
    """
    Metaclass that registers YAML representers and constructors for the type.
    This means that all classes must be defined (and imported) before attempting
    to load from YAML.
    """

    def __init__(cls, name, bases, clsdict):
        super(YamlRegisterable, cls).__init__(name, bases, clsdict)

        # type guards
        assert hasattr(cls, 'to_yaml')
        assert hasattr(cls, 'from_yaml')

        yaml.add_representer(cls, cls.to_yaml)
        yaml.add_constructor(f'!{cls.__name__}', cls.from_yaml,
                             Loader=yaml.SafeLoader)


class YamlSerializable(metaclass=YamlRegisterable):
    """
    A custom implementation of representers and constructors for YAML objects
    that is slightly different from the yaml.YamlObject class. In YamlObject,
    all of the object's keys are exposed, including internal/private ones.

    In this representation, the class can explicitly state which keys to
    serialize by implementing _to_yaml_dict(). Note that the output dict should
    be passable (as kwargs) to the class's constructor to fully reconstruct
    the object. to_yaml() and from_yaml() do not have to be reimplemented.
    """

    # def __init__(self, **kwargs):
    #     """
    #     Set up YAML representer and constructor for this class.
    #     """


    def _verify(self) -> None:
        """
        Performs (semantic) verification on an object after construction from
        YAML. (Object should already be structurally correct.)
        """
        raise NotImplementedError()

    def _to_yaml_dict(self) -> Dict:
        """
        Returns a dict representing the current object. Note that the keys
        of this dict should include the named parameters of the constructor
        :return:    dictionary representing the object
        """
        raise NotImplementedError()

    @classmethod
    def to_yaml(cls, dumper: Dumper, data: 'YamlSerializable') -> Node:
        """
        Implementation of representer for pyyaml. Represents the object as
        as dict defined by to_yaml_dict
        :param dumper:  YAML dumper
        :param data:    representable object
        :return:        YAML mapping representing object
        """
        return dumper.represent_mapping(f'!{cls.__name__}',
                                        data._to_yaml_dict())

    @classmethod
    def from_yaml(cls, loader: Loader, node: Node) -> 'YamlSerializable':
        """
        Implementation of constructor for pyyaml. Constructs the object by
        passing in the YAML representation (a YAML mapping) as kwargs to
        the constructor.
        :param loader:  YAML loader
        :param node:    YAML mapping representing object
        :return:        object from YAML
        """
        return cls(**loader.construct_mapping(node, deep=True))

    @classmethod
    def load_yaml(cls, obj_yaml: str) -> 'YamlSerializable':
        """
        Load from YAML using default loading properties and input validation.
        :param obj_yaml:    serialized object
        :return:            deserialized object
        """
        obj = yaml.safe_load(obj_yaml)

        # input validation
        assert isinstance(obj, cls)
        obj._verify()

        return obj

    def dump_yaml(self) -> str:
        """
        Dump object to YAML using default serialization properties.
        :return:        serialized object
        """
        return yaml.dump(self, Dumper=Dumper, default_flow_style=None)
