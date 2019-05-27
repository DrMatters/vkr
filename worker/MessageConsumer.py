import ModelRunner
import json
from google.cloud import pubsub_v1


class MessageConsumer:
    def __init__(self, project_id):
        # load model runner with default model
        self.models_info = {}
        self.models = {}
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = project_id

    def new_message_callback(self, message):
        data = json.loads(message.data)
        msg_text = data['text']

        self.hotswap_model_if_needed(data['group_id'], data['base_folder_path'],
                                     data['framework'], data['preprocessing_version'])

        probability = self.models[data['group_id']].run(msg_text)
        self.publish_processed(data, probability)
        message.ack()
        print(f"Acked: `{data}`. Probability: {probability}")

    def hotswap_model_if_needed(self, group_id, new_base_folder_path, framework, preprocessing_version):
        if group_id in self.models_info:
            if new_base_folder_path == self.models_info[group_id]:
                # hotswap or initialization is not required
                return False

        # make hotswap
        # create a model and rewrite or `just` write model to dispatch dictionary
        self.models_info[group_id] = new_base_folder_path
        self.models[group_id] = ModelRunner.ModelRunner(base_folder_path=new_base_folder_path,
                                                        framework=framework,
                                                        preprocessing_version=preprocessing_version)
        return True

    def publish_processed(self, message_data, probability):
        topic_path = self.publisher.topic_path(self.project_id, 'add_classified_comment')
        data = {
            'id': message_data['id'],
            'probability': probability,
        }
        data_json = json.dumps(data, ensure_ascii=False).encode('utf-8')
        _ = self.publisher.publish(topic_path, data=data_json)
        print(f'Published ""{data}"".')
