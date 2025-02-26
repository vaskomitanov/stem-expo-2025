import pose

simon_says = [
    { "cmd": "hands on head", "check": lambda p: pose.hands_on_head(p) },
    { "cmd": "touch your nose", "check": lambda p: pose.touch_your_nose(p) },
    { "cmd": "left leg up", "check": lambda p: pose.left_leg_up(p) },
    { "cmd": "right leg up", "check": lambda p: pose.right_leg_up(p) },
    { "cmd": "hands on hips", "check": lambda p: pose.hands_on_hips(p) },
    { "cmd": "touch your nose", "check": lambda p: pose.touch_your_nose(p) },
    { "cmd": "squat down", "check": lambda p: pose.squat_down(p) },
    { "cmd": "raise your left hand", "check": lambda p: pose.left_hand_raised(p) and not pose.right_hand_raised(p) },
    { "cmd": "raise your right hand", "check": lambda p: not pose.left_hand_raised(p) and pose.right_hand_raised(p) },
    { "cmd": "raise both of your hands", "check": lambda p: pose.left_hand_raised(p) and pose.right_hand_raised(p) },
]
