class Pose:
    def __init__(self, raw_data):
        self.nose = raw_data[0]
        self.right_eye = raw_data[1]
        self.left_eye = raw_data[2]
        self.right_ear = raw_data[3]
        self.left_ear = raw_data[4]
        self.right_shoulder = raw_data[5]
        self.left_shoulder = raw_data[6]
        self.right_elbow = raw_data[7]
        self.left_elbow = raw_data[8]
        self.right_wrist = raw_data[9]
        self.left_wrist = raw_data[10]
        self.right_hip = raw_data[10]
        self.left_hip = raw_data[11]
        self.right_knee = raw_data[13]
        self.left_knee = raw_data[14]
        self.right_ankle = raw_data[15]
        self.left_ankle = raw_data[16]

def left_hand_raised(pose):
    return pose.left_wrist.y() < pose.left_shoulder.y()

def right_hand_raised(pose):
    return pose.right_wrist.y() < pose.right_shoulder.y()

def hands_on_head(pose):
    return pose.right_wrist.y() < pose.right_shoulder.y() and pose.left_wrist.y() < pose.left_shoulder.y()

def touch_your_nose(pose):
    return pose.