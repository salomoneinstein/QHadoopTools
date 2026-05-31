import json


class GeoJSONService:

    def fix(self, input_file, output_file=None):
        
        if output_file is None:
            output_file = input_file

        # Read input
        try:
            with open(input_file, "r", encoding="utf-8") as f:

                try:
                    #intentar JSON normal
                    data = json.load(f)

                except json.JSONDecodeError:
                    #fallback: JSON Lines (Hive)
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


        # Convert / Fix
        geojson = self._convert(data)


        # Basic validation
        if not isinstance(geojson, dict):
            raise ValueError("Invalid GeoJSON structure")

        valid_types = {
            "FeatureCollection",
            "Feature",
            "GeometryCollection",
            "Point",
            "MultiPoint",
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon"
        }

        geo_type = geojson.get("type")
        if geo_type not in valid_types:
            raise ValueError("Invalid GeoJSON type")

        # Validación adicional para FeatureCollection
        if geo_type == "FeatureCollection":
            if "features" not in geojson:
                raise ValueError("FeatureCollection missing 'features'")

            if not isinstance(geojson["features"], list):
                raise ValueError("'features' must be a list")


        # Write output
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)

        except OSError as e:
            raise RuntimeError(f"Error writing output file: {e}")

 
    # Internal conversion logic
    def _convert(self, data):

        features = []

        #recorrer lista de registros
        for item in data:

            if "attributes" not in item or "geometry" not in item:
                continue

            props = item["attributes"]

            geom = item["geometry"]

            #convertir rings → coordinates
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

        return {
            "type": "FeatureCollection",
            "features": features
        }