import json


class Activity(object):
    def __init__(self, _id, name, duration_secs, img1, img2):
        super().__init__()
        self.id = _id
        self.name = name
        self.duration_secs = duration_secs
        self.img1 = img1
        self.img2 = img2

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'duration_secs': self.duration_secs,
            'img1': self.img1,
            'img2': self.img2
        })

    @staticmethod
    def from_json(json_str):
        j = json.loads(json_str)
        _id = j['id']
        name = j['name']
        dur = j['duration_secs']
        img1 = j['img1']
        img2 = j['img2']
        return Activity(_id, name, dur, img1, img2)

    @staticmethod
    def list_from_json(json_arr):
        # j_list = json.loads(json_arr_str)
        activities = []
        for j in json_arr:
            _id = j['id']
            name = j['name']
            dur = j['duration_secs']
            img1 = j['img1']
            img2 = j['img2']
            activities.append(Activity(_id, name, dur, img1, img2))
        return activities

    @staticmethod
    def to_json_array(activities):
        j_arr = []
        for a in activities:
            j_arr.append(a.to_json())
        return json.dumps(j_arr)
