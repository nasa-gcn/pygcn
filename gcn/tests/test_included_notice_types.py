from .. import notice_types


def test_included_notice_types():
    import requests
    import re

    for notice_id, notice_name in re.findall(
            r"^<tr.*?><th>(.*?)</th><th>(.*?)</th><th>.*?ACTIVE</th>",
            requests.get("https://gcn.gsfc.nasa.gov/filtering.html").text,
            re.M,
            ):

        if notice_name in ("VOE_1.1_IM_ALIVE", "VOE_2.0_IM_ALIVE"):
            continue

        if notice_name in ("LVC_PRELIM", "LVC_CNTRPART"):
            print("why are these shorter versions, and do we care?")
            continue

        assert int(notice_id) == getattr(notice_types, notice_name)
