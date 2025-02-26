import math

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

def distance(point_a, point_b):
    return math.sqrt((point_a.x() - point_b.x()) ** 2 + (point_a.y() - point_b.y()) ** 2)

def are_close(point_a, point_b):
    return int(distance(point_a, point_b) * 1000) < 100

def are_closeish(point_a, point_b):
    return int(distance(point_a, point_b) * 1000) < 400

def are_close_but_far(point_a, point_b):
    return int(distance(point_a, point_b) * 1000) < 1000

def are_close_but_really_far(point_a, point_b):
    return int(distance(point_a, point_b) * 1000) < 2000

def hands_on_head(pose):
    return are_close(pose.left_wrist, pose.left_ear) and are_close(pose.right_wrist, pose.right_ear)

def touch_your_nose(pose):
    return are_close_but_far(pose.left_wrist, pose.nose) or are_closeish(pose.right_wrist, pose.nose)

def left_leg_up(pose):
    dx = pose.left_ankle.x() - pose.right_ankle.x()
    dy = pose.left_ankle.y() - pose.right_ankle.y()
    return dx/dy > 0.0

def right_leg_up(pose):
    dx = pose.left_ankle.x() - pose.right_ankle.x()
    dy = pose.left_ankle.y() - pose.right_ankle.y()
    return dx/dy < 0.0

def hands_on_hips(pose):
    return are_close_but_far(pose.left_wrist, pose.left_hip) and are_close(pose.right_wrist, pose.right_hip)

def squat_down(pose):
    return pose.left_hip.y() > pose.left_knee.y() and pose.right_hip.y() > pose.right_knee.y()