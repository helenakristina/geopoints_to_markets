# Geopoints to Nielsen DMA (Designated Market Areas)

## Purpose of this project

This project solves the issue of resolving any file with CSV geographical datapoints to Nielsen DMA markets. Additionally, DMA geojson file can be replaced with any other geojson boundary file if other divisions are desired.

Default dataset resolves US zip codes to Nielsen DMAs.

Input (optional if different geopoint values are desired):

- Any CSV file(separator need not be comma, that is part of the config) file without headers that contains fields longitude and latitude -- CSV file should be placed in input folder
- Any GEOJSON file for boundaries (optional if don't want to use Nielsen DMAs as the boundaries)

_Config_:

- all config values are optional, if none are entered, program will output a filename called postal_codes_to_markets.csv that contains US postal codes and the Nielsen DMAs that they resolve to
- Config values will be set by (in order of preference):
  - command line arguments
  - environment variables
  - config.yml
  - default values
- I included the default values in both the config.yml and the default dictionary as examples of how they can be set
  
- Config values
  - input_filepath(should be in input folder): default `input/us_zipcodes.csv`
  - market_filepath(should be in input folder): (geojson file that designates the market area. Defaults to Nielsen DMA market, but can be used with any GEOJSON file that divides US into markets eg.states, regions, etc.) default: `input/nielsen-dma-markets.geo.json`
  - output_filepath: will end up in output volume: default `output/postal_codes_to_markets.csv`
  - separator: default: `"\t"`
  - columns: array of headers of input file
    - columns array must include fields longitude and latitude (case insensitive, will all be converted to lower case)

Also includes Jupyter notebook for running locally step by step, must have all the dependencies installed.

### Usage

- Clone repo
- Navigate to top level folder
  - If you want to change your config, you can modify values using one of the options listed in the config section
- Must have Docker installed
  - Build: `docker build -t geopoints_to_markets .`
  - `docker run --mount type=bind,target=/opt/app/output,source=$PWD/output --rm geopoints_to_markets`
  - Windows: `docker run --mount type=bind,target=/opt/app/output,source=%CD%/output --rm geopoints_to_markets`
- result file should be in output folder
