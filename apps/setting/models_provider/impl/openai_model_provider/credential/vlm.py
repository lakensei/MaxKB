# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:32
    @desc:
"""
from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class OpenAIVLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            img_url = f"data:image/jpeg;base64,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"
            content = [
                {
                    "type": "text",
                    "text": "What’s in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_url
                    },
                },
            ]
            model.invoke([HumanMessage(content=content)])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)
