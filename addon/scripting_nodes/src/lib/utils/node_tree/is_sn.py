def is_sn(ntree):
    return getattr(ntree, "is_sn_ntree", False)
