# pyexcel-export - Keep optimal formatting when exported to xlsx format

pyexcel-export is a wrapper around [pyexcel](https://github.com/pyexcel/pyexcel), [pyexcel-xlsx](https://github.com/pyexcel/pyexcel-xlsx) and [openpyxl](https://bitbucket.org/openpyxl/openpyxl) to read the formatting (stylesheets) and update the pre-existing file without destroying the stylesheets.

pyexcel-export also introduces two new exporting format, `*.yaml` and `*.pyexcel.json` which is based on [NoIndentEncoder](https://stackoverflow.com/a/25935321/9023855). This allows you to edit the spreadsheet in you favorite text editor, without being frustrated by automatically collapsed cells in Excel.

## Known constraints

The "stylesheets" exported from Excel is in a very long base64 encoded format when exported to `*.json` or `*.pyexcel.json`, so exporting such to `*.json` is disabled by default.

As stylesheets copying works by [`openpyxl.worksheet.copier.WorksheetCopy`](https://openpyxl.readthedocs.io/en/2.5/_modules/openpyxl/worksheet/copier.html), it may work only on values, styles, dimensions and merged cells, but charts might not be supported.

## Installation

You can install pyexcel-export via pip:

```commandline
$ pip install pyexcel-export
```

or clone it and install it.

## Usage

For more documentation, see https://github.com/patarapolw/pyexcel-export/tree/master/docs

### Read \*.pyexcel.json

```python
>>> from pyexcel_export import get_data
>>> from collections import OrderedDict
>>> data, meta = get_data('test.yaml')  # *.pyexcel.json is also possible.
>>> data
OrderedDict([('test', [['id', 'English', 'Pinyin', 'Hanzi', 'Audio', 'Tags'], [1419644212689, 'Hello!', 'Nǐ hǎo!', '你好！', '[sound:tmp1cctcn.mp3]', ''], [1419644212690, 'What are you saying?', 'Nǐ shuō shénme?', '你说什么？', '[sound:tmp4tzxbu.mp3]', ''], [1419644212691, 'What did you do?', 'nǐ zuò le shénme ?', '你做了什么？', '[sound:333012.mp3]', '']])])
>>> meta
Meta([
  created : '2018-07-15T18:26:05.879991',
  has_header : True,
  freeze_header : True,
  col_width_fit_param_keys : True,
  col_width_fit_ids : True,
  bool_as_string : True,
  allow_table_hiding : True,
  _styles : <_io.BytesIO object at 0x10553b678>
])
>>> meta.matrix
[('created', '2018-07-15T05:32:43.976194'), ('modified', '2018-07-15T05:32:52.248192'), ('has_header', True), ('freeze_header', True), ('col_width_fit_param_keys', True), ('col_width_fit_ids', True), ('allow_hidden_tables', True), ('_styles', {"<class '_io.BytesIO'>": <_io.BytesIO object at 0x1103d9048>})]
>>> meta.excel_matrix
[('created', '2018-07-15T05:32:43.976194'), ('modified', '2018-07-15T05:32:52.248192'), ('has_header', {"<class 'bool'>": True}), ('freeze_header', {"<class 'bool'>": True}), ('col_width_fit_param_keys', {"<class 'bool'>": True}), ('col_width_fit_ids', {"<class 'bool'>": True}), ('allow_hidden_tables', {"<class 'bool'>": True}), ('_styles', {"<class '_io.BytesIO'>": <_io.BytesIO object at 0x10b56b048>})]
```

### Exporting stylesheets

```python
>>> from pyexcel_export import get_meta
>>> get_meta()
Meta([
  created : '2018-07-15T18:26:05.879991',
  has_header : True,
  freeze_header : True,
  col_width_fit_param_keys : True,
  col_width_fit_ids : True,
  bool_as_string : True,
  allow_table_hiding : True
])
>>> get_meta('test.xlsx')
Meta([
  created : '2018-07-15T18:26:05.879991',
  has_header : True,
  freeze_header : True,
  col_width_fit_param_keys : True,
  col_width_fit_ids : True,
  bool_as_string : True,
  allow_table_hiding : True,
  _styles : <_io.BytesIO object at 0x10553b678>
])
```
### Saving files, while preserving the formatting.

```python
>>> from pyexcel_export import get_meta, save_data
>>> from collections import OrderedDict
>>> meta = get_meta('test.xlsx')
>>> data = OrderedDict()
>>> data.update({"Sheet 1": [["header A", "header B", "header C"], [1, 2, 3]]})
>>> save_data("your_file.xlsx", data, meta=meta)
```
### \*.yaml format

```yaml
!!python/object/apply:collections.OrderedDict
- - - _meta
    - - !!python/tuple [created, '2018-07-15T05:32:43.976194']
      - !!python/tuple [modified, '2018-07-15T13:31:47.725480']
      - !!python/tuple [has_header, true]
      - !!python/tuple [freeze_header, true]
      - !!python/tuple [col_width_fit_param_keys, true]
      - !!python/tuple [col_width_fit_ids, true]
      - !!python/tuple [allow_hidden_tables, true]
  - - test
    - - [id, English, Pinyin, Hanzi, Audio, Tags]
      - [1419644212689, Hello!, Nǐ hǎo!, 你好！, '[sound:tmp1cctcn.mp3]', '']
      - [1419644212690, 'What are you saying?', 'Nǐ shuō shénme?', 你说什么？, '[sound:tmp4tzxbu.mp3]',
        '']
      - [1419644212691, 'What did you do?', 'nǐ zuò le shénme ?', 你做了什么？, '[sound:333012.mp3]',
        '']

```

### \*.pyexcel.json format
```json
{
  "_meta": [
    ["\"created\"", "\"2018-07-12T15:21:25.777499\""],
    ["\"modified\"", "\"2018-07-15T06:59:22.707162\""],
    ["\"has_header\"", "true"],
    ["\"freeze_header\"", "true"],
    ["\"col_width_fit_param_keys\"", "true"],
    ["\"col_width_fit_ids\"", "true"]
  ],
  "test": [
    ["\"id\"", "\"English\"", "\"Pinyin\"", "\"Hanzi\"", "\"Audio\"", "\"Tags\""],
    ["1419644212689", "\"Hello!\"", "\"Nǐ hǎo!\"", "\"你好！\"", "\"[sound:tmp1cctcn.mp3]\"", "\"\""],
    ["1419644212690", "\"What are you saying?\"", "\"Nǐ shuō shénme?\"", "\"你说什么？\"", "\"[sound:tmp4tzxbu.mp3]\"", "\"\""],
    ["1419644212691", "\"What did you do?\"", "\"nǐ zuò le shénme ?\"", "\"你做了什么？\"", "\"[sound:333012.mp3]\"", "\"\""]
  ]
}
```
