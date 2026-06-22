import re
import traceback

import FreeCAD as App
from logger import log, warn

MATE_RE = re.compile(r'(?:^|\s)mater\d*(?:\s|$)', re.I)
ROT_180_Y = App.Rotation(App.Vector(0, 1, 0), 180)

def is_fixed_joint(o: 'App.FeaturePython'):
    return (
        hasattr(o, 'JointType')
        and str(o.JointType).lower() == 'fixed'
        and hasattr(o, 'Reference1')
        and hasattr(o, 'Reference2')
        and hasattr(o, 'Placement1')
        and hasattr(o, 'Placement2')
    )

def linked_target(o: App.DocumentObject) -> App.GeoFeature:
    return getattr(o, 'LinkedObject')

def child_by_name(parent: App.DocumentObject, name: str):
    for c in getattr(parent, 'OutList', []):
        if c.Name == name:
            return c
    return None

def resolve_joint_lcs(ref: tuple[App.DocumentObject, list[str]]) -> App.GeoFeature:
    # Expected: (<App::Link>, ['LCS.', 'LCS.'])
    base, subs = ref[0], ref[1]
    obj = linked_target(base)
    # use first referenced subpath
    sub = subs[0]
    path = str(sub).strip('.').split('.')
    for name in path:
        obj = child_by_name(obj, name)
    return obj

def is_mate_connector_lcs(o: App.GeoFeature):
    return (
        getattr(o, 'TypeId').endswith('::LocalCoordinateSystem')
        and MATE_RE.search(getattr(o, 'Label', ''))
    )

def clock(docs: list[App.DocumentObject]):
    changed = 0
    skipped = 0

    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            j.Offset1 = App.Placement()
            j.Offset2 = App.Placement()
            j.Placement1 = App.Placement()
            j.Placement2 = App.Placement(App.Vector(), ROT_180_Y)
            j.touch()

            print('CLOCKED')
            changed += 1
        except Exception as e:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')


def set_visibility(docs: list[App.DocumentObject], hidden: bool):
    changed = 0
    skipped = 0

    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            lcs1.ViewObject.Visibility = not hidden
            lcs2.ViewObject.Visibility = not hidden

            log('HIDDEN' if hidden else 'VISIBLE')
            changed += 1
        except Exception as e:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')


def toggle_visibility(docs: list[App.DocumentObject]):
    changed = 0
    skipped = 0

    seen = set()
    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            if lcs1 not in seen:
                lcs1.ViewObject.Visibility = not lcs1.ViewObject.Visibility
                seen.add(lcs1)
                log('Ref 1 VISIBILITY TOGGLED')
            if lcs2 not in seen:
                lcs2.ViewObject.Visibility = not lcs2.ViewObject.Visibility
                seen.add(lcs2)
                log('Ref 2 VISIBILITY TOGGLED')
            changed += 1
        except Exception as e:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')