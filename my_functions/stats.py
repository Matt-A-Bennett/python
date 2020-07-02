#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def make_dm(conds, block_len=12, base_len=12):
    """Doc String."""

    import numpy as np

    dm = np.zeros([(base_len + block_len)*len(conds), len(set(conds))])
    i = 0
    for cond_ind, cond in enumerate(conds):
        i += block_len
        dm[i:i+block_len, cond_ind] += 1
        i += base_len
    return dm

