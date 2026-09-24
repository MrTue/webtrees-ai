# -*- coding: utf-8 -*-
"""Henter AO-billeder med genforsøg. Bruges af de andre scripts via import."""
import io, time, urllib.request
from PIL import Image

def hent(billed_id, forsoeg=5):
    sidste = None
    for i in range(forsoeg):
        try:
            req = urllib.request.Request(
                "https://api.rigsarkivet.dk/ao/v1/images/%d" % billed_id,
                headers={"User-Agent": "slaegtsforskning/1.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
            return Image.open(io.BytesIO(data)).convert("RGB")
        except Exception as e:                                   # noqa: BLE001
            sidste = e
            time.sleep(2 + 3 * i)
    raise sidste
