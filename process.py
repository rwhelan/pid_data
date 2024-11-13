import sys
import json

from typing import List

modules = {
    "11": "ECU-0x11",
    "40": "BCM-0x40",
}

def mod_name_from_can_frame(can_frame: str) -> str:
    return modules.get(can_frame[9:11], "UNK")

raw_scan = json.loads(open(sys.argv[1], "r").read())

class UDSMsg:
    def __init__(self, data):
        self.data = data

    @property
    def response_sid(self):
        return self.data[0:2]


def process_raw_response(msg: str) -> List[str]:
    msg = msg.lstrip("b'").rstrip("\\r\\r>'")

    return [i.strip() for i in msg.split("\\r")]


def assemble_can_msg(msg: List[str]) -> str:
    frames = sorted([i[12:] for i in msg], key=lambda x: x[:2])

    # Single Frame (SF)
    if frames[0][0] == "0":
        msg_len = int(frames[0][1], 16)

        if msg_len == 0:
            raise Exception("Unsupported Msg Format: " + frames[0])
        
        return frames[0][3:(msg_len*3)+2]

    # First Frame (FF)
    elif frames[0][0] == "1":
        msg_len = int(frames[0][1] + frames[0][3:5], 16)

        first_frame_body = frames[0][6:]
        body = first_frame_body + " " + " ".join([i[3:] for i in frames[1:]])
        return body[:(msg_len*3)-1]

    print(msg)
    raise Exception("Unsupported Msg Format")


# def uds_message(msg: str) -> 
pre_processed = {}
for pid in sorted(raw_scan.keys()):
    processed_value = process_raw_response(raw_scan[pid])
    if processed_value[0] != "NO DATA":
        pre_processed[pid] = processed_value

open("pre_processed.json", "w").write(json.dumps(pre_processed, indent=4))

processed = {}
for pid in sorted(pre_processed.keys()):
    processed[pid] = {}
    for can_frame in pre_processed[pid]:

        mod_name = mod_name_from_can_frame(can_frame)
        if mod_name not in processed[pid]:
            processed[pid][mod_name] = []

        processed[pid][mod_name].append(can_frame)

    for mod in processed[pid]:
        print(pid)
        processed[pid][mod] = assemble_can_msg(processed[pid][mod])

open("processed.json", "w").write(json.dumps(processed, indent=4))




