from veikk.daemon.veikk_daemon import VeikkDaemon


def main(**kwargs):
    """
    Entry point if running as a console script
    """
    VeikkDaemon(**kwargs)
