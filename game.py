import logging
import sys
import wave
from pathlib import Path
from typing import Any, Dict
import subprocess
import random
import os
from multiprocessing import Process

from piper import PiperVoice
from piper.download import ensure_voice_exists, find_voice, get_voices

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import hailo

from hailo_apps_infra.hailo_rpi_common import (
    app_callback_class,
)
from hailo_apps_infra.pose_estimation_pipeline import GStreamerPoseEstimationApp
from commands import simon_says
from pose import Pose, right_leg_up

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
            # ensure_voice_exists(model, data_dir, download_dir, voices_info)
            model, config = find_voice(model, data_dir)

        self.voice = PiperVoice.load(model, config_path=config, use_cuda=False)
        self.last_simon_says_command_idx = None
        self.did_simon_say = False
        self.say_process = None


def say_text(voice, players_out_text, command_idx, did_simon_say):
    if os.path.exists(output_file):
        os.remove(output_file)

    item = simon_says[command_idx]
    text = ("Simon says, {}" if did_simon_say else "Hmm...{}").format(item["cmd"])

    if players_out_text:
        text = players_out_text + ". " + text
    with wave.open(output_file, "wb") as wav_file:
        voice.synthesize(text, wav_file, **synthesize_args)
    if os.path.exists(output_file):
        subprocess.check_call(["aplay", "-q", output_file])


def app_callback(pad, info, user_data):
    user_data.increment()

    if user_data.frame_count % 200 == 0:
        if user_data.say_process is not None and user_data.say_process.is_alive():
            # previous process didn't finish, wait for 3 seconds to finish
            user_data.say_process.join(3)

        player_num = 0
        players_out = []

        buffer = info.get_buffer()
        if buffer is None:
            return Gst.PadProbeReturn.OK

        roi = hailo.get_roi_from_buffer(buffer)
        detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

        for detection in detections:
            label = detection.get_label()
            if label == "person":
                player_num += 1
                landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
                if len(landmarks) > 0:
                    points = landmarks[0].get_points()
                    if len(points) == 17:
                        if user_data.last_simon_says_command_idx is not None:
                            if simon_says[user_data.last_simon_says_command_idx]["check"](Pose(points)) is False:
                                players_out.append(str(player_num))


        if len(players_out) == 0:
            players_out_text = None
        elif len(players_out) == 1:
            players_out_text = "Player number {} is out!".format(players_out[0])
        else:
            players_out_text = "Players with numbers {} are out!".format(",".join(players_out))

        command_idx = random.randint(0, len(simon_says) - 1)
        simon_say = (random.randint(1, 4) < 4) # 75% probability of "simon says"
        user_data.say_process = Process(target=say_text, args=(user_data.voice, players_out_text, command_idx, simon_say))
        if simon_say:
            user_data.last_simon_says_command_idx = command_idx
        user_data.did_simon_say = simon_say
        user_data.say_process.start()

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    main()
