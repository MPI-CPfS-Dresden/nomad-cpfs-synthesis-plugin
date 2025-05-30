#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nomad.config import config
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    BrowserAnnotation,
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    ActivityStep,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad_material_processing.crystal_growth import (
    CrystalGrowth,
)
from nomad_material_processing.utils import (
    create_archive,
)
from structlog.stdlib import (
    BoundLogger,
)

from cpfs_synthesis.cpfs_schemes import (
    CPFSCrystal,
    CPFSFurnace,
    CPFSInitialSynthesisComponent,
    CPFSRodInformation,
)

configuration = config.get_plugin_entry_point(
    'cpfs_synthesis.schema_packages:schema_floatingzone_entry_point'
)

m_package = Package(name='MPI CPFS FLOATING ZONE')


class CPFSFloatingZoneProcessStep(ActivityStep, EntryData):
    """
    A step in the Floating Zone Process, for now same as CzochralskiProcessStep.
    """

    melting_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    growth_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    rotation_speed = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(component='NumberEditQuantity', defaultDisplayUnit='hertz'),
    )
    rotation_direction = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    pulling_rate = Quantity(
        type=float,
        unit='meter/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity', defaultDisplayUnit='millimeter/minute'
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `FloatingZoneProcessStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class CPFSFloatingZoneProcess(CrystalGrowth, EntryData):
    """
    Application definition section for a Floating Zone Process at MPI CPFS.
    """

    m_def = Section(
        links=[''],
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'end_time',
                ],
            ),
            lane_width='600px',
        ),
    )
    method = Quantity(
        type=str,
        default='Floating Zone Process',
    )
    furnace = SubSection(
        section_def=CPFSFurnace,
    )
    rod_information = SubSection(
        section_def=CPFSRodInformation,
    )
    initial_materials = SubSection(
        section_def=CPFSInitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        section_def=CPFSFloatingZoneProcessStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=CPFSCrystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )
    xlsx_file = Quantity(
        type=str,
        description="""
        The xlsx file with data (optional). (.xlsx file).
        """,
        a_browser=BrowserAnnotation(adaptor='RawFileAdaptor'),
        a_eln=ELNAnnotation(component='FileEditQuantity'),
    )
    lab_id = Quantity(
        type=str,
        description="""An ID string that is unique at least for the lab that produced
        this data.""",
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `FloatingZoneProcess` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        self.location = 'MPI CPfS Dresden'
        if self.xlsx_file:
            import pandas as pd

            with archive.m_context.raw_file(self.xlsx_file, 'r') as xlsx:
                inp = pd.read_csv(xlsx)
                if inp.loc[2][1].split()[1] == 'CPFSFloatingZone':
                    self.name = str(inp.loc[10][2])
                    self.furnace = CPFSFurnace(name=str(inp.loc[13][2]))
                    self.furnace.normalize(archive, logger)
                    self.rod_information = CPFSRodInformation(
                        rod_preparation=str(inp.loc[16][2]),
                        seed_rod_diameter=float(inp.loc[17][2]) / 1000,
                        feed_rod_diameter=float(inp.loc[18][2]) / 1000,
                        feed_rod_crystal_direction=str(inp.loc[19][2]),
                    )
                    step = []
                    step.append(
                        CPFSFloatingZoneProcessStep(
                            melting_power_in_percent=float(inp.loc[31][2]),
                            growth_power_in_percent=float(inp.loc[32][2]),
                            rotation_speed=float(inp.loc[33][2]),
                            rotation_direction=str(inp.loc[34][2]),
                            pulling_rate=float(inp.loc[35][2]) / 1000 / 60,
                        )
                    )
                    self.steps = step
                    components = []
                    for i in range(5):
                        if not pd.isna(inp.loc[24 + i][1]):
                            single_component = CPFSInitialSynthesisComponent(
                                name=str(inp.loc[24 + i][1]),
                                state=str(inp.loc[24 + i][2]),
                                weight=float(inp.loc[24 + i][3]),
                                providing_company=str(inp.loc[24 + i][4]),
                            )
                            single_component.normalize(archive, logger)
                            components.append(single_component)
                    self.initial_materials = components
                    crystal_ref = create_archive(
                        CPFSCrystal(
                            name=str(inp.loc[38][2]) + '_' + str(inp.loc[39][2]),
                            sample_id=str(inp.loc[38][2]),
                            achieved_composition=str(inp.loc[39][2]),
                            final_crystal_length=float(inp.loc[40][2]) / 1000,
                            single_poly=str(inp.loc[41][2]),
                            crystal_shape=str(inp.loc[42][2]),
                            crystal_orientation=str(inp.loc[43][2]),
                            safety_reactivity=str(inp.loc[44][2]),
                            description=str(inp.loc[45][2]),
                        ),
                        archive,
                        str(inp.loc[38][2])
                        + '_'
                        + str(inp.loc[39][2])
                        + '_CPFSCrystal.archive.json',
                    )
                    self.resulting_crystal = crystal_ref
                else:
                    self.xlsx_file = 'Not a valid CPFSFloatingZoneProcess template.'


m_package.__init_metainfo__()
