import hashlib
import time
import json

from django.conf import settings
from django.db.models.query import QuerySet
from django.db import models

import redis
redis_conn = redis.from_url(settings.REDIS_URL)

import logging
_log = logging.getLogger(__name__)

def get_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()



class CachedRandomManager(models.Manager):

    def __init__(self,key_prefix,*args, **kwargs):
        self.key_prefix = key_prefix
        super(CachedRandomManager, self).__init__(*args, **kwargs)

    def _populate_models_cache(self,key,query,cache_length=None):
            """
            Attempts to creates categorize_requests cache
            returns number of requests in cache or None
            - try acquiring lock
            - if not acquired:
            -   is lock is expired
            -   delete lock and acquire
            - if acquired:
            -   if it really needed to populate:
            -       populate
            -   else:
            -       release lock
            """

            ttl = 30 # seconds
            _log.info('populating [%s] for pending requests' % key)
            now = time.time()
            lock_key = 'lock.' + key
            _log.info('acquiring lock')
            acquired = redis_conn.setnx(lock_key, now)
            if not acquired:
                _log.info('found existing lock')
                then = float(redis_conn.get(lock_key))
                lock_expired = (now - then) > ttl
                if lock_expired:
                    _log.info('removing existing expired lock')
                    redis_conn.delete(lock_key)
                    acquired = redis_conn.setnx(lock_key, now)
            if acquired:
                _log.info('acquired lock')
                set_len = redis_conn.scard(key)
                if set_len is 0: # Making sure we popoulate only when necessary
                    random_ids = query.order_by('?').values_list('id',flat = True)
                    redis_conn.delete(key)
            set_len = redis_conn.sadd(key, *random_ids)
            _log.info('completed populating [%s] with %s pending requests' % (key, set_len))
            redis_conn.delete(lock_key)
            _log.info('released lock')
            return set_len



    def random(self,*args,**kwargs):
            #create a key based on the query parametes
            key = self.key_prefix + ':' +  get_hash(args) + ':' + get_hash(kwargs)
            random_id = redis_conn.spop(key)
            query = self.filter(*args,**kwargs)
            if not random_id:
                 self._populate_models_cache(key,query)
                 random_id = redis_conn.spop(key)
                 return self.get(id=random_id)if random_id else None
            else:
                 return self.get(id=random_id)


