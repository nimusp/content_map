import re
import os
import sys


def generate_k_dict(path: str) -> dict:
    """
    Генерация коэффициентов для
    широты и долготы при
    целочисленном значении zoom
    на основе данных, сгенерированных
    android-разработчиками

    *Используется для определения
    граничных координат viewport'а

    :param path:
        Путь до файла

    """

    if not (os.path.exists(path) and os.path.isfile(path)):
        sys.exit(f'Не найден файл данных эмулятора {path} ¯\\_(ツ)_/¯')

    float_pattern = r'-?\d+\.?\d+'
    k_dict_ = {}

    with open(path, mode='r') as f:
        try:
            while True:
                _ = next(f)  # center-center point
                zoom = float(re.search(float_pattern, next(f)).group(0))
                tl_lat, tl_lon = map(float, re.findall(float_pattern, next(f)))
                _ = next(f)  # top-right point
                br_lat, br_lon = map(float, re.findall(float_pattern, next(f)))
                _ = next(f)  # bottom-left point
                _ = next(f)  # separator in file

                lat_delta = abs(tl_lat - br_lat)
                lon_delta = abs(tl_lon - br_lon)

                k_dict_[zoom] = {
                    "lat_delta": lat_delta,
                    "lon_delta": lon_delta
                }
        except StopIteration:
            pass
        return k_dict_
