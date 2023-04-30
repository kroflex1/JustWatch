import pytest

from app import schemas, models, crud, errors, authentication
from app.database import PeeweeConnectionState
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video, models.Comment])
test_db.drop_tables([models.User, models.Video, models.Comment])
test_db.create_tables([models.User, models.Video, models.Comment])
test_db.close()


def create_author():
    user = schemas.UserCreate(email='test_user@mail.ru', username='test_user_name', password='test_user_password')
    return crud.create_user(user)


def create_video(author_id: int):
    return crud.create_video(schemas.VideoCreate(video_name='fake video', description='fake video descr'), author_id)


def test_create_comment():
    author = create_author()
    video = create_video(author_id=author.id)
    comment_text = 'some text'
    comment = crud.create_comment(
        schemas.CommentCreate(video_id=video.id, author_id=author.id, text=comment_text))
    assert comment.author_id.id == author.id
    assert comment.video_id.id == video.id
    assert comment.text == comment_text
    test_db.drop_tables([models.User, models.Video, models.Comment])
    test_db.create_tables([models.User, models.Video, models.Comment])


def test_create_many_comments():
    author = create_author()
    video = create_video(author_id=author)
    number_of_comments = 5
    for i in range(number_of_comments):
        crud.create_comment(schemas.CommentCreate(video_id=video.id, author_id=author.id, text=i))
    assert len(video.comments) == number_of_comments
    test_db.drop_tables([models.User, models.Video, models.Comment])
    test_db.create_tables([models.User, models.Video, models.Comment])


def test_get_comments_show_inf_from_video():
    author = create_author()
    video = create_video(author_id=author)
    number_of_comments = 5
    for i in range(number_of_comments):
        crud.create_comment(schemas.CommentCreate(video_id=video.id, author_id=author.id, text=i))
    comments_show_inf = crud.get_comments_show_inf_from_video(video.id)
    assert len(comments_show_inf) == number_of_comments
    for comment_show_inf in comments_show_inf:
        assert comment_show_inf.author_name == author.username
    test_db.drop_tables([models.User, models.Video, models.Comment])
    test_db.create_tables([models.User, models.Video, models.Comment])
