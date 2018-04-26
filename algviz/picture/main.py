from algviz.parser.json_objects import Tokens
from .recursive import main as recursive_main
from .fabulous import main as fabulous_main

class InvalidUserConfigError(Exception):
    pass

module_options = {
    "fabulous": fabulous_main,
    "fab": fabulous_main,
    "recursive": recursive_main,
    "rec": recursive_main,
}

class _keys:
    uid = Tokens.UID
    var = Tokens.VARNAME
    module = "module"
    snapshot = "snapshot"

reserved_config_keys = frozenset(key for key in dir(_keys) if not key.startswith("_"))

def make_svg(snapshots, user_config):
    obj = _get_object_to_draw(snapshots, user_config)
    module = _choose_module(snapshots, user_config)
    for key in reserved_config_keys:
        user_config.pop(key, None)
    return module.make_svg(obj, snapshots, user_config)

def _get_object_to_draw(snapshots, user_config):
    # TODO - snapshots should really be an OrderedDict, and users should be
    # able to name their snapshots
    if _keys.snapshot not in user_config and len(snapshots) != 1:
        raise InvalidUserCOnfigError("Specify {} to choose a snapshot ({} available)"
                                     .format(_keys.snapshot, len(snapshots)))
    snap_key = int(user_config.get(_keys.snapshot, 0))
    try:
        snapshot = snapshots[snap_key]
    except (KeyError, IndexError):
        raise InvalidUserConfigError("{}={} - no such snapshot".format(
            _keys.snapshot, snapshot))
    return _choose_object_from_snapshot(snapshot, user_config)

    obj = user_config.get(_keys.var, user_config.get(_keys.uid))
    if obj is None:
        raise InvalidUserConfigError("Specify {} or {} so we know what to draw!"
                                     .format(_keys.uid, _keys.var))
    
def _choose_object_from_snapshot(snapshot, user_config):
    uid = user_config.get(_keys.uid)
    if uid is not None:
        return snapshot.obj_table.getuid(uid)
    var = user_config.get(_keys.var)
    if var is not None:
        return snapshot.names[var]
    raise InvalidUserConfigError(
        "Specify one of {} or {}".format(_keys.uid, _keys.var))

def _choose_module(snapshots, user_config):
    if _keys.module not in user_config:
        return recursive_main  # default only because it can handle arrays without crashing
    if user_config[_keys.module] not in module_options:
        _bad_for_key(_keys.module, user_config[_keys.module], module_options.keys())
    return module_options[user_config[_keys.module]]
    

def _bad_for_key(key, val, suggestions):
    msg = "{} is an invalid setting for key {}".format(val, key)
    if suggestions:
        msg += "\nSuggested values:  {}".format(
            "|".join(str(s) for s in suggestions))
    raise InvalidUserConfigError(msg)
