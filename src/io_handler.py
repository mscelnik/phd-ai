import yaml
import pandas as pd


class IOHandler:
    @staticmethod
    def read_input_file(file_path):
        """
        Read a YAML input file.

        :param file_path: Path to the input file.
        :return: Parsed data as a dictionary.
        """
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    @staticmethod
    def write_output_file(data, file_path):
        """
        Write simulation results to a CSV file.

        :param data: Data to write (list of dictionaries).
        :param file_path: Path to the output file.
        """
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
