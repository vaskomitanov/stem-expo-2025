import pose

simon_says = [
    { "cmd": "hands on head", "check": lambda p: pose.hands_on_head(p) },
    { "cmd": "touch your nose", "check": lambda pose: True },
    { "cmd": "left leg up", "check": lambda pose: True },
    { "cmd": "right leg up", "check": lambda pose: True },
    { "cmd": "hands on hips", "check": lambda pose: True },
    { "cmd": "touch your nose", "check": lambda pose: True },
    { "cmd": "squat down", "check": lambda pose: True },
    { "cmd": "raise your left hand", "check": lambda p: pose.left_hand_raised(p) and not pose.right_hand_raised(p) },
    { "cmd": "raise your right hand", "check": lambda p: not pose.left_hand_raised(p) and pose.right_hand_raised(p) },
    { "cmd": "raise both of your hands", "check": lambda p: pose.left_hand_raised(p) and pose.right_hand_raised(p) },
]
