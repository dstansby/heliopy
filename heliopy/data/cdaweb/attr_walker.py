from sunpy.net.attr import AttrWalker, AttrAnd, AttrOr
import heliopy.data.cdaweb.attrs as a

walker = AttrWalker()


@walker.add_creator(AttrOr)
def create_or(wlk, tree):
    params = []
    for sub in tree.attrs:
        sub_params = wlk.create(sub)
        # Strip out one layer of nesting of lists
        # This means that create always returns a list of dicts.
        if isinstance(sub_params, list) and len(sub_params) == 1:
            sub_params = sub_params[0]

        params.append(sub_params)

    return params


@walker.add_creator(AttrAnd, a.Dataset)
def create_and(wlk, tree):
    params = dict()
    # Use the apply dispatcher to convert the attrs to their query parameters
    wlk.apply(tree, params)
    return [params]


@walker.add_applier(AttrAnd)
def iterate_over_and(wlk, tree, params):
    for sub in tree.attrs:
        wlk.apply(sub, params)

# Converters from Attrs to ValueAttrs
# SunPy Attrs
@walker.add_applier(a.Time)
def _(wlk, attr, params):
    return params.update({'startTime': attr.start,
                          'endTime': attr.end})


@walker.add_applier(a.Dataset)
def _(wlk, attr, params):
    return params.update({'dataset': attr.value})
