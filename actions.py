# This file contains your custom actions for the career counsellor chatbot.

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
import logging
from careers import CAREER_DATA

logger = logging.getLogger(__name__)

class ActionRecommendCareer(Action):
    """
    Custom action to recommend career paths based on user interests.
    It identifies the interest category from the latest user intent
    and provides detailed career information from CAREER_DATA.
    """

    def name(self) -> Text:
        """Returns the name of the action (must match 'actions' in domain.yml)."""
        return "action_recommend_career"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Safe access to the latest intent name
        latest_intent = tracker.latest_message.get('intent', {}).get('name')
        logger.info(f"Latest intent detected by Rasa: {latest_intent}")

        # Mapping of categories
        interest_category_map = {
            "inform_tech_interest": "tech",
            "inform_arts_interest": "arts",
            "inform_commerce_interest": "commerce",
            "inform_health_interest": "health",
            "inform_creative_interest": "creative",
            "inform_analytical_interest": "analytical",
            "inform_social_interest": "social",
            "inform_practical_interest": "practical"
        }

        interest_category = interest_category_map.get(latest_intent)

        if interest_category and interest_category in CAREER_DATA:
            careers_in_category = CAREER_DATA[interest_category]

            if careers_in_category:
                # Suggest top 3 random careers from the category
                career_names = random.sample(list(careers_in_category.keys()), 
                                             min(3, len(careers_in_category)))

                buttons = [
                    {
                        "title": name,
                        "payload": f'/select_career{{"career": "{name}"}}'
                    } for name in career_names
                ]

                dispatcher.utter_message(
                    text="Here are some career paths that match your interests. Would you like to know more about any of these?",
                    buttons=buttons
                )

                chosen_career_name = random.choice(career_names)
                chosen_career_info = careers_in_category[chosen_career_name]
                message = (
                    f"### Career Path: {chosen_career_name}\n\n"
                    f"**Description:** {chosen_career_info['description']}\n\n"
                    f"**Key Skills:** {', '.join(chosen_career_info['skills'])}\n\n"
                    f"**Typical Education:** {chosen_career_info['education']}\n\n"
                    f"**Possible Further Paths:** {', '.join(chosen_career_info['paths'])}\n\n"
                    f"**Useful Resources:** {', '.join(chosen_career_info['resources'])}\n\n"
                    "I hope this helps! Would you like to explore other careers or tell me more about your preferences?"
                )
                dispatcher.utter_message(text=message)
                
                logger.info(f"Recommended career: {chosen_career_name} in category '{interest_category}'")

                return [
                    SlotSet("last_recommended_category", interest_category),
                    SlotSet("last_recommended_career", chosen_career_name)
                ]
            else:
                logger.warning(f"Category '{interest_category}' found, but no careers defined.")
                dispatcher.utter_message(response="utter_default_recommendation")
                return []

        else:
            logger.warning(f"No valid interest category matched for intent: {latest_intent}")
            dispatcher.utter_message(response="utter_default_recommendation")
            return []

print("actions.py loaded successfully!!!")
#actions folder should be deleted if actions.py is used in the same directory as the main file.