import os
import time
from datetime import datetime
from deep_sort import nn_matching
from deep_sort import generate_detections as gdet
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
import numpy as np
from classes.Cnn_onnx import CnnOnnx
from classes.class_zones import Zone
from classes.class_db_connector import DBConnector
try:
    from cv2 import cv2
except:
    import cv2


# TODO проблема, заново начинает тот же видос смотреть

def draw_boxes(frame, bboxes, track_ids):
    for bbox, idx in zip(bboxes, track_ids):
        frame = cv2.putText(frame, f"ID: {idx}", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)
        frame = cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 200), 3)

    return frame


class EventStack:
    def __init__(self, length, placeholder=2):
        self.stack = [placeholder] * length
        self.length = length
        self.placeholder = placeholder

    def append(self, event):
        self.stack.pop(0)
        self.stack.append(event)

    def get_last(self):
        return self.stack[-1]

    def get_stack(self):
        return self.stack

    def clear(self):
        self.stack = [self.placeholder] * self.length


class TrackedPerson:
    def __init__(self, idx, start_point):
        self.idx = idx
        self.history = EventStack(20, start_point)
        self.start = start_point

    def get_last(self):
        return self.history.get_last()


class VideoManager:
    def __init__(self, processed_vids, directory, db: str, show=False):
        self.processed_vids = processed_vids
        self.directory = directory
        self.last_check = datetime.now()
        self.actual_tasks = []
        self.show = show
        self.db = DBConnector(db)
        self.cnn = CnnOnnx('classes/yolov7darknet/yolov7_dynamic.onnx',
                       640)

        max_cosine_distance = 0.6
        nn_budget = None
        self.encoder = gdet.create_box_encoder('classes/model_data/mars-small128.pb', batch_size=1)
        self.metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)

    def diff(self, li1, li2):
        li_dif = [i for i in li1 + li2 if i not in li2]
        return li_dif

    def check_new(self):
        all_files = os.listdir(self.directory)
        new = self.diff(all_files, self.processed_vids)

        self.last_check = datetime.now()
        if len(new) == 0:
            print(f"No tasks detected: {self.last_check}")
            time.sleep(5)
        self.actual_tasks = new

    def do_work(self, zone):
        for work in self.actual_tasks:
            res = self.process_video(work, zone)
            print(res)
            self.processed_vids.append(work)
            self.db.insert_job(res)

    def track_to_rel(self, track, frame):
        h, w = frame.shape[:2]
        start, end = track
        sx, sy = start
        ex, ey = end
        sx /= w
        sy /= h

        ex /= w
        ey /= h

        return (sx, sy), (ex, ey)

    def process_video(self, video_path, zone: Zone):

        max_age = 15

        cap = cv2.VideoCapture(os.path.join(self.directory, video_path))
        tracker = Tracker(self.metric, max_age=max_age, n_init=2)
        counter = 0
        ret, frame = cap.read()
        current_tracks = {}
        height, width = frame.shape[:2]
        video = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1, (width, height))

        points = []

        while True:
            counter += 1
            ret, frame = cap.read()

            # frame = cv2.copyMakeBorder(frame, 0, 200,0,0, cv2.BORDER_CONSTANT)

            if not ret:
                break
            if counter % 2 != 0:
                continue

            boxes, scores, classids = self.cnn.detect_image(frame)
            if boxes is None:
                boxes = []
                scores = []
                classids = []

            boxes = np.array(boxes)
            names = np.array(classids)
            scores = np.array(scores)
            features = np.array(self.encoder(frame, boxes))
            detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in
                          zip(boxes, scores, names, features)]

            tracker.predict()
            tracker.update(detections)

            tracked_bboxes = []
            tracked_ids = []
            for track in tracker.tracks:

                if not track.is_deleted():
                    if track.track_id not in current_tracks.keys():
                        current_tracks[track.track_id] = TrackedPerson(track.track_id,
                                                                       (int(track.mean[0]), int(track.mean[1])))
                    else:
                        current_tracks[track.track_id].history.append((int(track.mean[0]), int(track.mean[1])))
                if track.time_since_update > max_age-1:
                    # print(f'Track ended: {track.track_id}')
                    # print(current_tracks[track.track_id].start, current_tracks[track.track_id].get_last())
                    track_points = (current_tracks[track.track_id].start, current_tracks[track.track_id].get_last())
                    rel_track = self.track_to_rel(track_points, frame)
                    points.append(track_points)
                    # print(rel_track)
                    print(zone.process_single(rel_track))
                    del current_tracks[track.track_id]

                if not track.is_confirmed() or track.time_since_update > 5:
                    continue
                bbox = track.to_tlbr()  # Get the corrected/predicted bounding box
                class_name = track.get_class()  # Get the class name of particular object
                tracking_id = track.track_id  # Get the ID for the particular track
                tracked_ids.append(tracking_id)
                tracked_bboxes.append(bbox.tolist())

            bboxes = np.array(tracked_bboxes, dtype=int)
            # print(bboxes)
            image = draw_boxes(frame, bboxes, tracked_ids)

            for start, end in points:
                image = cv2.circle(image, start, 6, (0, 255, 0), -1)
                image = cv2.circle(image, end, 6, (0, 0, 255), -1)
                image = cv2.line(image, start,end, (255, 0, 0), 2)

            image = zone.draw(image)
            if self.show:
                cv2.imshow('output', image)
                video.write(image)
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break

        if self.show:
            cv2.destroyAllWindows()
            video.release()
        return zone.process_coords(points)
