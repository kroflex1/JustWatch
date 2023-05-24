from . import models, schemas, errors
from passlib.context import CryptContext
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Reaction(str, Enum):
    LIKE = 'like'
    DISLIKE = 'dislike'
    NEUTRAL = 'neutral'


def get_user_by_id(user_id: int):
    return models.User.filter(models.User.id == user_id).first()


def get_user_by_email(email: str):
    return models.User.filter(models.User.email == email).first()


def get_user_by_email_and_password(email: str, password: str):
    db_user = get_user_by_email(email)
    if db_user is not None and pwd_context.verify(password, db_user.hashed_password):
        return db_user


def create_user(user: schemas.UserCreate):
    if user.username == '' or user.email == '' or user.password == '':
        raise errors.AuthError
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    try:
        db_user.save()
    except:
        raise errors.RegisterError
    else:
        return db_user


def delete_user_by_id(user_id: int):
    q = models.User.delete().where(models.User.id == user_id)
    q.execute()


def delete_user_by_email(email: str):
    q = models.User.delete().where(models.User.email == email)
    q.execute()


def update_user_refresh_token(user_id: int, refresh_token: str):
    q = (models.User.update({models.User.refresh_token: refresh_token}).where(models.User.id == user_id))
    q.execute()


def create_video(video_base: schemas.VideoCreate, user_id: int):
    db_video = models.Video(video_name=video_base.video_name, author_id=user_id, description=video_base.description)
    db_video.save()
    return db_video


def get_video_by_id(video_id: int):
    return models.Video.filter(models.Video.id == video_id).first()


def get_all_videos():
    return models.Video.select()


def rate_video(user_id: int, video_id: int, user_reaction: Reaction):
    if get_video_by_id(video_id) is None:
        raise errors.VideoNotExist
    if get_user_by_id(user_id) is None:
        raise errors.AccountNotFound

    try:
        db_reaction = models.Reaction.get(
            (models.Reaction.user == user_id) &
            (models.Reaction.video == video_id))
    except models.Reaction.DoesNotExist:
        db_reaction = models.Reaction.create(
            user_id=user_id, video_id=video_id, is_like=user_reaction == Reaction.LIKE,
            is_dislike=user_reaction == Reaction.DISLIKE
        )
    else:
        if user_reaction == Reaction.NEUTRAL:
            db_reaction.is_like = False
            db_reaction.is_dislike = False
        elif user_reaction == Reaction.LIKE:
            db_reaction.is_like = True
            db_reaction.is_dislike = False
        else:
            db_reaction.is_like = False
            db_reaction.is_dislike = True
        db_reaction.save()
    return db_reaction


def get_video_number_of_likes_and_dislikes(video_id: int) -> schemas.VideoReactionsInf:
    number_of_likes = models.Reaction.select().where(
        (models.Reaction.video == video_id) & (models.Reaction.is_like == Reaction.LIKE)).count()
    number_of_dislike = models.Reaction.select().where(
        (models.Reaction.video == video_id) & (models.Reaction.is_dislike == Reaction.DISLIKE)).count()

    return schemas.VideoReactionsInf(number_of_likes=number_of_likes,
                                     number_of_dislikes=number_of_dislike)


def get_user_reaction_to_video(user_id: int, video_id: int) -> str:
    try:
        reaction_db = models.Reaction.get((models.Reaction.user == user_id) & (models.Reaction.video == video_id))
        if reaction_db.is_like:
            return 'like'
        if reaction_db.is_dislike:
            return 'dislike'
        return 'neutral'
    except:
        return 'neutral'


def create_comment(comment_inf: schemas.CommentCreate):
    comment_db = models.Comment(video_id=comment_inf.video_id, author_id=comment_inf.author_id, text=comment_inf.text)
    comment_db.save()
    return comment_db


def get_comments_show_inf_from_video(video_id: int) -> list[schemas.CommentShow]:
    comments = models.Video.get(models.Video.id == video_id).comments
    result = []
    for comment in comments:
        author_name = models.User.get(models.User.id == comment.author_id).username
        result.append(
            schemas.CommentShow(author_name=author_name, text=comment.text, published_at=comment.published_at))
    return result


def delete_video(video_id: int):
    q = models.Video.delete().where(models.Video.id == video_id)
    q.execute()


def subscribe(subscriber_id: int, author_id: int):
    if subscriber_id == author_id:
        raise errors.SubscribeToYourself
    try:
        models.Subscriber.create(subscriber=subscriber_id, author=author_id)
    except:
        raise errors.AlreadySubscribed


def unsubscribe(subscriber_id: int, author_id: int):
    if subscriber_id == author_id:
        raise errors.SubscribeToYourself
    try:
        q = models.Subscriber.delete().where((models.Subscriber.subscriber == subscriber_id) & (models.Subscriber.author == author_id))
        q.execute()
    except:
        raise errors.AlreadySubscribed

def is_user_subscribed_to_author(user_id:int, author_id:int):
    if user_id == author_id:
        return False
    try:
        models.Subscriber.get((models.Subscriber.subscriber == user_id) & (models.Subscriber.author == author_id))
    except:
        return False
    else:
        return True