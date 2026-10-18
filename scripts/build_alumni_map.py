"""Build the local Alumni Map from Natural Earth's public-domain country data."""
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path, help='Natural Earth Admin 0 countries GeoJSON')
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding='utf-8'))
    countries = {}
    paths = []
    for feature in source['features']:
        props = feature['properties']
        if props['ADMIN'] == 'Antarctica':
            continue
        code = props['ADM0_A3']
        countries[code] = {'name': props['ADMIN'], 'x': round((props['LABEL_X'] + 180) / 360 * 1000, 1),
                           'y': round((90 - props['LABEL_Y']) / 180 * 500, 1)}
        geometry = feature['geometry']
        polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        for polygon in polygons:
            d = 'M' + 'L'.join(f'{(lon + 180) / 360 * 1000:.1f},{(90 - lat) / 180 * 500:.1f}' for lon, lat in polygon[0]) + 'Z'
            paths.append(f'<path d="{d}"><title>{escape(props["ADMIN"])}</title></path>')
    data_path = ROOT / 'app/data/map_countries.json'
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(countries, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    image_path = ROOT / 'static/assets/img/maps/alumni-world.svg'
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500">'
                          '<title>World countries — Natural Earth public domain</title>'
                          '<rect width="1000" height="500" fill="#e8f0ee"/>'
                          '<g fill="#ceded3" stroke="#f7faf5" stroke-width=".6">' + ''.join(paths) + '</g></svg>', encoding='utf-8')
    print(f'Built local map and {len(countries)} country choices.')


if __name__ == '__main__':
    main()
