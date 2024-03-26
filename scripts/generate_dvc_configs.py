from itertools import product
from abc import ABC, abstractmethod

import numpy as np
import yaml


class ConfigurationMatrixInterface(ABC):
    @abstractmethod
    def get_configuration(self, idx):
        pass

    @abstractmethod
    def get_shape(self):
        pass

    @abstractmethod
    def get_axes(self):
        pass

    @abstractmethod
    def axis_components(self, axis_name):
        pass


class ConfigurationMatrix(ConfigurationMatrixInterface):
    def __init__(self, axis, variants):
        self._axis_idx = list(range(len(axis)))
        self._axis_names = axis

        variants_by_idx = {}
        for variant in variants:
            axe_name = list(variant.keys())[0]
            if axe_name not in self._axis_names:
                print(f"[WARNING] There is not '{axe_name}' axe in axis list")
                continue
            axe_id = self._axis_names.index(axe_name)
            variants_by_idx[axe_id] = variant[axe_name]

        self._matrix_components = []
        for axe_id in self._axis_idx:
            self._matrix_components.append(variants_by_idx[axe_id])

        self._matrix = np.array(
            np.meshgrid(*[list(range(len(matrix_component))) for matrix_component in self._matrix_components],
                        indexing='ij')
        )
        self._shape = self._matrix.shape[1:]

    def get_configuration(self, idx):
        return [self._matrix_components[m][self._matrix[m][idx]] for m in self._axis_idx]

    def get_axes(self):
        return self._axis_names

    def axis_components(self, axis_name):
        return self._matrix_components[self._axis_names.index(axis_name)]

    def get_shape(self):
        return self._shape


class ConfigurationMatrixWithExcludes(ConfigurationMatrixInterface):
    def __init__(self, configuration_matrix: ConfigurationMatrixInterface, excludes):
        self._configuration_matrix = configuration_matrix

        self._excludes = []
        for exclude in excludes:
            if len(exclude.keys()) != len(exclude.keys() & self._configuration_matrix.get_axes()):
                raise RuntimeError("Exclude configuration isn't correct. Not all excluded axes exists in matrix")
            exclude_idx = []
            for axis_name in self._configuration_matrix.get_axes():
                if axis_name in exclude:
                    exclude_idx.append(
                        [i for i, val in enumerate(self._configuration_matrix.axis_components(axis_name)) if
                         val in exclude[axis_name]])
                else:
                    exclude_idx.append(list(range(len(self._configuration_matrix.axis_components(axis_name)))))
            self._excludes.extend(list(product(*exclude_idx)))

    def get_configuration(self, idx):
        if idx in self._excludes:
            return None
        return self._configuration_matrix.get_configuration(idx)

    def get_axes(self):
        return self._configuration_matrix.get_axes()

    def axis_components(self, axis_name):
        return self._configuration_matrix.axis_components(axis_name)

    def get_shape(self):
        return self._configuration_matrix.get_shape()


class PrintableConfigurationMatrix:
    """This class is for debug only"""
    def __init__(self, configuration_matrix: ConfigurationMatrixInterface):
        self.configuration_matrix = configuration_matrix

    def _get_all_configuration(self):
        length_per_dimension = self.configuration_matrix.get_shape()
        indexes_for_all_elements = product(*[list(range(length)) for length in length_per_dimension])
        return [self.configuration_matrix.get_configuration(idx) for idx in indexes_for_all_elements]

    def print(self):
        for configuration in self._get_all_configuration():
            print(configuration)

class DvcConfigurations:
    def __init__(self, configuration_matrix: ConfigurationMatrixInterface, batch_size=1):
        self._configuration_matrix = configuration_matrix
        self._batch_size = batch_size

    def _get_all_configuration(self):
        length_per_dimension = self._configuration_matrix.get_shape()
        indexes_for_all_elements = product(*[list(range(length)) for length in length_per_dimension])
        return [self._configuration_matrix.get_configuration(idx) for idx in indexes_for_all_elements]

    def get_configuration_strings(self):
        configurations = self._get_all_configuration()
        configurations = [configuration for configuration in configurations if configuration is not None]

        configurations_batches = []
        configurations_batch = []
        for configuration in configurations:
            if np.prod([len(np.unique(i)) for i in np.array([*configurations_batch, configuration]).T]) > self._batch_size:
                configurations_batches.append(configurations_batch)
                configurations_batch = []
                configurations_batch.append(configuration)
            else:
                configurations_batch.append(configuration)
        configurations_batches.append(configurations_batch)

        configuration_strings = []
        for batch in configurations_batches:
            values_per_axis = {i: list(set(values)) for (i, values) in enumerate(np.column_stack(batch))}
            configuration_strings.append("-S "+ " -S ".join([f"{axis}=\"{','.join(values_per_axis[i])}\"" for i, axis in enumerate(self._configuration_matrix.get_axes())]))
        return configuration_strings

if __name__ == '__main__':
    input_file = "tests.yaml"
    test_name = "sanity_check"
    jobs_pers_config = 4
    output_file = "dvc_configuration_strings.yaml"

    with open(input_file) as f:
        y = yaml.safe_load(f)

    configuration = y['tests'][test_name]
    configuration_matrix = ConfigurationMatrix(
        configuration['axis'],
        configuration['variants']
    )
    configuration_matrix = ConfigurationMatrixWithExcludes(configuration_matrix, configuration['excludes'])

    printable_configuration_matrix = PrintableConfigurationMatrix(configuration_matrix)
    dvc_configurations = DvcConfigurations(configuration_matrix, jobs_pers_config)
    configuration_strings = dvc_configurations.get_configuration_strings()

    with open(output_file, "w") as f:
        yaml.dump(configuration_strings, f)