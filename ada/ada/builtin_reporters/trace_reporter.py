from ada.definitions import *
from ada.reporter_registry import reporter
import json


@reporter("trace")
class TracingReporter:
    def __init__(self, pds: [ProfilingData]):
        self._pds = pds

    def report(self, file_path):
        for i, pd in enumerate(self._pds):
            total_count = len(pd.event_records)
            ns_count = 0
            j_file = {"traceEvents": []}
            j_file_record = j_file["traceEvents"]
            for rec in pd.event_records:
                dur = (rec.end - rec.start) / 1000

                if dur < 1:
                    ns_count += 1

                j_rec = {
                    "name": get_name(rec),
                    "ph": "X",
                    "pid": rec.device,
                    "tid": rec.tid,
                    "ts": rec.start / 1000,
                    "dur": dur
                }
                j_file_record.append(j_rec)

            if ns_count * 10 >= total_count:
                j_file["displayTimeUnit"] = "ns"

            dump_path = "{}_tracing_{}{}".format(file_path, i, ".json")
            print("Dump to tracing file {}".format(dump_path))
            with open(dump_path, "w") as f:
                json.dump(j_file, f)
