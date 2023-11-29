from classes.video_manager_class import VideoManager
from classes.class_zones import CircleZone, DividingLine

directory = 'videos'
processed = []

manager = VideoManager(processed, directory, db='database/stat_database.db', show=True)

circle_zone = CircleZone((0.6, 0.9), 0.15)
line_zone = DividingLine((0.6, 0), (0.5, 1), False)


def main():
    while True:
        manager.check_new()
        manager.do_work(circle_zone)


if __name__ == '__main__':
    main()
