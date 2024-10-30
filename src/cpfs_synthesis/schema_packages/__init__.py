from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class NewSchemaBridgmanEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from cpfs_synthesis.schema_packages.bridgman import m_package

        return m_package


class NewSchemaCVTEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from cpfs_synthesis.schema_packages.cvt import m_package

        return m_package


class NewSchemaCzochalskiEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from cpfs_synthesis.schema_packages.czochalski import m_package

        return m_package


class NewSchemaFloatingZoneEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from cpfs_synthesis.schema_packages.floatingzone import m_package

        return m_package


class NewSchemaFluxGrowthEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from cpfs_synthesis.schema_packages.fluxgrowth import m_package

        return m_package


schema_bridgman_entry_point = NewSchemaBridgmanEntryPoint(
    name='NewSchemaBridgman',
    description='New schema package entry point configuration.',
)

schema_cvt_entry_point = NewSchemaCVTEntryPoint(
    name='NewSchemaCVT',
    description='New schema package entry point configuration.',
)

schema_czochalski_entry_point = NewSchemaCzochalskiEntryPoint(
    name='NewSchemaCzochalski',
    description='New schema package entry point configuration.',
)

schema_floatingzone_entry_point = NewSchemaFloatingZoneEntryPoint(
    name='NewSchemaFloatingZone',
    description='New schema package entry point configuration.',
)

schema_fluxgrowth_entry_point = NewSchemaFluxGrowthEntryPoint(
    name='NewSchemaFluxGrowth',
    description='New schema package entry point configuration.',
)
