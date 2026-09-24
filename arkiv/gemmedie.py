# -*- coding: utf-8 -*-
"""Henter et AO-billede (med genforsøg) og lægger det i webtrees' mediemappe.

    python gemmedie.py <billed-id> <filnavn.jpg>
"""
import os
import sys
from hent import hent

MAPPE = os.path.join(os.environ.get("WEBTREES_MEDIA", "//NAS/docker/webtrees/data/media"), "kirkeboger")

im = hent(int(sys.argv[1]))
sti = MAPPE + "\\" + sys.argv[2]
im.save(sti, "JPEG", quality=88)
print("gemt:", sti, im.size)
