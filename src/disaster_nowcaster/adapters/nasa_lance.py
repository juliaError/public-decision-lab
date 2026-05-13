"""Local NASA LANCE-style flood raster adapter."""

from __future__ import annotations

from pathlib import Path

from disaster_nowcaster.adapters.base import AdapterMetadata, AdapterResult
from disaster_nowcaster.adapters.raster_hazard import (
    write_thresholded_raster_hazard_geojson,
)
from disaster_nowcaster.events import DisasterEvent
from disaster_nowcaster.hazard import load_hazard


class LocalNasaLanceFloodAdapter:
    """Convert a local NASA LANCE-style flood GeoTIFF into hazard GeoJSON.

    This adapter does not download NASA data. It thresholds an existing local
    raster and polygonizes cells that meet the configured flood value.
    """

    def __init__(
        self,
        raster_path: str | Path,
        output_geojson: str | Path,
        *,
        flood_value: float = 1.0,
        source_name: str = "NASA LANCE-style local flood raster",
        source_url: str | None = "https://earthdata.nasa.gov/earth-observation-data/near-real-time",
        license_or_terms: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        self.raster_path = Path(raster_path)
        self.output_geojson = Path(output_geojson)
        self.flood_value = flood_value
        self.metadata = AdapterMetadata(
            source_name=source_name,
            source_url=source_url,
            license_or_terms=license_or_terms,
            spatial_resolution="source raster resolution; often product-specific",
            temporal_resolution="source raster temporal coverage; product-specific",
            update_frequency="not checked by local adapter",
            source_type="manual",
            observed_or_modeled="remote_sensing_product",
            known_limitations=[
                "This adapter only reads a local raster; it does not download NASA LANCE data.",
                "Flood threshold semantics depend on the source product and must be verified.",
                "Output is a hazard exposure input, not confirmed damage.",
                "No reprojection is performed; raster and downstream vector inputs must align.",
            ],
            auto_downloaded=False,
            notes=notes or [],
        )

    def prepare(self, event: DisasterEvent | None = None) -> AdapterResult:
        """Write thresholded flood pixels to local hazard GeoJSON."""

        if event and event.hazard_type != "flood":
            raise ValueError(
                f"NASA LANCE flood adapter requires flood event, got "
                f"{event.hazard_type!r}."
            )
        write_thresholded_raster_hazard_geojson(
            self.raster_path,
            self.output_geojson,
            threshold=self.flood_value,
            source="local_nasa_lance_style_raster",
            value_property="flood_value",
        )
        load_hazard(self.output_geojson)
        return AdapterResult(
            path=self.output_geojson,
            layer_name="hazard",
            metadata=self.metadata,
        )
