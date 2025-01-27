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
from structlog.stdlib import (
    BoundLogger,
)

from cpfs_synthesis.cpfs_schemes import (
    CPFSCrystal,
    CPFSCrystalGrowthTube,
    CPFSInitialSynthesisComponent,
)

configuration = config.get_plugin_entry_point(
    'cpfs_synthesis.schema_packages:schema_cvt_entry_point'
)

m_package = Package(name='MPI CPFS CVT')


class CPFSChemicalVapourTransportStep(ActivityStep, EntryData):
    """
    A step in the Chemical Vapour Transport. Contains 2 temperatures and transport agent
    """

    temperature_low = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity', defaultDisplayUnit='celsius'
        ),
    )
    temperature_high = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity', defaultDisplayUnit='celsius'
        ),
    )
    duration = Quantity(
        type=float,
        unit='hour',
        a_eln=ELNAnnotation(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `ChemicalVapourTransportStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class CPFSChemicalVapourTransportSushmita(CrystalGrowth, EntryData):
    """
    Application definition section for a Chemical Vapour Transport at MPI CPFS.
    """

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0002652'],
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'furnace',
                    'tube',
                    'initial_materials',
                    'steps',
                    'resulting_crystal',
                ],
            ),
            lane_width='600px',
        ),
    )
    method = Quantity(
        type=str,
        default='Chemical Vapour Transport',
    )
    grower = Quantity(
        type=str,
        default='Sushmita Chandra',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    target_material = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    tube = SubSection(
        section_def=CPFSCrystalGrowthTube,
    )
    initial_materials = SubSection(
        section_def=CPFSInitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        section_def=CPFSChemicalVapourTransportStep,
        # repeats=False,
    )
    transport_agent = SubSection(
        section_def=CPFSInitialSynthesisComponent,
    )
    resulting_crystal = Quantity(
        type=CPFSCrystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `Chemical Vapour Transport` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)

        delattr(self, CPFSChemicalVapourTransportSushmita.ending_time)
        delattr(self, CPFSChemicalVapourTransportSushmita.instruments)
        delattr(self, CPFSChemicalVapourTransportSushmita.samples)

        if not self.location:
            self.location = 'MPI CPfS Dresden'


m_package.__init_metainfo__()
