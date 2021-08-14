import os

from api.schema import ScreenResolution
from utils.functions import generate_k_dict

EMULATOR_SCREEN = ScreenResolution(width=1440.0, height=2392.0)
K_DICT = generate_k_dict(
    path=os.path.join(os.path.dirname(__file__), 'emulator_data.txt')
)
