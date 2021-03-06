import os
import simplejson
from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

import util.video
from model.video import Video
from model.comment import Comment
from model.user import User

site = Blueprint('video', __name__)

# @site.route('/play', methods=['GET'])
# def play_video(userid,videoid):
#     page_title='NyanNyan'
#     desc='Blablabla'
#     return render_template('_videoplayer.html',video_data = video)
# 
# @site.route('/uservideos', methods=['GET'])
# def list_uservideos(userid,sort='time'):
#     return render_template('_uservideos.html')

def get_current_videos():
    videos = current_user.videos
    file_display = []
    for video in videos:
        file_saved = util.video.UploadResponse(name=video.title,
                                               size=video.size,
                                               url=url_for('video.play', id=video.id),
                                               delete_url=url_for('video.delete', id=video.id))
        file_display.append(file_saved.get_file())
    return simplejson.dumps({"files": file_display})

@site.route("/manage", methods=['GET'])
@login_required
def manage():
    return render_template('video/manage.html')

@site.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            filename = util.video.get_non_conflict_name(filename, current_user)
            mimetype = file.content_type

            if not util.video.allowed_file(filename):
                result = util.video.UploadResponse(name=filename,
                                                   type=mimetype,
                                                   size=0,
                                                   not_allowed_msg="Filetype not allowed")

            else:
                # save then record to db
                video = Video.upload(file, filename, current_user)

                # create thumbnail after saving
                # if mimetype.startswith('image'):
                #     create_thumbnai(filename)

                # return json for js call back
                result = util.video.UploadResponse(name=video.title,
                                                   type=mimetype,
                                                   size=video.size,
                                                   not_allowed_msg=None,
                                                   url=url_for('video.play', id=video.id),
                                                   delete_url=url_for('video.delete', id=video.id))

            # for validation
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        return get_current_videos()

    redirect(url_for('video.manage'))

@site.route("/play/<id>", methods=['GET'])
@login_required
def play(id):
    video = Video.from_id(id)
    poster = User.from_id(video.poster_id)
    return render_template('video/play.html', poster=poster, video=video)

@site.route("/delete/<id>", methods=['DELETE'])
@login_required
def delete(id):
    Video.from_id(id).delete()
    return get_current_videos()


