
import abc

import pandas as pd

from PyDSS.exceptions import InvalidParameter


class _ValueStorageBase(abc.ABC):

    DELIMITER = "__"

    @staticmethod
    def get_columns(df, name, prop, label=None):
        """Return the column names in the dataframe that match name and prop.

        Parameters
        ----------
        df : pd.DataFrame
        name : str
        prop : str
        label : int | str
            Return data corresponding to this label.
            May not be applicable for all subtypes.

        Returns
        -------
        list

        """
        columns = []
        for column in df.columns:
            fields = column.split(_ValueStorageBase.DELIMITER)
            assert len(fields) >= 2, column
            _name = fields[0]
            _prop = fields[1]
            if _name != name or _prop != prop:
                continue
            if label is None:
                columns.append(column)
            else:
                assert len(fields) == 3, column
                _label = fields[2]
                if _label == label:
                    columns.append(column)

        if not columns:
            raise InvalidParameter(f"{name} does not exist in DataFrame")

        return columns


    @abc.abstractmethod
    def to_dataframe(self):
        """Convert the stored data to a DataFrame.

        Returns
        -------
        pd.DataFrame

        """


class ValueByString(_ValueStorageBase):
    """Stores a list of numbers for an element/property."""
    def __init__(self, name, prop, value):
        self._data = [value]
        self._name = name
        self._prop = prop

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)

    def append(self, other):
        """Append values from another instance of ValueByNumber"""
        self._data += other

    @property
    @staticmethod
    def num_columns():
        return 1

    @staticmethod
    def _make_column(name, prop):
        return _ValueStorageBase.DELIMITER.join((name, prop))

    def to_dataframe(self):
        return pd.DataFrame(self._data, columns=[self._make_column(self._name, self._prop)])

class ValueByNumber(_ValueStorageBase):
    """Stores a list of numbers for an element/property."""
    def __init__(self, name, prop, value):
        self._data = [value]
        self._name = name
        self._prop = prop

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)

    def append(self, other):
        """Append values from another instance of ValueByNumber"""
        self._data += other

    @property
    @staticmethod
    def num_columns():
        return 1

    @staticmethod
    def _make_column(name, prop):
        return _ValueStorageBase.DELIMITER.join((name, prop))

    def to_dataframe(self):
        return pd.DataFrame(self._data, columns=[self._make_column(self._name, self._prop)])


class ValueByLabel(_ValueStorageBase):
    """Stores a list of lists of numbers by an arbitrary label."""
    def __init__(self, name, prop, value, Nodes, is_complex, units):
        """Constructor for ValueByLabel

        Parameters
        ----------
        name : str
        prop : str
        label_prefix : str
            Text to use as a prefix for column labels. Ex: Phase
        labels : list
            list of str
        values : list
            Pairs of values that can be interpreted as complex numbers.

        """
        phs = {
            1: 'A',
            2: 'B',
            3: 'C',
            0: 'N',
        }

        self._name = name
        self._prop = prop
        self._labels = []
        self._data = {}

        n = 2
        m = int(len(value) / (len(Nodes)*n))
        value = [value[i * n:(i + 1) * n] for i in range((len(value) + n - 1) // n)]
        value = [value[i * m:(i + 1) * m] for i in range((len(value) + m - 1) // m)]

        for i, node_val in enumerate(zip(Nodes, value)):
            node, val = node_val
            for v , x in zip(node, val):
                label = '_{}{}'.format(phs[v], str(i+1))
                if is_complex:
                    label += " " + units[0]
                    self._labels.append(label)
                    self._data[label] = [complex(x[0], x[1])]
                else:
                    label_mag = label + ' ' + units[0]
                    label_ang = label + ' ' + units[1]
                    self._labels.extend([label_mag ,label_ang])
                    self._data[label_mag] = [x[0]]
                    self._data[label_ang] = [x[1]]

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)

    def append(self, other):
        """Append values from another instance of ValueByLabel"""
        for key in other:
            assert key in self._data
            for val in other.get(key):
                self._data[key].append(val)

    def get(self, key):
        """Return the list of data for key.

        Parameters
        ----------
        key : str

        Returns
        -------
        list

        """
        return self._data[key]

    @property
    def num_columns(self):
        return len(self._data)

    def _make_columns(self):
        return [
            self.DELIMITER.join((self._name, f"{x}")) for x in self._labels
        ]

    def to_dataframe(self):
        df = pd.DataFrame(self._data)
        df.columns = self._make_columns()
        return df

def get_value_class(class_name):
    """Return the class with the given name."""
    if class_name == "ValueByNumber":
        cls = ValueByNumber
    elif class_name == "ValueByLabel":
        cls = ValueByLabel
    else:
        raise InvalidParameter(f"invalid class name={class_name}")

    return cls
