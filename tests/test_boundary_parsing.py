import pytest
from pyrosm import get_path


@pytest.fixture
def helsinki_pbf():
    pbf_path = get_path("helsinki_pbf")
    return pbf_path


@pytest.fixture
def helsinki_region_pbf():
    pbf_path = get_path("helsinki_region_pbf")
    return pbf_path


def test_reading_boundaries_with_defaults(helsinki_pbf):
    from pyrosm import OSM
    osm = OSM(helsinki_pbf)
    gdf = osm.get_boundaries()

    # Test shape
    assert gdf.shape == (8, 11)
    required_columns = ['name', 'admin_level', 'boundary', 'id', 'timestamp', 'version',
                        'changeset', 'geometry', 'tags', 'osm_type']
    for col in required_columns:
        assert col in gdf.columns

    # osm_type should be 'relation'
    assert gdf.osm_type.unique()[0] == 'relation'


def test_reading_boundaries_with_name_search(helsinki_pbf):
    from pyrosm import OSM
    osm = OSM(helsinki_pbf)

    # Full name and also partial name should work and produce data
    # 'saari' is included in 'Siltasaari'
    names = ["Punavuori", "saari"]

    for name in names:
        gdf = osm.get_boundaries(name=name)

        # Should now only contain one row
        assert gdf.shape == (1, 11)

        required_columns = ['name', 'admin_level', 'boundary', 'id', 'timestamp', 'version',
                            'changeset', 'geometry', 'tags', 'osm_type']
        for col in required_columns:
            assert col in gdf.columns

        # osm_type should be 'relation'
        assert gdf.osm_type.unique()[0] == 'relation'


def test_reading_all_boundaries(helsinki_region_pbf):
    from pyrosm import OSM
    osm = OSM(helsinki_region_pbf)
    gdf = osm.get_boundaries(boundary_type="all")

    # Test shape
    assert gdf.shape == (733, 19)

    required_columns = ['name', 'admin_level', 'boundary', 'id', 'timestamp', 'version',
                        'changeset', 'geometry', 'tags', 'osm_type']

    for col in required_columns:
        assert col in gdf.columns

    # Test filtering different types of boundaries
    value_counts = gdf['boundary'].value_counts()

    for boundary_type, cnt in value_counts.items():
        # Some incorrect boundary types exists in the data
        if boundary_type in ["lot 1", "imagery", "historic"]:
            continue

        gdf = osm.get_boundaries(boundary_type=boundary_type)
        assert len(gdf) >= cnt, f"Got incorrect number of rows with {boundary_type}"


def test_passing_incorrect_parameters(helsinki_pbf):
    from pyrosm import OSM
    osm = OSM(helsinki_pbf)
    try:
        gdf = osm.get_boundaries(boundary_type="incorrect")
    except ValueError as e:
        if "should be one of the following" in str(e):
            pass
    except Exception as e:
        raise e

    try:
        gdf = osm.get_boundaries(name=1)
    except ValueError as e:
        if "should be text" in str(e):
            pass
    except Exception as e:
        raise e

