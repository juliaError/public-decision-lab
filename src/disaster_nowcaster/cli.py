"""Command-line interface for Disaster Impact Nowcaster."""

from __future__ import annotations

import argparse
from pathlib import Path

from disaster_nowcaster.admin import load_admin_units
from disaster_nowcaster.aoi import load_aoi
from disaster_nowcaster.exposure import compute_exposure
from disaster_nowcaster.hazard import load_hazard
from disaster_nowcaster.infrastructure import load_infrastructure
from disaster_nowcaster.population import compute_population_exposure
from disaster_nowcaster.report import write_outputs
from disaster_nowcaster.schemas import RunConfig


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="disaster-nowcaster",
        description="Generate a minimal local disaster exposure report.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a local exposure screen.")
    run_parser.add_argument("--aoi", required=True, type=Path, help="AOI polygon GeoJSON.")
    run_parser.add_argument(
        "--hazard", required=True, type=Path, help="Hazard polygon GeoJSON."
    )
    run_parser.add_argument(
        "--roads", required=True, type=Path, help="Road line GeoJSON."
    )
    run_parser.add_argument(
        "--facilities", required=True, type=Path, help="Facility point GeoJSON."
    )
    run_parser.add_argument(
        "--admin", required=True, type=Path, help="Administrative boundary GeoJSON."
    )
    run_parser.add_argument(
        "--population",
        type=Path,
        help="Optional local population raster GeoTIFF with people-per-cell values.",
    )
    run_parser.add_argument(
        "--output", required=True, type=Path, help="Output directory for generated files."
    )
    run_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing generated files in an existing output directory.",
    )
    run_parser.set_defaults(func=run_command)
    return parser


def run_command(args: argparse.Namespace) -> int:
    """Execute the run subcommand."""

    config = RunConfig(
        aoi=args.aoi,
        hazard=args.hazard,
        roads=args.roads,
        facilities=args.facilities,
        admin=args.admin,
        population=args.population,
        output=args.output,
        overwrite=args.overwrite,
    )

    aoi = load_aoi(config.aoi)
    hazard = load_hazard(config.hazard)
    roads = load_infrastructure(config.roads, name="roads")
    facilities = load_infrastructure(config.facilities, name="facilities")
    admin = load_admin_units(config.admin)
    population_exposure = (
        compute_population_exposure(config.population, hazard=hazard, admin=admin)
        if config.population
        else None
    )

    result = compute_exposure(
        aoi=aoi,
        hazard=hazard,
        roads=roads,
        facilities=facilities,
        admin=admin,
        population_exposure=population_exposure,
    )
    written = write_outputs(result, config, aoi=aoi, hazard=hazard, admin=admin)

    print(f"Wrote {len(written)} files to {config.output}")
    print(
        "Exposure estimates only: "
        f"{result.affected_road_count} potentially affected roads, "
        f"{result.affected_facility_count} facilities located within the hazard extent."
    )
    if result.population_exposure:
        print(
            "Estimated exposed population: "
            f"{result.population_exposure.estimated_exposed_population:.2f}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
