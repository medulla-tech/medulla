from mmc.plugins.pulse2.location import ComputerLocationManager
import logging

def unique(s):
    """
    Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

def same_network(ip1, ip2, netmask):
    try:
        ip1 = map(lambda x:int(x), ip1.split('.'))
        ip2 = map(lambda x:int(x), ip2.split('.'))
        netmask = map(lambda x:int(x), netmask.split('.'))
        for i in [0,1,2,3]:
            if ip1[i].__and__(netmask[i]) != ip2[i].__and__(netmask[i]):
                return False
    except ValueError:
        return False
    return True

def complete_ctx(ctx):
    """
    Set GLPI user locations and profile in current security context.
    """
    from mmc.plugins.glpi.database import Glpi
    if not hasattr(ctx, "locations") or ctx.locations == None:
        logging.getLogger().debug("adding locations in context for user %s" % (ctx.userid))
        ctx.locations = ComputerLocationManager().getUserLocations(ctx.userid)
        ctx.locationsid = map(lambda e: e.ID, Glpi().getUserLocations(ctx.userid))
    if not hasattr(ctx, "profile"):
        logging.getLogger().debug("adding profiles in context for user %s" % (ctx.userid))
        ctx.profile = ComputerLocationManager().getUserProfile(ctx.userid)
    
def onlyAddNew(obj, value):
    if type(value) == list:
        for i in value:
            try:
                obj.index(i)
            except:
                obj.append(i)
    else:
        try:
            obj.index(value)
        except:
            obj.append(value)
    return obj

