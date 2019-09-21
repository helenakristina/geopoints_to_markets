import geopandas
import pandas as pd
from shapely.geometry import Point
import yaml

import argparse
from collections import ChainMap
import logging
import os


log = logging.getLogger(__name__)


def get_input_dataframe(
    input_filepath: str, separator: str, columns: list
) -> pd.DataFrame:
    """
    Method for creating dataframe from csv without headers

    Parameters:
    input_filepath (string): The relative filepath of input csv file
    separator (string): separator of csv file (default is tab-separated)
    columns (list): list of headers for building dataframe

    Returns:
    Pandas dataframe of values from the input csv file
    """

    df = pd.read_csv(input_filepath, sep=separator, names=columns)
    df.rename({column: column.lower() for column in df.columns})
    if "longitude" not in df.columns or "longitude" not in df.columns:
        raise ValueError("Headers must contain latitude and longitude")
    log.info(f"Successfully created dataframe of shape {df.shape}")
    log.info(df.head())
    return df


def convert_to_geo_dataframe(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """
    Method for creating geodataframe from dataframe with longitude and latitude

    Parameters:
    input_filepath (string): The relative filepath of input csv file
    separator (string): separator of csv file (default is tab-separated)
    columns (list): list of headers for building dataframe

    Returns:
    Pandas dataframe of values from the input csv file

    """
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    crs = {"init": "epsg:4326"}
    geo_df = geopandas.GeoDataFrame(df, crs=crs, geometry=geometry)
    log.info(
        f"Successfully converted dataframe to geodataframe of shape {geo_df.shape}"
    )
    log.info(geo_df.head())
    return geo_df


def get_market_geo_dataframe(market_filepath: str) -> geopandas.GeoDataFrame:
    """
    Method for converting market geojson file into Geopandas GeoDataFrame

    Parameters:
    market_filepath (string): The relative filepath of the market geojson file

    Returns:
    Geopandas GeoDataFrame of the market geographies
    """
    markets_df = geopandas.read_file(market_filepath)
    markets_df.rename({column: column.lower() for column in markets_df.columns})
    log.info(
        f"Successfully converted market geojson into geodataframe of shape {markets_df.shape}"
    )
    print(markets_df.columns)
    log.info(markets_df.head())
    return markets_df


def merge_geopoints_with_markets(
    geo_df: geopandas.GeoDataFrame, market_df: geopandas.GeoDataFrame
) -> pd.DataFrame:
    """
    Method for merging (inner join) the geopoint dataframe with the market dataframe

    Parameters:
    geo_df: Geopandas GeoDataFrame of geopoints to map to markets
    market_df: GeoPandas GeoDataFrame of market geography polygons

    Returns:
    Geopandas GeoDataFrame of only the geopoints that resolved to markets
    (Could return them all by changing sjoin to left join)
    """
    geopoints_with_markets = geopandas.sjoin(
        geo_df, market_df, how="inner", op="intersects"
    )
    log.info(
        f"Successfully merged geopoints with markets\n Result shape {geopoints_with_markets.shape}\n Unable to resolve markets for {geopoints_with_markets.shape[0] - geo_df.shape[0]}"
    )
    # remove geography attribute
    result_df = geopoints_with_markets.drop("geometry", axis=1)
    log.info("Successfully dropped geography attribute")
    log.info(result_df.head())
    return result_df


def main():
    """
    Method for getting the config values and orchestrating the process
    """
    columns: list
    input_filepath: str
    market_filepath: str
    output_filepath: str
    separator: str
    df: pd.DataFrame
    geo_df: geopandas.GeoDataFrame
    market_df: geopandas.GeoDataFrame
    result_df: pd.DataFrame

    try:
        columns = CONFIG["columns"]
        input_filepath = CONFIG["input_filepath"]
        market_filepath = CONFIG["market_filepath"]
        output_filepath = CONFIG["output_filepath"]
        separator = CONFIG["separator"]

    except KeyError:
        log.exception("Missing one or more required config values")
        exit(1)

    try:
        df = get_input_dataframe(
            input_filepath=input_filepath, separator=separator, columns=columns
        )
    except ValueError as ve:
        log.exception(ve)
        exit(1)

    except Exception as e:
        log.exception(e)
        exit(1)

    try:
        geo_df = convert_to_geo_dataframe(df=df)

        market_df = get_market_geo_dataframe(market_filepath=market_filepath)

        result_df = merge_geopoints_with_markets(geo_df=geo_df, market_df=market_df)

        result_df.to_csv(output_filepath, index=False)

    except Exception as e:
        log.exception()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--columns", required=False)
    parser.add_argument("--input_filepath", required=False)
    parser.add_argument("--market_filepath", required=False)
    parser.add_argument("--output_filepath", required=False)
    parser.add_argument("--separator", required=False)
    arguments = vars(parser.parse_args())
    arguments = {k: v for k, v in arguments.items() if v}

    default = {
        "columns": [
            "country_code",
            "postal_code",
            "place_name",
            "admin_name_1",
            "admin_code_1",
            "admin_name_2",
            "admin_code_2",
            "admin_name_3",
            "admin_code_3",
            "latitude",
            "longitude",
            "accuracy",
        ],
        "input_filepath": "../input/us_zipcodes.csv",
        "market_filepath": "../input/nielsen-dma-markets.geo.json",
        "output_filepath": "../output/postal_codes_to_markets.csv",
        "separator": "\t",
    }

    config = {}
    config_file_path = "../conf/config.yml"

    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
    global CONFIG
    CONFIG = ChainMap(arguments, os.environ, config, default)
    main()
