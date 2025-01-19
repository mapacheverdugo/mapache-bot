import logging
from typing import Any, Callable, Dict, List, Optional, Union

from telebot import REPLY_MARKUP_TYPES, TeleBot, types


class MessagerInterface:
    def send_message(self, chat_id: Union[int, str], text: str, 
            parse_mode: Optional[str]=None, 
            entities: Optional[List[types.MessageEntity]]=None,
            disable_web_page_preview: Optional[bool]=None,    # deprecated, for backward compatibility
            disable_notification: Optional[bool]=None, 
            protect_content: Optional[bool]=None,
            reply_to_message_id: Optional[int]=None,          # deprecated, for backward compatibility
            allow_sending_without_reply: Optional[bool]=None, # deprecated, for backward compatibility
            reply_markup: Optional[REPLY_MARKUP_TYPES]=None,
            timeout: Optional[int]=None,
            message_thread_id: Optional[int]=None,
            reply_parameters: Optional[types.ReplyParameters]=None,
            link_preview_options : Optional[types.LinkPreviewOptions]=None,
            business_connection_id: Optional[str]=None,
            message_effect_id: Optional[str]=None,
            allow_paid_broadcast: Optional[bool]=None) -> types.Message:
        pass
    
    def message_handler(
            commands: Optional[List[str]]=None,
            regexp: Optional[str]=None,
            func: Optional[Callable]=None,
            content_types: Optional[List[str]]=None,
            chat_types: Optional[List[str]]=None,
            **kwargs):
        """A decorator that is used to register a view function for a
        given URL rule.  This does the same thing as :meth:`add_url_rule`
        but is intended for decorator usage::
            @app.route('/')
            def index():
                return 'Hello World'
        For more information refer to :ref:`url-route-registrations`.
        :param rule: the URL rule as string
        :param endpoint: the endpoint for the registered URL rule.  Flask
                         itself assumes the name of the view function as
                         endpoint
        :param options: the options to be forwarded to the underlying
                        :class:`~werkzeug.routing.Rule` object.  A change
                        to Werkzeug is handling of method options.  methods
                        is a list of methods this rule should be limited
                        to (``GET``, ``POST`` etc.).  By default a rule
                        just listens for ``GET`` (and implicitly ``HEAD``).
                        Starting with Flask 0.6, ``OPTIONS`` is implicitly
                        added and handled by the standard request handling.
        """
        pass
    
    def poll(self, timeout: Optional[int]=20, skip_pending: Optional[bool]=False, long_polling_timeout: Optional[int]=20,
                         logger_level: Optional[int]=logging.ERROR, allowed_updates: Optional[List[str]]=None,
                         restart_on_change: Optional[bool]=False, path_to_watch: Optional[str]=None, *args, **kwargs):
        '''These should also be in the config section, but some here for
        overrides

        '''
        pass

class TeleBotMessager(MessagerInterface):
    def __init__(self, api_key):
        self.api_key = api_key
        self.bot = TeleBot(api_key)


    def send_message(self, chat_id: Union[int, str], text: str, 
            parse_mode: Optional[str]=None, 
            entities: Optional[List[types.MessageEntity]]=None,
            disable_web_page_preview: Optional[bool]=None,    # deprecated, for backward compatibility
            disable_notification: Optional[bool]=None, 
            protect_content: Optional[bool]=None,
            reply_to_message_id: Optional[int]=None,          # deprecated, for backward compatibility
            allow_sending_without_reply: Optional[bool]=None, # deprecated, for backward compatibility
            reply_markup: Optional[REPLY_MARKUP_TYPES]=None,
            timeout: Optional[int]=None,
            message_thread_id: Optional[int]=None,
            reply_parameters: Optional[types.ReplyParameters]=None,
            link_preview_options : Optional[types.LinkPreviewOptions]=None,
            business_connection_id: Optional[str]=None,
            message_effect_id: Optional[str]=None,
            allow_paid_broadcast: Optional[bool]=None) -> types.Message:
        return self.bot.send_message(
            chat_id,
            text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            link_preview_options=link_preview_options,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast
        )

    def message_handler(self, commands: Optional[List[str]]=None,
            regexp: Optional[str]=None,
            func: Optional[Callable]=None,
            content_types: Optional[List[str]]=None,
            chat_types: Optional[List[str]]=None,
            **kwargs):
        
        return self.bot.message_handler(
            commands=commands,
            regexp=regexp,
            func=func,
            content_types=content_types,
            chat_types=chat_types,
            **kwargs
        )
    
    def poll(self, timeout: Optional[int]=20, skip_pending: Optional[bool]=False, long_polling_timeout: Optional[int]=20,
                         logger_level: Optional[int]=logging.ERROR, allowed_updates: Optional[List[str]]=None,
                         restart_on_change: Optional[bool]=False, path_to_watch: Optional[str]=None, *args, **kwargs):
        return self.bot.infinity_polling(
            timeout=timeout,
            skip_pending=skip_pending,
            long_polling_timeout=long_polling_timeout,
            logger_level=logger_level,
            allowed_updates=allowed_updates,
            restart_on_change=restart_on_change,
            path_to_watch=path_to_watch,
            *args,
            **kwargs
        )
        
