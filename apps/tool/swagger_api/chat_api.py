# coding=utf-8
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin

# 首先定义最内层的结构
TextItem = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'type': openapi.Schema(type=openapi.TYPE_STRING),
        'text': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['type', 'text']
)

ImageItem = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'type': openapi.Schema(type=openapi.TYPE_STRING),
        'image_url': openapi.Schema(type=openapi.TYPE_OBJECT),
    },
    required=['type', 'image_url']
)

# 定义 content 的子项，它可以是 TextItem 或者一个简单的字符串
ContentItem = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=[
        TextItem,
        ImageItem
    ]
)


# 定义 messages 的结构，它可以包含多个 ContentItem
# ContentItem = openapi.Schema(
#     type=openapi.TYPE_OBJECT,
#     properties={
#         'content': openapi.Schema(
#             type=openapi.TYPE_ARRAY,
#             items=openapi.Items(oneOf=[TextItem, ImageItem])
#         ),
#     },
#     required=['content']
# )

class ChatApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        messages = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['role', 'content'],
            properties={
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="角色", description="角色"),
                'content': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    oneOf=[
                        ContentItem,
                        openapi.Schema(type=openapi.TYPE_STRING)
                    ], title="内容", description="内容")
            }
        )
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['model_id', 'message'],
            properties={
                'max_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, title="max_tokens", description="max_tokens",
                                             default=2048),
                'temperature': openapi.Schema(type=openapi.TYPE_NUMBER, title="temperature", description="temperature",
                                              default=0.8),
                'top_p': openapi.Schema(type=openapi.TYPE_NUMBER, title="top_p", description="top_p", default=0.8),
                'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                'messages': openapi.Schema(type=openapi.TYPE_ARRAY, title="问题", description="问题", items=messages),
                'stream': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="流式返回", default=True)

            }
        )
