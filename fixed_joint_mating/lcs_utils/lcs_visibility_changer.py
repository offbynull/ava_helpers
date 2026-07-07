import re
from enum import Enum

import FreeCAD as App

from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import log


class ChainType(Enum):
    NAME = "Name"
    LABEL = "Label"


def _parent_chains(obj, chain_type: ChainType):
    def _elem(o):
        if chain_type == ChainType.NAME:
            return o.Name
        if chain_type == ChainType.LABEL:
            return o.Label
        raise ValueError(chain_type)

    def _walk(o, path, seen):
        parents = getattr(o, "InList", [])
        if not parents:
            return [".".join(reversed(path))]
        chains = []
        for parent in parents:
            if parent.Name in seen:
                continue
            chains.extend(
                _walk(
                    parent,
                    path + [_elem(parent)],
                    seen | {parent.Name},
                )
            )
        return chains

    return _walk(obj, [_elem(obj)], {obj.Name})


def change(
        doc: App.Document,
        visibility: bool,
        label_parents_cache: dict[App.DocumentObject, list[str]],
        name_parents_cache: dict[App.DocumentObject, list[str]],
        label_path_regex: str = '.*',
        name_path_regex: str = '.*',
):
    label_path_regex = re.compile(label_path_regex)
    name_path_regex = re.compile(name_path_regex)
    for obj in doc.Objects:
        if not hasattr(obj, MATER_LCS_IDENTIFIER):
            continue
        if obj not in name_parents_cache:
            log('---')
            parents = _parent_chains(obj, ChainType.NAME)
            for p in parents:
                log(f'{obj.Name} / {obj.Label}: {p}')
            name_parents_cache[obj] = parents
        else:
            parents = name_parents_cache[obj]
        if not any(name_path_regex.search(p) for p in parents):
            continue
        if obj not in label_parents_cache:
            log('---')
            parents = _parent_chains(obj, ChainType.LABEL)
            for p in parents:
                log(f'{obj.Name} / {obj.Label}: {p}')
            label_parents_cache[obj] = parents
        else:
            parents = label_parents_cache[obj]
        if not any(label_path_regex.search(p) for p in parents):
            continue
        obj.Visibility = visibility

    doc.recompute()

    return None
