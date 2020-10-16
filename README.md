# parser-csv-geometry

Parses string like 'POINT (10.2 5.1)' or 'POLYGON ((10.2 5.1, 11.5 2.5, 5.6 8.5)) from exported csv in *shapely.geometry* instances.

### Usage

```python
x = "POINT (10.2 5.1)"
print(type(x))

>>> <class 'str'>

y = parser_type(x)
print(type(y))

>>> <class 'shapely.geometry.point.Point'>
```

### Requirements

It requires *Shapely==1.7.0*.
