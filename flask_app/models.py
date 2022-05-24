from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from hashlib import md5
from werkzeug.utils import secure_filename
from datetime import datetime
import os


db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(40), nullable=False)
    hpsw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.id} {self.username}"

    def avatar(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=mp&s=128"
    
    def has_liked_video(self, video):
        return LikeModel.query.filter(LikeModel.username == self.username, LikeModel.video_id == video.id).count() > 0

    def like_video(self, video):
        if not self.has_liked_video(video):
            like = LikeModel(username=self.username, video_id=video.id)
            db.session.add(like)
            db.session.flush()
            db.session.commit()

    def unlike_video(self, video):
        if self.has_liked_video(video):
            LikeModel.query.filter_by(username=self.username, video_id=video.id).delete()
            db.session.commit()

    def show_user_likes(self):
        all_video_id = []
        likes = LikeModel.query.filter_by(username=self.username)
        for like in likes:
            all_video_id.append(like.video_id)
        return VideoModel.query.filter(VideoModel.id.in_(all_video_id)).all()


class VideoModel(db.Model):
    __tablename__ = "Videos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    author = db.Column(db.String(25), db.ForeignKey("Users.username"))
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    path = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"Video {self.id} {self.title} by {self.author}"

    def count_likes(self):
        return LikeModel.query.filter_by(video_id=self.id).count()

    def get_author(self):
        return UserModel.query.filter_by(username=self.author).first()

    def delete_video(self):
        os.remove("flask_app/" + self.path)
        LikeModel.query.filter_by(video_id=self.id).delete()
        VideoModel.query.filter_by(id=self.id).delete()
        db.session.commit()


class LikeModel(db.Model):
    __tablename__ = "Likes"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("Videos.id"))
    username = db.Column(db.String(25), db.ForeignKey("Users.username"))

    def __repr__(self):
        return f"Like on video {self.video_id} by {self.username}"