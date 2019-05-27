import MessageConsumer
import time
from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists

project_id = 'ai-moderator'
subscriber = pubsub_v1.SubscriberClient()


def create_subscription(sub_name, topic_name, callback):
    topic_path = subscriber.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(project_id, sub_name)

    try:
        subscriber.create_subscription(subscription_path, topic_path)
    except AlreadyExists as e:
        print(e)

    return subscriber.subscribe(subscription_path, callback)


def main():
    consumer = MessageConsumer.MessageConsumer(project_id=project_id)

    future = create_subscription('new_comment_sub', 'new_comment', consumer.new_message_callback)

    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        print('\nSuccessful shutdown')
    except Exception as ex:
        future.cancel()
        print(ex)


if __name__ == "__main__":
    main()
