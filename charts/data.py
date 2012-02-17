from redis import Redis
from datetime import date

redis = Redis()
DATE_FMT = '%Y-%m-%d'

def _parse_date_from_str(date_str):
    return date.strptime(date_str, DATE_FMT)

def _prep_date_for_storage(dt):
    return dt.strftime(DATE_FMT)

def _start_of_period(date_in_period, accumulation_period):
    if accumulation_period in (None, 'D'):
        return date_in_period
    elif accumulation_period == 'W':
        return (date_in_period - timedelta(date_in_period.weekday()))
    elif accumulation_period == 'M':
        tt = date_in_period.timetuple()
        return date(tt[0], tt[1], 1) 
    raise ValueError('%s is not a recognized accumulation period' %
                     accumulation_period)

class ChartData(object):
    def __init__(self, chart):
        self.key = 'CD:%d' % chart.id

    def update(number, when):
        with redis.pipeline() as pipe:
            while True:
                pipe.watch(self.key)

                #get most recent datapoint
                recent = redis.lindex(self.key, -1)

                # if it's before when, fill to when then update

                # if it's after when, check whether we will need to pre-fill by
                # getting first member of the list.

    def recent():
        pass

    def range(*args, **kwargs):
        pass

    @property
    def current(self):
        pass




    def increment(self, by=1):
        shard = metrics_redis.get_server(self.key)

    def _do_increment(self, pipe):
        today = _days_since_epoch()
        last_day_incremented = int(pipe.get(self.last_day_incremented_key) or today)
        days_since_last = today - last_day_incremented

        if days_since_last == 0:
            current_count = pipe.lindex(self.key, 0)
            pipe.multi()
            if current_count is not None:
                current_count = int(current_count)
                pipe.lset(self.key, 0, current_count + 1)
            else:
                pipe.lpush(self.key, 1)
        else:
            pipe.multi()
            for _ in range(days_since_last - 1):
                # push zero for any days between last_day and today
                pipe.lpush(self.key, 0)
                pipe.ltrim(self.key, 0, self.MAX_SIZE - 1)
            pipe.lpush(self.key, 1)
            pipe.ltrim(self.key, 0, self.MAX_SIZE - 1)
        pipe.set(self.last_day_incremented_key, today)
