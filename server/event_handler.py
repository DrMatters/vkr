import os
import json
from flask import abort
from google.cloud import datastore, pubsub_v1

key = os.environ['KEY']
project_id = os.environ['GCP_PROJECT']

datastore_client = None
publisher = None


def event_handler(request):
    content = request.get_json()
    if content['type'] == 'confirmation':
        return key
    elif content['type'] == 'wall_reply_new':
        handle_wall_reply_new(content['group_id'], content['object'])
        return key
    elif content['type'] == 'wall_reply_delete':
        handle_wall_reply_delete(content['group_id'], content['object'])
        return key
    else:
        abort(400)


def handle_wall_reply_new(group_id, comment):
    # TODO: clean code !!! of this function

    global datastore_client
    if not datastore_client:
        datastore_client = datastore.Client()

    comment_key = datastore_client.key('Group', group_id, 'Comment', comment['id'])
    comment_entity = datastore.Entity(key=comment_key)
    comment_entity.update(comment)
    comment_entity.update({
        'group_id': group_id,
        'known_class': None,                                 # None stands for unknown
        'predicted_probability': None,                       # None stands for unpredicted
    })
    datastore_client.put(comment_entity)

    global publisher
    if not publisher:
        publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'new_comment')

    group_key = datastore_client.key('Group', group_id)
    group_entity = datastore_client.get(group_key)
    data_for_classification = {
        'id': comment_entity['id'],
        'text': comment_entity['text'],
        'group_id': group_id,
        'base_folder_path': group_entity['base_folder_path'],
        'framework': group_entity['framework'],
        'preprocessing_version': group_entity['preprocessing_version']
    }
    data = json.dumps(data_for_classification, ensure_ascii=False).encode('utf-8')
    future = publisher.publish(topic_path, data=data)
    print(f'Published {data} of message ID {future.result()}.')


def handle_wall_reply_delete(group_id, comment):
    global datastore_client
    if not datastore_client:
        datastore_client = datastore.Client()

    comment_key = datastore_client.key('Group', group_id, 'Comment', comment['id'])
    comment_entity = datastore_client.get(comment_key)
    comment_entity.update(comment)
    # TODO: check if it's moderator who's deleted the comment
    comment_entity.update({
        'known_class': 1,                       # if comment is deleted by
                                                # admin (user) then we know, that is may be inappropriate
    })
    datastore_client.put(comment_entity)

