from veikk.common.command.command import CommandMap


class ConfigIO:
    """
    Functions to serialize and deserialize the VEIKK configuration (which
    comprises a set of command mappings) to a YAML configuration file.
    
    By default, the configuration is read from /usr/local/etc/veikkd.yaml,
    but this can be changed using the -f option with the edit and apply
    subcommands.

    TODO: still have to figure out how to store the pen mappings
    TODO: how to handle inconsistent state/bad YAML format?
    """

    @staticmethod
    def write_config(filename: str, config: CommandMap) -> None:
        """
        Write a config to a file.
        :param filename:    filename of config file to write to
        :param config:      the configuration to write
        """
        with open(filename, 'w+') as out_file:
            # write a little header
            out_file.write('Configuration for the VEIKK mapping tool (veikkd)\n'
                           'https://github.com/jlam55555/veikk-config\n\n')

    @staticmethod
    def read_config(filename: str) -> CommandMap:
        """
        Read a config from a file.
        :param filename:    filename of config file to read from
        :return:            the read and parsed configuration
        """
        pass
