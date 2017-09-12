from django.db import connection
from time import time
from operator import add
import re
from functools import reduce

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

try:
    from project.local_settings import DEBUG
except ImportError:
    from project.settings import DEBUG


class StatsMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        In your base template, put this:
        <div id="stats">
        <!-- STATS: Total: %(total_time).2fs Python: %(python_time).2fs DB: %(db_time).2fs Queries: %(db_queries)d ENDSTATS -->
        </div>
        '''

        # Uncomment the following if you want to get stats on DEBUG=True only
        if not DEBUG:
            return None


        # get number of db queries before we do anything
        n = len(connection.queries)

        # time the view
        start = time()
        response = view_func(request, *view_args, **view_kwargs)
        total_time = time() - start

        # compute the db time for the queries just run
        db_queries = len(connection.queries) - n
        if db_queries:
            db_time = reduce(add, [float(q['time'])
                                   for q in connection.queries[n:]])
        else:
            db_time = 0.0

        # and backout python time
        python_time = total_time - db_time

        stats = {
            'total_time': total_time,
            'python_time': python_time,
            'db_time': db_time,
            'db_queries': db_queries,
        }

        print(stats)

        # replace the comment if found
        # if response and response.content:
        if (hasattr(response,'is_rendered') and response.is_rendered or not hasattr(response,'is_rendered') ) and response.content:
            s = response.content.decode('utf-8')
            regexp = re.compile(r'(?P<cmt><!--\s*STATS:(?P<fmt>.*?)ENDSTATS\s*-->)')
            match = regexp.search(s)
            if match:
                s = (s[:match.start('cmt')] +
                     match.group('fmt') % stats +
                     s[match.end('cmt'):])
                response.content = s

        return response
