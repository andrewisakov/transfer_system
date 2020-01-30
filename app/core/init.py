import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateDatabase, DuplicateTable
from app.settings import INIT, DSN

database = DSN['database']
CREATE_DATABASE = f'create database {database};'
CREATE_TRANSFERS = (
    'create table transfers ('
    'participant_id integer not null, '
    'payee_id integer not null, '
    'amount NUMERIC(12, 4) not null, '
    'created_at timestamptz not null default now(), '
    'description varchar(512), '
    'primary key (participant_id, created_at), '
    'constraint participant_id_fkey '
    'foreign key (participant_id) '
    'references participants (id) match simple '
    'on update no action on delete no action'
    ');'
)
CREATE_PARTICIPANTS = (
    'create table participants ('
    'id serial primary key, '
    'currency char(3) default \'RUB\', '
    'email varchar(255) unique not null, '
    'password varchar(40) not null, '
    'created_at timestamptz not null default now(), '
    'last_login timestamptz '
    ''
    ');'
)
SELECT_TRANSFERS = (
    'select t.created_at, description, p.email as payer, '
    'pp.email as payee, (t.participant_id=t.payee_id) as self '
    'from transfers t '
    'join participants p on (p.id=t.participant_id) '
    'join participants pp on (pp.id=t.payee_id) '
    'where timestamp beetween %s and %s;'
)
GET_ACTUAL = (
    'select '
    'from transfers tr '

)
INSERT_TRANSFER = (

)
INSERT_PARTICIPANT = 'insert into participants (email, password, currency) values (%s, %s, %s);'

CREATE_CURRENCIES = (
    'create table currencies ('
    'id varchar(3) not null, '
    'rate NUMERIC(12, 4) not null, '
    'actual_date timestamp not null, '
    'primary key (id, actual_date)'
    ');'
    'create index on currencies (id, actual_date);'
)

ACCOUNT = 'select id, email, password, created_at from participants where email=%s password=%s'
SELECT_PARTICIPANT = 'select id from participants where email=%s and password=%s;'


def init():

    with psycopg2.connect(**INIT) as init_db:
        init_db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with init_db.cursor() as c:
            try:
                c.execute(CREATE_DATABASE)
            except DuplicateDatabase as e:
                init_db.rollback()

    with psycopg2.connect(**DSN) as dsn:
        dsn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with dsn.cursor() as c:
            for CREATE in (CREATE_CURRENCIES, CREATE_PARTICIPANTS, CREATE_TRANSFERS):
                try:
                    c.execute(CREATE)
                except DuplicateTable as e:
                    dsn.rollback()
            try:
                c.execute(INSERT_PARTICIPANT,
                        ('admin',
                        '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8',  # password
                        None,
                        ))
            except Exception as e:
                pass