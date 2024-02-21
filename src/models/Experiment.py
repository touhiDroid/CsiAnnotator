import json

from src.models.Activity import Activity


class Experiment(object):
    def __init__(self, _id, name, activities, transition_secs=10, reps_per_activity=20, ):
        super().__init__()
        self.id = _id
        self.name = name
        self.activities = activities
        self.transition_secs = transition_secs
        self.reps_per_activity = reps_per_activity

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'activities': Activity.to_json_array(self.activities),
            'transition_secs': self.transition_secs,
            'reps_per_activity': self.reps_per_activity,
        })

    def __str__(self):
        return self.name

    @staticmethod
    def from_json(json_str):
        j = json.loads(json_str)
        _id = j['id']
        name = j['name']
        activities = Activity.list_from_json(j['activities'])
        tr = j['transition_secs']
        reps = j['reps_per_activity']
        return Experiment(_id, name, activities, tr, reps)

    @staticmethod
    def list_from_json(json_arr):
        # j_list = json.loads(json_arr_str)
        experiments = []
        for j in json_arr:
            _id = j['id']
            name = j['name']
            activities = Activity.list_from_json(j['activities'])
            tr = j['transition_secs']
            reps = j['reps_per_activity']
            experiments.append(Experiment(_id, name, activities, tr, reps))
        return experiments

    @staticmethod
    def to_json_array(experiments):
        j_arr = []
        for e in experiments:
            j_arr.append(e.to_json())
        return json.dumps(j_arr)

    @staticmethod
    def to_name_list(experiments):
        names = []
        for e in experiments:
            names.append(e.name)
        return names
