import argparse
import logging
import sys
import time
import wave
from pathlib import Path
from typing import Any, Dict
import subprocess
import time
import random
import os
from multiprocessing import Process

from piper import PiperVoice
from piper.download import ensure_voice_exists, find_voice, get_voices

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import cv2
import hailo

from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.pose_estimation_pipeline import GStreamerPoseEstimationApp
from commands import simon_says
from pose import Pose, left_hand_raised, right_hand_raised, hands_on_head

_FILE = Path(__file__)
_DIR = _FILE.parent
_LOGGER = logging.getLogger(_FILE.stem)

synthesize_args = {
    "speaker_id": None,
    "length_scale": None,
    "noise_scale": None,
    "noise_w": None,
    "sentence_silence": 0.0,
}

output_file = "/run/user/1000/simon_says.wav"


def main() -> None:
    os.environ["DISPLAY"] = ":0"
    sys.argv += ["--input", "rpi"]
    user_data = user_app_callback_class()
    app = GStreamerPoseEstimationApp(app_callback, user_data)
    app.run()


class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()

        model = "en_US-ryan-medium"

        data_dir = [str(Path.cwd())]
        download_dir = data_dir[0]
        logging.basicConfig(level=logging.ERROR)

        model_path = Path(model)
        if not model_path.exists():
            # Download voice if file doesn't exist
            voices_info = get_voices(download_dir, update_voices=False)
            aliases_info: Dict[str, Any] = {}
            for voice_info in voices_info.values():
                for voice_alias in voice_info.get("aliases", []):
                    aliases_info[voice_alias] = {"_is_alias": True, **voice_info}
            voices_info.update(aliases_info)
            ensure_voice_exists(model, data_dir, download_dir, voices_info)
            model, config = find_voice(model, data_dir)

        self.voice = PiperVoice.load(model, config_path=config, use_cuda=False)
        self.last_command_idx = None
        self.did_simon_say = False
        self.say_process = None


def say_text(voice, players_out_text, last_command_idx, did_simon_say):
    if os.path.exists(output_file):
        os.remove(output_file)

    item = simon_says[last_command_idx]
    text = ("Simon says, {}" if did_simon_say else "Hmm...{}").format(item["cmd"])

    if players_out_text:
        text = players_out_text + ". " + text
    with wave.open(output_file, "wb") as wav_file:
        voice.synthesize(text, wav_file, **synthesize_args)
    if os.path.exists(output_file):
        subprocess.check_call(["aplay", "-q", output_file])


def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    
    # for detection in detections:
    #     label = detection.get_label()
    #     bbox = detection.get_bbox()
    #     confidence = detection.get_confidence()
    #     if label == "person":
    #         landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
    #         if len(landmarks) > 0:
    #             points = landmarks[0].get_points()
    #             if len(points) == 17:
    #                 print(hands_on_head(Pose(points)))

    if user_data.frame_count % 200 == 0:
        if user_data.say_process is not None:
            # previous process didn't finish, wait for it first
            user_data.say_process.join()

        player_num = 0
        players_out = []
        for detection in detections:
            label = detection.get_label()
            bbox = detection.get_bbox()
            confidence = detection.get_confidence()
            if label == "person":
                player_num += 1
                track_id = 0
                track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
                if len(track) == 1:
                    track_id = track[0].get_id()

                landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
                if len(landmarks) > 0:
                    points = landmarks[0].get_points()
                    if len(points) == 17:
                        if user_data.last_command_idx is not None and user_data.did_simon_say is True:
                            pose = Pose(points)
                            if simon_says[user_data.last_command_idx]["check"](pose) is False:
                                players_out.append(str(player_num))


        if len(players_out) == 0:
            players_out_text = None
        elif len(players_out) == 1:
            players_out_text = "Player number {} is out!".format(players_out[0])
        else:
            players_out_text = "Players with numbers {} are out!".format(",".join(players_out))

        command_idx = random.randint(0, len(simon_says) - 1)
        simon_say = (random.randint(1, 2) == 1) # 50% probability of "simon says"
        user_data.say_process = Process(target=say_text, args=(user_data.voice, players_out_text, command_idx, simon_say))
        user_data.say_process.start()
        user_data.last_command_idx = command_idx
        user_data.did_simon_say = simon_say

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    main()
