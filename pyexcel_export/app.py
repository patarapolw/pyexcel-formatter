import pyexcel
from collections import OrderedDict
from datetime import datetime
import os
import json
import copy
import yaml
import logging

from .serialize import RowExport, PyexcelExportEncoder, MyEncoder
from .defaults import Meta
from .formatter import ExcelFormatter
from .yaml_deserialize import MyYamlLoader

debugger_logger = logging.getLogger('debug')


class ExcelLoader:
    def __init__(self, in_file: str=None, **flags):
        if in_file:
            self.in_file = in_file
            self.meta = Meta(**flags)

            in_base, in_format = os.path.splitext(in_file)

            if in_format == '.xlsx':
                self.data = self._load_pyexcel_xlsx()
            elif in_format == '.json':
                if os.path.splitext(in_base)[1] == '.pyexcel':
                    self.data = self._load_pyexcel_json()
                else:
                    self.data = self._load_json()
            elif in_format in ('.yaml', '.yml'):
                self.data = self._load_yaml()
            else:
                raise ValueError('Unsupported file format, {}.'.format(in_format))
        else:
            self.meta = Meta(**flags)

    def _load_pyexcel_xlsx(self):
        updated_data = pyexcel.get_book_dict(file_name=self.in_file)
        self.meta['_styles'] = ExcelFormatter(self.in_file).data

        return self._set_updated_data(updated_data)

    def _load_pyexcel_json(self):
        with open(self.in_file) as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        for sheet_name, sheet_data in data.items():
            for j, row in enumerate(sheet_data):
                for i, cell in enumerate(row):
                    data[sheet_name][j][i] = json.loads(cell)

        return self._set_updated_data(data)

    def _load_json(self):
        with open(self.in_file) as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        return self._set_updated_data(data)

    def _load_yaml(self):
        with open(self.in_file) as f:
            data = yaml.load(f)

        return self._set_updated_data(data)

    def _set_updated_data(self, updated_data):
        data = OrderedDict()

        if '_meta' in updated_data.keys():
            for row in updated_data['_meta']:
                if not row or not row[0]:
                    break

                if len(row) < 2:
                    updated_meta_value = None
                else:
                    try:
                        updated_meta_value = list(json.loads(row[1]).values())[0]
                    except (json.decoder.JSONDecodeError, TypeError):
                        updated_meta_value = row[1]

                self.meta[row[0]] = updated_meta_value

            try:
                self.meta.move_to_end('modified', last=False)
                self.meta.move_to_end('created', last=False)
            except KeyError as e:
                debugger_logger.debug(e)

            updated_data.pop('_meta')

        for k, v in updated_data.items():
            data[k] = v

        return data

    @property
    def formatted_object(self):
        formatted_object = OrderedDict(
            _meta=self.meta.matrix
        )

        for sheet_name, sheet_data in self.data.items():
            formatted_sheet_object = []
            for row in sheet_data:
                formatted_sheet_object.append(RowExport(row))
            formatted_object[sheet_name] = formatted_sheet_object

        return formatted_object

    def save(self, out_file: str, retain_meta=True, out_format=None, retain_styles=True):
        self.meta['modified'] = datetime.fromtimestamp(datetime.now().timestamp()).isoformat()
        self.meta.move_to_end('modified', last=False)

        if 'created' in self.meta.keys():
            self.meta.move_to_end('created', last=False)

        if out_format is None:
            out_base, out_format = os.path.splitext(out_file)
        else:
            out_base = os.path.splitext(out_file)[0]

        save_data = copy.deepcopy(self.data)

        if retain_meta:
            save_data['_meta'] = self.meta.matrix
            if not retain_styles:
                for i, row in enumerate(save_data['_meta']):
                    if row[0] == '_styles':
                        save_data['_meta'].pop(i)
                        break

            save_data.move_to_end('_meta', last=False)
        else:
            if '_meta' in save_data.keys():
                save_data.pop('_meta')

        to_remove = []
        for sheet_name, sheet_matrix in save_data.items():
            if sheet_name == '_meta' or not sheet_name.startswith('_'):
                for i, row in enumerate(sheet_matrix):
                    if out_format == '.json':
                        save_data[sheet_name][i] = RowExport(row)
            else:
                to_remove.append(sheet_name)

        for sheet_name in to_remove:
            save_data.pop(sheet_name)

        if out_format == '.xlsx':
            self._save_openpyxl(out_file=out_file, out_data=save_data, retain_meta=retain_meta)
        elif out_format == '.json':
            if os.path.splitext(out_base)[1] == '.pyexcel':
                self._save_pyexcel_json(out_file=out_file, out_data=save_data)
            else:
                self._save_json(out_file=out_file, out_data=save_data)
        elif out_format in ('.yaml', '.yml'):
            self._save_yaml(out_file=out_file, out_data=save_data)
        else:
            raise ValueError('Unsupported file format, {}.'.format(out_file))

    def _save_openpyxl(self, out_file: str, out_data: OrderedDict, retain_meta: bool=True):
        formatter = ExcelFormatter(out_file)
        if os.path.exists(out_file):
            self.meta['_styles'] = formatter.data

        formatter.save(out_data, out_file, meta=self.meta, retain_meta=retain_meta)

    @staticmethod
    def _save_pyexcel_json(out_file: str, out_data: OrderedDict):
        with open(out_file, 'w') as f:
            export_string = json.dumps(out_data, cls=PyexcelExportEncoder,
                                       indent=2, ensure_ascii=False)
            f.write(export_string)

    @staticmethod
    def _save_json(out_file: str, out_data: OrderedDict):
        with open(out_file, 'w') as f:
            export_string = json.dumps(out_data, cls=MyEncoder,
                                       indent=2, ensure_ascii=False)
            f.write(export_string)

    @staticmethod
    def _save_yaml(out_file: str, out_data: OrderedDict):
        with open(out_file, 'w') as f:
            yaml.dump(out_data, f, allow_unicode=True)
