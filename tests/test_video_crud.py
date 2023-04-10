from app import schemas, models, crud, errors
from app.database import PeeweeConnectionState
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video])
test_db.drop_tables([models.User, models.Video])
test_db.create_tables([models.User, models.Video])
test_db.close()

VIDEO_NAME = 'Top 10 cats'
VIDEO_DESCRIPTION = 'The most funny cats'


def create_author():
    user = schemas.UserCreate(email='test_user@mail.ru', username='test_user_name', password='test_user_password')
    return crud.create_user(user)


def test_create_video():
    author = create_author()
    video_base = schemas.VideoBase(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    assert video_db.video_name == VIDEO_NAME
    assert video_db.description == VIDEO_DESCRIPTION
    assert video_db.author_id.id == author.id
    test_db.drop_tables([models.User, models.Video])
    test_db.create_tables([models.User, models.Video])


def test_author_have_videos():
    author = create_author()
    video_bases = [('video_1', 'video_1_desc'), ('video_2', 'video_2_desc'), ('video_3', 'video_3_desc')]
    for video_name, video_desc in video_bases:
        crud.create_video(schemas.VideoBase(video_name=video_name, description=video_desc), author.id)
    result = []
    for video in author.videos:
        result.append(video.video_name)
    assert len(result) == 3
    assert set(result) == set([video_name for video_name, video_desc in video_bases])
    test_db.drop_tables([models.User, models.Video])
    test_db.create_tables([models.User, models.Video])

