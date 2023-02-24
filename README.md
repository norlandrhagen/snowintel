# snowintel

**Warning: In development, nothing stable**

## Installation

`pip install git+https://github.com/norlandrhagen/snowintel`

### Activate Environment

If you're using miniconda/micromamba, run

`mamba create -f environment.yml`

Then:

`mamba activate snowintel`

This should install all the required packages.

## Example Usage

### Get Site Information

```python
from snowintel.core import getSites

gs = getSites()
```

### Retrieve Data for a SNOTEL Site

```python
from snowintel.utils import get_snotel_data_by_site_id

df = get_snotel_data_by_site_id(site_id='865_UT_SNTL',start_date='2023-01-01',end_date='2023-02-23',variable='SNWD_D')
```

### Visualize Sites

```python

from snowintel.core import GetSites
import folium

gs = GetSites(state_filter="UT")

gdf = gs.geodataframe()

m = gs.return_map()

m

```

## ToDo

- Docs
- Tests
- Mapping

GetSites:

- ToDo / Future Methods:
- Find nearest n sites. Input site_ID & n closest sites
- Find sites within radius of site
- Find sites within radius of input lat/lon pair
- Filter sites by elevation

snotel_sites = {
"WIDTSOE_3": "SNOTEL:865_UT_SNTL",
"CLAYTON_SPRINGS": "SNOTEL:983_UT_SNTL",
"AGUA_CANYON": "SNOTEL:907_UT_SNTL",
"SUNFLOWER_FLAT": "SNOTEL:1249_UT_SNTL",
"DONKEY_RESERVOIR": "SNOTEL:452_UT_SNTL",
}
