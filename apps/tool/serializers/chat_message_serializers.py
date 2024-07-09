# coding=utf-8
import json
import uuid

import requests
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from rest_framework import serializers

from common.exception.app_exception import AppModelException
from common.util.field_message import ErrMessage
from common.util.rsa_util import rsa_long_decrypt
from setting.models import Model, Status
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants


# chat_cache = caches['model_cache']

class ChatMessageSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))
    messages = serializers.ListField(required=True, error_messages=ErrMessage.char("用户问题"))
    stream = serializers.BooleanField(required=True, error_messages=ErrMessage.char("是否流式回答"))
    max_tokens = serializers.IntegerField(required=True, error_messages=ErrMessage.uuid("最大长度"))
    top_p = serializers.FloatField(required=True, error_messages=ErrMessage.char("top_p"))
    temperature = serializers.FloatField(required=True, error_messages=ErrMessage.char("temperature"))

    def execute_stream(self, response):
        chat_id = uuid.uuid1()

        def handler():
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')[6:]
                    try:
                        response_json = json.loads(decoded_line)
                        print("content", response_json)
                        content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        yield 'data: ' + json.dumps({'id': str(chat_id), 'operate': True,
                                                     'content': content, 'is_end': False}) + "\n\n"
                    except Exception as e:
                        print("Special Token:", decoded_line)
            yield 'data: ' + json.dumps({'id': str(chat_id), 'operate': True,
                                         'content': "", 'is_end': True}) + "\n\n"

        r = StreamingHttpResponse(
            streaming_content=handler(),
            content_type='text/event-stream;charset=utf-8')

        r['Cache-Control'] = 'no-cache'
        return r

    def chat_simple(self):
        model_id = self.data.get('model_id')
        model = QuerySet(Model).filter(id=model_id).first()
        if model is None:
            raise AppModelException(500, "当前模型不可用")
        if model.status == Status.ERROR:
            raise AppModelException(500, "当前模型不可用")
        vlm_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                          json.loads(
                                                                              rsa_long_decrypt(
                                                                                  model.credential)),
                                                                          streaming=True)
        messages = self.data.get('messages')
        stream = self.data.get('stream')
        max_tokens = self.data.get('max_tokens')
        top_p = self.data.get('top_p')
        temperature = self.data.get('temperature')
        data = {
            "model": model.name,
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        base_url = vlm_model.openai_api_base
        try:
            response = requests.post(f"{base_url}/chat/completions", json=data, stream=stream)
        except BaseException as e:
            raise AppModelException(500, f'模型调用失败: {str(e)}')
        if response.status_code == 200:
            if stream:
                return self.execute_stream(response)
            else:
                # 处理非流式响应
                decoded_line = response.json()
                content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
                return content
        else:
            print("Error:", response.status_code)
            return "出错了"

    def chat(self):
        super().is_valid(raise_exception=True)
        return self.chat_simple()
