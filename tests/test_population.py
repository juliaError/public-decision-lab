from pathlib import Path

from disaster_nowcaster.admin import load_admin_units
from disaster_nowcaster.hazard import load_hazard
from disaster_nowcaster.population import compute_population_exposure


FIXTURES = Path(__file__).parent / "fixtures"


def test_population_exposure_sums_hazard_cells_by_admin():
    result = compute_population_exposure(
        FIXTURES / "population.tif",
        hazard=load_hazard(FIXTURES / "hazard.geojson"),
        admin=load_admin_units(FIXTURES / "admin.geojson"),
    )

    assert result.estimated_exposed_population == 20.0
    assert result.included_cell_count == 4
    assert result.exposed_population_by_admin == [
        {
            "admin_id": "admin_west",
            "admin_name": "Synthetic West District",
            "estimated_exposed_population": 10.0,
            "population_cell_count": 2,
        },
        {
            "admin_id": "admin_east",
            "admin_name": "Synthetic East District",
            "estimated_exposed_population": 10.0,
            "population_cell_count": 2,
        },
    ]
