from veikk.daemon.daemon import Daemon


def main(**kwargs):
    """
    Entry point if running as a console script
    """
    Daemon(**kwargs)
