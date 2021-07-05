from pathlib import Path
from typing import Dict

import yaml


class VeikkModel:
    """
    VeikkModel holds information about a Veikk device.
    """

    def __init__(self,
                 name: str,
                 model_id: int = None,
                 x_max: int = None,
                 y_max: int = None):
        self.name = name
        self.model_id = model_id
        self.x_max = x_max
        self.y_max = y_max

    @staticmethod
    def get_models_data() -> Dict[str, 'VeikkModel']:
        """
        Loads all VEIKK models into a dict from ./veikk_models.yaml.
        :return: dict of all VEIKK models
        """
        with open(Path(__file__).parent / 'veikk_models.yaml') as fd:
            models_yaml = fd.read()
        models_data = yaml.safe_load(models_yaml)
        return {kwargs['name']: VeikkModel(**kwargs) for kwargs in models_data}
