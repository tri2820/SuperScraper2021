#!python -Wignore main.py | jq -C | less -R

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd
from dataclasses import dataclass, field
from pandas.core.frame import DataFrame

# pd.set_option('display.max_rows', None)

# ----------------------------
from itertools import repeat
@dataclass
class Format:
    header_row: int
    name_row: str
    unknown_rows: list[int] = field(default_factory=list)
    # groups_meta:
    

@dataclass
class SheetReader:
    format: Format
    name: str


@dataclass
class GroupedCol:
    min: int
    max: int

@dataclass
class View:
    group: GroupedCol
    name: str

@dataclass
class Table:
    name: str
    data: DataFrame
    views : list[View]

MaskedUnit = None

# ----------------------------

def merge(outlines: list[GroupedCol]):
    result : list[GroupedCol] = []
    for o in outlines:
        mismatched = result == [] or result[-1].max+1 < o.min
        if mismatched: result.append(o) 
        else: result[-1] = GroupedCol(result[-1].min, o.max)
    return result

def extract_groups(ws: Worksheet):
    dim = ws.column_dimensions
    maybeBounds = map(lambda d: GroupedCol(d.min, d.max) if d.outlineLevel == 1 else None, dim.values())
    bounds = filter(lambda o: o is not None, maybeBounds)
    groups = merge(bounds)
    return groups

def read(F : Format, data: DataFrame, groups : list[GroupedCol]) -> Table :
    name = data.iloc[F.name_row][0]
    data.replace(to_replace=[r'\\t|\\n|\\r,\t|\n|\r', r'^\*$', '%$'], value=[' ', MaskedUnit, ''], regex=True, inplace=True)
    data.iloc[F.header_row] = data.iloc[F.header_row].str.strip()
    data.columns = data.iloc[F.header_row]
    data.drop([F.name_row, F.header_row, *F.unknown_rows], inplace=True)

    default_view_names = map(lambda g: f'Group {g.min}', groups)
    views = map(lambda gn: View(gn[0], gn[1]), zip(groups, default_view_names))
    
    return Table(name, data, list(views))

def loadWorkSheet(bookname: str, S : SheetReader) -> DataFrame:
    df = pd.read_excel(bookname, sheet_name=S.name)
    groups = loadGroupInfos(bookname, S.name)
    table = read(S.format, df, groups)
    return table

from openpyxl import load_workbook
def loadGroupInfos(bookname: str, sheetname: str):
    wb : Workbook = load_workbook(bookname)
    ws : Worksheet = wb[sheetname]
    groups = extract_groups(ws)
    return groups

from itertools import chain
import sys
import json
def jsonify(t: Table):
    groups = list(map(lambda v: v.group, t.views))
    subdatas = list(map(lambda g: t.data.iloc[:, g.min-1:g.max], groups))
    drop_ind = set(chain(*list(map(lambda g: range(g.min-1, g.max), groups))))
    table_ind = list(set(range(0, t.data.shape[1])) - drop_ind)
    table = t.data.iloc[:, table_ind]

    # print(table)

    # Check unique
    # If not, use the one above as extra key

    try:
        J = table.to_json(orient='records')
    except Exception as e:
        counts = table.columns.value_counts()
        print(f'Cannot convert table to json', file=sys.stderr)
        print(e)
        # Some may due to group inside group
        print(table.columns)
        return None

    J = json.loads(J)

    for (i,v) in enumerate(t.views):
        try:
            records = json.loads(subdatas[i].to_json(orient='records'))
            view_jsons = list(map(lambda r: {v.name : r}, records))
            for (j,_) in enumerate(J): J[j].update(view_jsons[j])
        except Exception as e:
            counts = subdatas[i].columns.value_counts()
            print(f'Cannot convert {v.name} to json, skip', file=sys.stderr)
            print(e)
            print(counts)
        
    return J
    
# ----------------------------

# bookname = 'Annual fund-level superannuation statistics June 2020.xlsx'

# Working
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 1')
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 2')
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 3')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 7')
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 8')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 9')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 11')

# Not working
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 4')
# S = SheetReader(Format(3, 0, [1,2,4,5]), 'Table 5')
# S = SheetReader(Format(5, 0, [1,2,3,4,6,7]), 'Table 6')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 10')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 12')
# S = SheetReader(Format(4, 0, [1,2,3,5,6]), 'Table 13')


# -----------------------------
bookname = 'Quarterly MySuper statistics backseries September 2013 - June 2019.xlsx'
# Not working - Group inside group, multiple nan columns
S = SheetReader(Format(3, 0, [0,1,2,4,5]), 'Table 2a')
S = SheetReader(Format(3, 0, [0,1,2,4,5]), 'Table 2b')

# Working
S = SheetReader(Format(2, 0, [0,1,3,4]), 'Table 1b')
S = SheetReader(Format(2, 0, [0,1,3,4]), 'Table 1a')
S = SheetReader(Format(3, 0, [0,1,2,4,5]), 'Table 3')
S = SheetReader(Format(1, 0, [0,2,3]), 'Table 4')
S = SheetReader(Format(2, 0, [0,1,3,4]), 'Table 5')
S = SheetReader(Format(2, 0, [0,1,3,4]), 'Table 6')
S = SheetReader(Format(3, 0, [0,1,2,4,5]), 'Table 7')


table : Table = loadWorkSheet(bookname, S)

J = jsonify(table)
print(json.dumps(J))