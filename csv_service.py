
import pandas

class CsvService():
    # Should determine file path as method parameters instead set to attribute.
    def update_data_to_csv(self, data, file_path):
        data.to_csv(file_path, index = False)

    def get_csv_file_data(self, file_path):
        return pandas.read_csv(file_path)

        
