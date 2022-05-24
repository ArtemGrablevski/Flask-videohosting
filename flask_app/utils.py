from .models import UserModel, VideoModel, db


def is_email_unique(email: str) -> bool:
    return False if UserModel.query.filter_by(email = email).first() is None else True

def is_username_unique(username: str ) -> bool:
    return False if UserModel.query.filter_by(username = username).first() is None else True

def does_username_exists(email: str) -> bool:
    return False if UserModel.query.filter_by(email = email).first() is None else True

def get_all_videos() -> list[VideoModel]:
    return VideoModel.query.all()[::-1]

def get_all_videos_of_user(username: str) -> list[VideoModel]:
    return VideoModel.query.filter_by(author=username).all()[::-1]

def get_user_by_email(email: str) -> UserModel:
    return UserModel.query.filter_by(email = email).first()

def get_user_by_username(username: str) -> UserModel:
    return UserModel.query.filter_by(username = username).first()

def get_video_by_id(id: int) -> VideoModel:
    return VideoModel.query.filter_by(id=id).first_or_404()

def create_new_video(video_title: str, author: str, path: str) -> VideoModel:
    video = VideoModel(title=video_title, author=author, path=path)
    db.session.add(video)
    db.session.flush()
    db.session.commit()
    return video

def create_new_user(username: str, email: str, hpsw: str) -> UserModel:
    user = UserModel(username=username, email=email, hpsw=hpsw)
    db.session.add(user)
    db.session.flush()
    db.session.commit()
    return user

def change_password(email: str, hpsw: str) -> UserModel:
    user = UserModel.query.filter_by(email = email).first()
    user.hpsw = hpsw
    db.session.add(user)
    db.session.flush()
    db.session.commit()
    return user

