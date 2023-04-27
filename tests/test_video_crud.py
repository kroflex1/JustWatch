import pytest

from app import schemas, models, crud, errors
from app.database import PeeweeConnectionState
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video])
test_db.drop_tables([models.User, models.Video, models.Reaction])
test_db.create_tables([models.User, models.Video, models.Reaction])
test_db.close()

VIDEO_NAME = 'Top 10 cats'
VIDEO_DESCRIPTION = 'The most funny cats'


def create_author():
    user = schemas.UserCreate(email='test_user@mail.ru', username='test_user_name', password='test_user_password')
    return crud.create_user(user)


def create_user(email, username, password):
    user = schemas.UserCreate(email=email, username=username, password=password)
    return crud.create_user(user)


def test_author_have_videos():
    author = create_author()
    video_bases = [('video_1', 'video_1_desc'), ('video_2', 'video_2_desc'), ('video_3', 'video_3_desc')]
    for video_name, video_desc in video_bases:
        crud.create_video(schemas.VideoCreate(video_name=video_name, description=video_desc), author.id)
    result = []
    for video in author.videos:
        result.append(video.video_name)
    assert len(result) == 3
    assert set(result) == set([video_name for video_name, video_desc in video_bases])
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_create_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    assert video_db.video_name == VIDEO_NAME
    assert video_db.description == VIDEO_DESCRIPTION
    assert video_db.author_id.id == author.id
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_like_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == True
    assert reaction_db.is_dislike == False
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_dislike_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.DISLIKE)
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == False
    assert reaction_db.is_dislike == True
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_neutral_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.NEUTRAL)
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == False
    assert reaction_db.is_dislike == False
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_like_video_twice():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    assert len(video_db.reactions) == 1
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == True
    assert reaction_db.is_dislike == False
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_like_and_dislike_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.DISLIKE)
    assert len(video_db.reactions) == 1
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == False
    assert reaction_db.is_dislike == True
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_like_and_neutral_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    reaction_db = crud.rate_video(user_id=author.id, video_id=video_db.id, user_reaction=crud.Reaction.NEUTRAL)
    assert len(video_db.reactions) == 1
    assert reaction_db.video.id == video_db.id
    assert reaction_db.user.id == author.id
    assert reaction_db.is_like == False
    assert reaction_db.is_dislike == False
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_many_likes():
    number_of_likes = 5
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, 1)
    for i in range(number_of_likes):
        new_user_db = create_user(i, i, 'somePassword')
        crud.rate_video(user_id=new_user_db.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    reactions_inf = crud.get_video_number_of_likes_and_dislikes(video_db.id)
    assert len(video_db.reactions) == 5
    assert reactions_inf.number_of_likes == 5
    assert reactions_inf.number_of_dislikes == 0
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_many_likes_and_dislikes():
    number_of_rates = 5
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, 1)
    for i in range(number_of_rates):
        new_user_like_db = create_user(i, i, 'somePassword')
        new_user_dislike_db = create_user(i + number_of_rates, i + number_of_rates, 'somePassword')
        crud.rate_video(user_id=new_user_like_db.id, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
        crud.rate_video(user_id=new_user_dislike_db.id, video_id=video_db.id, user_reaction=crud.Reaction.DISLIKE)

    reactions_inf = crud.get_video_number_of_likes_and_dislikes(video_db.id)
    assert len(video_db.reactions) == number_of_rates * 2
    assert reactions_inf.number_of_likes == 5
    assert reactions_inf.number_of_dislikes == 5
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_rate_non_existent_video():
    author = create_author()
    with pytest.raises(errors.VideoNotExist):
        crud.rate_video(user_id=author.id, video_id=9999, user_reaction=crud.Reaction.LIKE)
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])


def test_non_existent_user_rate_video():
    author = create_author()
    video_base = schemas.VideoCreate(video_name=VIDEO_NAME, description=VIDEO_DESCRIPTION)
    video_db = crud.create_video(video_base, author.id)
    with pytest.raises(errors.AccountNotFound):
        crud.rate_video(user_id=9999, video_id=video_db.id, user_reaction=crud.Reaction.LIKE)
    test_db.drop_tables([models.User, models.Video, models.Reaction])
    test_db.create_tables([models.User, models.Video, models.Reaction])
