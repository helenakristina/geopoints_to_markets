"""
Module to test dataframe input and output
Uses city longitude and latitude points and state geojson boundaries

# City data from https://simplemaps.com/data/us-cities
# State geojson from https://eric.clst.org/tech/usgeojson/

"""
import src.app as app

import geopandas
import pandas as pd
import pytest

columns = [
    "city",
    "city_ascii",
    "state_id_1",
    "state_name_1",
    "county_fips",
    "county_name",
    "county_fips_all",
    "county_name_all",
    "latitude",
    "longitude",
    "population",
    "density",
    "source",
    "military",
    "incorporated",
    "timezone",
    "ranking",
    "zips",
    "id",
]
city_filepath = "tests/data/uscities.csv"
market_filepath = "tests/data/gz_2010_us_040_00_500k.json"
separator = ","


def test_get_input_dataframe(snapshot):
    columns = [
        "city",
        "city_ascii",
        "state_id_1",
        "state_name_1",
        "county_fips",
        "county_name",
        "county_fips_all",
        "county_name_all",
        "latitude",
        "longitude",
        "population",
        "density",
        "source",
        "military",
        "incorporated",
        "timezone",
        "ranking",
        "zips",
        "id",
    ]
    city_filepath = "tests/data/uscities.csv"
    separator = ","
    df = app.get_input_dataframe(
        input_filepath=city_filepath, separator=separator, columns=columns
    )
    snapshot.assert_match(df.to_json(orient="records"))
    df.to_csv("tests/test_output/test_1.csv", index=False)


def test_throws_value_error():
    columns = [
        "city",
        "city_ascii",
        "state_id_1",
        "state_name_1",
        "county_fips",
        "county_name",
        "county_fips_all",
        "county_name_all",
        "lat",
        "long",
        "population",
        "density",
        "source",
        "military",
        "incorporated",
        "timezone",
        "ranking",
        "zips",
        "id",
    ]
    city_filepath = "tests/data/uscities.csv"
    separator = ","
    with pytest.raises(ValueError):
        app.get_input_dataframe(
            input_filepath=city_filepath, separator=separator, columns=columns
        )


def test_convert_to_geo_dataframe(snapshot):
    df = pd.read_csv("tests/test_output/test_1.csv")
    result = app.convert_to_geo_dataframe(df)
    snapshot.assert_match(result.to_json())
    result.to_csv("tests/test_output/test_2.csv", index=False)
    assert "geometry" in result.columns


def test_get_market_geo_dataframe(snapshot):
    market_filepath = "tests/data/gz_2010_us_040_00_500k.json"
    result = app.get_market_geo_dataframe(market_filepath=market_filepath)
    snapshot.assert_match(result.to_json())
    result.to_csv("tests/test_output/test_3.csv", index=False)


def test_merge_geopoint_with_markets(snapshot):
    # Have to use the other functions to get the geodataframes to merge
    df = pd.read_csv("tests/test_output/test_1.csv")
    geo_df = app.convert_to_geo_dataframe(df)
    market_filepath = "tests/data/gz_2010_us_040_00_500k.json"
    market_df = app.get_market_geo_dataframe(market_filepath=market_filepath)

    result = app.merge_geopoints_with_markets(geo_df=geo_df, market_df=market_df)
    result = pd.DataFrame(result)
    snapshot.assert_match(result.to_json(orient="records"))
    result.to_csv("tests/test_output/result.csv")
    assert result["state_name_1"].equals(result["NAME"])
