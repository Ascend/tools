import csv
import enum
from collections import defaultdict

from ada.reporter_registry import reporter
from ada.definitions import *
from ada.builtin_reporters.summary_reporter import SummaryReporter

EXECUTE_EVENT = "[Execute]"


class OpExecutionType(enum.Enum):
    OTHERS = 1,
    AICORE_SINGLE_OP = 2
    AICORE_ATOMIC_CLEAN = 3
    AICPU_SINGLE_OP = 4
    AICPU_TYPE_3 = 5
    AICORE_TYPE_3 = 6
    SUBGRAPH = 7


class OpExecution:
    def __init__(self):
        self.event_records: [EventRecord] = []
        self.op_type = ""
        self.execution_type = OpExecutionType.OTHERS


def infer_execution_type(execution: OpExecution):
    aicore, aicpu, atomic_aicore, type3, launch = range(5)
    keys_to_kernel_types = {aicore: {"[LaunchKernelWithFlag]", "[LaunchKernelWithHandle]"},
                            atomic_aicore: {"[AtomicLaunchKernelWithFlag]", },
                            aicpu: {"[AicpuLaunchCCKernel]", },
                            type3: {"[SyncStream]", },
                            launch: set()}
    keys_to_kernel_types[launch].update(keys_to_kernel_types[aicore])
    keys_to_kernel_types[launch].update(keys_to_kernel_types[aicpu])
    keys_to_kernel_types[launch].update(keys_to_kernel_types[atomic_aicore])

    key_types_num = defaultdict(int)
    for rec in execution.event_records:
        for launch_type, kernel_types in keys_to_kernel_types.items():
            if rec.event in kernel_types:
                key_types_num[launch_type] += 1

    # 优先确认是否是单算子子图
    if key_types_num[launch] > 2:
        return OpExecutionType.SUBGRAPH
    if key_types_num[launch] == 2:
        if atomic_aicore in key_types_num:
            return OpExecutionType.AICORE_ATOMIC_CLEAN
        else:
            return OpExecutionType.SUBGRAPH

    # AICORE
    if aicore in key_types_num:
        if type3 in key_types_num:
            return OpExecutionType.AICORE_TYPE_3
        return OpExecutionType.AICORE_SINGLE_OP

    # AICPU
    if aicpu in key_types_num:
        if type3 in key_types_num:
            return OpExecutionType.AICPU_TYPE_3
        return OpExecutionType.AICPU_SINGLE_OP

    # UNKNOWN
    return OpExecutionType.OTHERS


@reporter("single_op_summary", category="single-op")
class SingleOpSummaryReporter:
    def __init__(self, pds: [ProfilingData]):
        self._pds = pds[:]

    @staticmethod
    def parse_to_op_executions(pd: ProfilingData):
        execution_types_to_executions = defaultdict(list)
        one_execution = None
        end_time = 0
        for event_record in pd.event_records:
            if event_record.event == EXECUTE_EVENT:
                if one_execution is not None:
                    one_execution.execution_type = infer_execution_type(one_execution)
                    execution_types_to_executions[one_execution.execution_type].append(one_execution)
                end_time = event_record.end
                one_execution = OpExecution()
            if event_record.end > end_time:
                print(f"WARNING: Drop event record {event_record.node_name}-{event_record.event} cause invalid end time"
                      f" {event_record.end}, expect end time must early than {end_time}")
                continue
            one_execution.event_records.append(event_record)

        if one_execution is not None:
            one_execution.execution_type = infer_execution_type(one_execution)
            execution_types_to_executions[one_execution.execution_type].append(one_execution)

        return execution_types_to_executions

    @staticmethod
    def report_single_op_summary(types_to_executions, path, index):
        total_count = 0
        total_time = 0.0

        csv_content = []
        for exe_type, executions in types_to_executions.items():
            time = 0.0
            for execution in executions:
                if len(execution.event_records) == 0:
                    raise AdaError("InnerError, no events in execution when single op summary")
                if execution.event_records[0].event != EXECUTE_EVENT:
                    raise AdaError("InnerError, invalid first event when single op summary")
                time += ((execution.event_records[0].end - execution.event_records[0].start) / 1000)

            count = len(executions)
            total_count += count
            total_time += time
            csv_content.append({
                "execution_type": exe_type.name.lower(),
                "count": count,
                "arg(us)": time / count,
                "total(us)": time,
            })

        if total_count == 0:
            print("WARNING: No records run in single op found, do not generate the single op summary file")
            return

        for row in csv_content:
            row['count-percent'] = float(row['count']) / float(total_count)
            row['time-percent'] = row['total(us)'] / total_time

        csv_content.append({
            "execution_type": "all",
            "count": total_count,
            "count-percent": 1.0,
            "arg(us)": total_time / total_count,
            "total(us)": total_time,
            "time-percent": 1.0
        })

        dump_path = f"{path}_single_op_summary_{index}.csv"
        print("Dump to single op summary file {}".format(dump_path))
        with open(dump_path, "w", newline='') as f:
            cf = csv.DictWriter(f, fieldnames=["execution_type", "count", "count-percent", "arg(us)", "total(us)",
                                               "time-percent"])
            cf.writeheader()
            cf.writerows(csv_content)

    def report(self, path):
        types_to_pds = defaultdict(list)
        for i, pd in enumerate(self._pds):
            types_to_executions = SingleOpSummaryReporter.parse_to_op_executions(pd)
            SingleOpSummaryReporter.report_single_op_summary(types_to_executions, path, i)

            for exe_type, executions in types_to_executions.items():
                type_pd = ProfilingData()
                type_pd.version = pd.version
                for execution in executions:
                    type_pd.event_records += execution.event_records
                types_to_pds[exe_type].append(type_pd)

        for exe_type, pds in types_to_pds.items():
            type_path = f"{path}_{exe_type.name.lower()}"
            SummaryReporter(pds).report(type_path)
