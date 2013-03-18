# Caprice

Generating random items in django can be very expensive. You can try the approaches mentioned in [this StackOverflow thread](http://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm) , but with any reasonably large database both this approaches would be too slow.

Hence introducing Caprice. It is a django model manager which provides for a random method that gets the random items from the redis cache and does the database query only when the redis cached is empty.


## When to use it?


The typical  use case for this app is if you want to keep generating random model instances one by one and perform an action on them.


## Usage

Define a REDIS_URL in your settings.py which points to your redis server

In the model which you want to query randomly define the manager as CachedRandomManager

    from caprice import CachedRandomManager

    class YourModel(models.Model):
        name = models.CharField(max_length=256)

        objects = CachedRandomManager()

In your code you can just call:
   YourModel.objects.random()  

While the first query will be expensive , all subsequent queries will be much faster

You can use random just like filter and pass the same parameters. Each query havinf different parametrs will have different caches.

For example
  YourModel.objects.random() and YourModel.objects.random(name__icontains = 'a') will have different caches which you can use separately.

## Caution
  If you want to perform any sort of filtering you must do it within random call. 

##TODO
  1. Add tests
  2. Add a backend based architecture where the cache need not strictly be Redis.

