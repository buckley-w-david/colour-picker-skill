# -*- coding: utf-8 -*-
#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

######## Convert SSML to Card text ############
# This is for automatic conversion of ssml to text content on simple card
# You can create your own simple cards for each response, if this is not
# what you want to use.

from six import PY3
if PY3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser


class SSMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.full_str_list = []
        if PY3:
            self.strict = False
            self.convert_charrefs = True

    def handle_data(self, d):
        self.full_str_list.append(d)

    def get_data(self):
        return ''.join(self.full_str_list)

################################################


skill_name = "My Colour Session"
help_text = ("Please tell me your favorite colour. You can say "
             "my favorite colour is red")

colour_slot_key = "COLOUR"
colour_slot = "Colour"

sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # Handler for Skill Launch
    speech = "Welcome to the Alexa Skills Kit colour session sample."

    handler_input.response_builder.speak(
        speech + " " + help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # Handler for Help Intent
    handler_input.response_builder.speak(help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    # Single handler for Cancel and Stop Intent
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # Handler for Session End
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("WhatsMyColourIntent"))
def whats_my_colour_handler(handler_input):
    # Check if a favorite colour has already been recorded in session attributes
    # If yes, provide the colour to the user. If not, ask for favorite colour
    if colour_slot_key in handler_input.attributes_manager.session_attributes:
        fav_colour = handler_input.attributes_manager.session_attributes[
            colour_slot_key]
        speech = "Your favorite colour is {}. Goodbye!!".format(fav_colour)
        handler_input.response_builder.set_should_end_session(True)
    else:
        speech = "I don't think I know your favorite colour. " + help_text
        handler_input.response_builder.ask(help_text)

    handler_input.response_builder.speak(speech)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("MyColourIsIntent"))
def my_colour_handler(handler_input):
    # Check if colour is provided in slot values. If provided, then
    # set your favorite colour from slot value into session attributes.
    # If not, then it asks user to provide the colour.
    slots = handler_input.request_envelope.request.intent.slots

    if colour_slot in slots:
        fav_colour = slots[colour_slot].value
        handler_input.attributes_manager.session_attributes[
            colour_slot_key] = fav_colour
        speech = ("Now I know that your favorite colour is {}. "
                  "You can ask me your favorite colour by saying, "
                  "what's my favorite colour ?".format(fav_colour))
        reprompt = ("You can ask me your favorite colour by saying, "
                    "what's my favorite colour ?")
    else:
        speech = "I'm not sure what your favorite colour is, please try again"
        reprompt = ("I'm not sure what your favorite colour is. "
                    "You can tell me your favorite colour by saying, "
                    "my favorite colour is red")

    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    # AMAZON.FallbackIntent is only available in en-US locale.
    # This handler will not be triggered except in that locale,
    # so it is safe to deploy on any locale
    speech = (
        "The {} skill can't help you with that.  "
        "You can tell me your favorite colour by saying, "
        "my favorite colour is red").format(skill_name)
    reprompt = ("You can tell me your favorite colour by saying, "
                "my favorite colour is red")
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


def convert_speech_to_text(ssml_speech):
    # convert ssml speech to text, by removing html tags
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


@sb.global_response_interceptor()
def add_card(handler_input, response):
    # Add a card by translating ssml text to card content
    response.card = SimpleCard(
        title=skill_name,
        content=convert_speech_to_text(response.output_speech.ssml))


@sb.global_response_interceptor()
def log_response(handler_input, response):
    # Log response from alexa service
    print("Alexa Response: {}\n".format(response))


@sb.global_request_interceptor()
def log_request(handler_input):
    # Log request to alexa service
    print("Alexa Request: {}\n".format(handler_input.request_envelope.request))


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # Catch all exception handler, log exception and
    # respond with custom message
    print("Encountered following exception: {}".format(exception))

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


# Handler to be provided in lambda console.
handler = sb.lambda_handler()
