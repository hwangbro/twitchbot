# Module for counter database

from peewee import *


db = SqliteDatabase('../db/counter.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,
    'foreign_keys': 1,
    'ignore_check_counstraints': 0,
    'synchronous': 0
    })

class BaseModel(Model):
    class Meta:
        database = db

class Counter(BaseModel):
    name = CharField(unique=True)
    count = IntegerField(default=0)


def increment_counter(name):
    Counter.insert(name=name, count=1).on_conflict(conflict_target=[Counter.name],update={Counter.count: Counter.count + 1}).execute()


def hydrate():
    increment_counter('hydrate')
    return hydrate_stats()


def hydrate_stats():
    drinks = Counter.get(Counter.name=='hydrate').count
    return f'hwangbroXD has hydrated {drinks} times today hexTHIRST'


def stats(poke):
    pokemon = 'nido' if 'nido' in poke else 'pidgey'
    catch = Counter.get(Counter.name == pokemon)
    fail = Counter.get(Counter.name == f'{pokemon}fail')
    return f'We caught {pokemon} {catch.count}/{catch.count+fail.count} times today.'


def drop_table():
    with db:
        db.drop_tables([Counter])

def create_tables():
    with db:
        db.create_tables([Counter])


def close_db():
    db.close()


def reset_entries(stat):
    source = []
    if stat in ['nido', '']:
        source += [{'name': 'nido'}, {'name': 'nidofail'}]
    if stat in ['pidgey', '']:
        source += [{'name': 'pidgey'}, {'name': 'pidgeyfail'}]
    if stat in ['hydrate', '']:
        source += [{'name': 'hydrate'}]
    Counter.insert_many(source).on_conflict(conflict_target=[Counter.name],  update={Counter.count: 0}).execute()
    return f'Resetting {stat} stats back to 0'

# increment_counter('nidoran')
#drop_table()
#create_tables()
# increment_counter('nidoran')
# increment_counter('pidgey')
# reset_counter('nidoran')
# reset_all()
# increment_counter('pidgeyfail')
# print(stats('pidgey'))
# print(hydrate())