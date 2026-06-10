import json

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GeoJSONService:

    def fix(self, input_file, output_file=None, progress_callback=None):

        if output_file is None:
            output_file = input_file

        try:
            with open(input_file, "r", encoding="utf-8") as f:

                try:
                    data = json.load(f)

                except json.JSONDecodeError:
                    f.seek(0)
                    data = []

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        data.append(json.loads(line))

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        except OSError as e:
            raise RuntimeError(f"Error reading input file: {e}")

        geojson = self._convert(data, progress_callback)

        if not isinstance(geojson, dict):
            raise ValueError("Invalid GeoJSON structure")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)

        except OSError as e:
            raise RuntimeError(f"Error writing output file: {e}")
            

    def _convert(self, data, progress_callback=None):

        features = []

        for item in data:

            if "attributes" not in item or "geometry" not in item:
                continue

            props = item["attributes"]
            geom = item["geometry"]
            coords = geom.get("rings")

            feature = {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coords
                }
            }

            features.append(feature)

        if progress_callback:
            progress_callback(100)

        return {
            "type": "FeatureCollection",
            "features": features
        }