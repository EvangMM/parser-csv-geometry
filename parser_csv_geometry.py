import re
from typing import List, Tuple, TypeVar, Union

from shapely.geometry import (LineString, Point, Polygon,
                              MultiPoint, MultiLineString, MultiPolygon,
                              GeometryCollection)

SimpleGeometry = TypeVar("SimpleGeometry",
                         LineString, Point, Polygon)
MultiGeometry = TypeVar("MultiGeometry",
                        MultiPoint, MultiLineString, MultiPolygon)

RGX_COLL = r"(?P<collection>GEOMETRYCOLLECTION\s\()(?P<parsable>(.+))(\))"
RGX_FNC = r"((?P<multi>MULTI)?(?P<geom>POINT|LINESTRING|POLYGON)\s?(?P<coords>\({1,3}[^()]*\){1,3}))"


def parse_collection(string: str) -> Tuple[str, bool]:
    """Verify if string is a collection
        and return parsable string."""

    collection = False
    match = re.match(RGX_COLL, string)
    if match:
        string = match.group("parsable")
        collection = True
    return string, collection


def parse_fnc(string: str) -> Tuple[str,
                                    SimpleGeometry,
                                    Union[None, MultiGeometry]]:
    """Return a coords string, a geometry type
    and eventually a multigeometry type."""

    match = re.match(RGX_FNC, string)
    if match:
        multi = match.group("multi")
        geom = match.group("geom")
        coords = match.group("coords")
        if geom == "POINT":
            fnc = Point
            mfnc = MultiPoint if multi else None
        elif geom == "LINESTRING":
            fnc = LineString
            mfnc = MultiLineString if multi else None
        elif geom == "POLYGON":
            fnc = Polygon
            mfnc = MultiPolygon if multi else None
        else:
            raise Exception("No valid object")
        return coords, fnc, mfnc
    else:
        raise Exception("No match in parse_func")


def fnc_rebuild(string: str, fnc: SimpleGeometry,
                mfnc: Union[None, MultiGeometry]) -> Union[SimpleGeometry,
                                                           MultiGeometry]:
    """Return a (multi)geometry object"""

    if mfnc:
        substring = string.split("), (")
        return mfnc([fnc(parse_coords(sub)) for sub in substring])
    else:
        return fnc(parse_coords(string))


def parse_coords(string: str) -> Union[List[float],
                                       List[List[float]]]:
    "Return a list of coordinates."

    # Strip string part:
    # e.g. "(43.21 18.23, 43.21 18.23)" -> "43.21,18.23,,43.21 18.23"
    new_string = re.sub(r"(\(|\))", "", string).replace(" ", ",")

    # Break the long string
    # for lines and polygons
    # "43.21,18.23,,43.22,18.29,," -> ["43.21,18.23","43.22,18.29"]
    # for points
    # "43.21,18.23" -> ["43.21,18.23"]
    list_string_coords = new_string.split(",,")

    # break the string coord in point string:
    # ["43.21,18.23"] -> ["43.21","18.23"]
    string_coords = [str_coord.split(",") for str_coord in list_string_coords]

    # convert string in float: ["43.21","18.23"] -> [43.21,18.23]
    if len(string_coords) > 1:
        return [list(map(float, point)) for point in string_coords]
    else:
        return list(map(float, string_coords[0]))


def parse_geometry(string: str) -> Union[GeometryCollection,
                                         SimpleGeometry,
                                         MultiGeometry]:
    """Return a geometry object parsed from a string."""
    string, collection = parse_collection(string)
    if collection:
        # return a tuple
        occurrences = re.findall(RGX_FNC, string)
        # first element in tuple
        list_geometries = list(map(lambda x: x[0], occurrences))
        coll = [fnc_rebuild(*parse_fnc(geom)) for geom in list_geometries]
        return GeometryCollection(coll)
    else:
        return fnc_rebuild(*parse_fnc(string))
