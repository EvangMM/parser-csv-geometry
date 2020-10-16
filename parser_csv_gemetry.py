import re

from shapely.geometry import (
            LineString, Point, Polygon, 
            MultiPoint, MultiLineString, MultiPolygon)


def parser_type(string):
    """
    Function that find out the geometry type
    of the input string
    
    Args:
        string : str, a string like 'POINT (10.2 5.1)'
            or 'POLYGON ((10.2 5.1, 11.5 2.5, 5.6 8.5))'
    Return
        shapely.geometry object, a transformed list of coordinates
    """   
    
    match = re.match(r"(\w*)(\s)", string)
    name = match.group(1)
    
    if name == "POINT":
        func = Point
        mfunc = None
        multi = False
    elif name == "LINESTRING":
        func = LineString
        mfunc = None
        multi = False
    elif name == "POLYGON":
        func = Polygon
        mfunc = None
        multi = False
    elif name == "MULTIPOINT":
        func = Point
        mfunc = MultiPoint
        multi = True
    elif name == "MULTILINESTRING":
        func = LineString
        mfunc = MultiLineString
        multi = True
    elif name == "MULTIPOLYGON":
        func = Polygon
        mfunc = MultiPolygon
        multi = True
    
    new_string = string.replace(match.group(0),"")
    
    if multi:
        substring = new_string.split("), (")
        return mfunc([func(parser_geometry(sub)) for sub in substring])
    else:
        return func(parser_geometry(new_string))


def parser_geometry(string):
    """
    Function that parse the geometry string and return a list
    
    Args:
        string : str, a geometry string
    Return:
        list, a list of float coordinates
    """

    #Strip string part: e.g. "(43.21 18.23, 43.21 18.23)" -> "43.21,18.23,,43.21 18.23"
    new_string = re.sub(r"(\(|\))","",string).replace(" ",",")
    
    #Break the long string 
    #   for lines and polygons "43.21,18.23,,43.22,18.29,," -> ["43.21,18.23","43.22,18.29"]
    #   for points "43.21,18.23" -> ["43.21,18.23"] 
    list_string_coords = new_string.split(",,")

    #break the string coord in point string: ["43.21,18.23"] -> ["43.21","18.23"]
    string_coords = [str_coord.split(",") for str_coord in list_string_coords]
    
    #convert string in float: ["43.21","18.23"] -> [43.21,18.23]
    if len(string_coords)>1:
        return [list(map(float,point)) for point in string_coords]
    else:
        return list(map(float,string_coords[0]))