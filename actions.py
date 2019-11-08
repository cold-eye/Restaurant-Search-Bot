# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,UserUtteranceReverted
import zomatoApi

class ActionGreetUser(Action):
    """
    Greet user for the first time he has opened the bot windows
    """
    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_template("utter_greet_user", tracker)        
        return [UserUtteranceReverted()] 

class ActionSearchRestaurants(Action):
    """
    Search the restaurants using location & cuisine.

    Required Parameters: Location, Cuisine
    """
    def name(self) -> Text:
        return "action_search_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print()
        print("====Inside ActionSearchRestaurants====")
        print()

        ## extract the required slots
        location=tracker.get_slot("location")
        cuisine=tracker.get_slot("cuisine")
        lat=tracker.get_slot("latitude")
        lon=tracker.get_slot("longitude")
        entity_id=tracker.get_slot("location_id")
        entity_type=tracker.get_slot("location_type")
        city_id=tracker.get_slot("city_id")

        ## extract the entities
        locationEntity=next(tracker.get_latest_entity_values("location"), None)
        cuisineEntity=next(tracker.get_latest_entity_values("cuisine"), None)
        user_locationEntity=next(tracker.get_latest_entity_values("user_location"), None)
        latEntity=next(tracker.get_latest_entity_values("latitude"), None)
        lonEntity=next(tracker.get_latest_entity_values("longitude"), None)

        ## if we latitude & longitude entities are found, set it to slot
        if(latEntity and lonEntity):
            lat=latEntity
            lon=lonEntity
        
        ## if user wants to search restaurants in his current location
        if(user_locationEntity or (latEntity and lonEntity) ):
            ##check if we already have the user location coordinates stoed in slots
            if(lat==None and lon==None):
                dispatcher.utter_message("Sure, please allow me to access your location 🧐")
                dispatcher.utter_custom_json({"payload":"location"})
                return []
            else:
                locationEntities=zomatoApi.getLocationDetailsbyCoordinates(lat,lon)
                location=locationEntities["title"]
                city_id=locationEntities["city_id"]
                entity_id=locationEntities["entity_id"]
                entity_type=locationEntities["entity_type"]
                
                ## store the user provided details to slot
                SlotSet("location", locationEntities["title"])
                SlotSet("city_id", locationEntities["city_id"])
                SlotSet("location_id", locationEntities["entity_id"])
                SlotSet("location_type", locationEntities["entity_type"])

        ## if user wants to search restaurants by location name
        if(locationEntity):
            locationEntities=zomatoApi.getLocationDetailsbyName(locationEntity)
            if(locationEntities["restaurants_available"]=="no"):
                dispatcher.utter_message("Sorry I couldn't find any restaurants  😓")
                return []
            entity_id=locationEntities["entity_id"]
            entity_type=locationEntities["entity_type"]
            city_id=locationEntities["city_id"]
            SlotSet("location", locationEntities["title"])

        ##get the cuisine id for the cuisine name user provided
        cuisine_id=zomatoApi.getCuisineId(cuisine,city_id)
        
        print("Entities:  ",entity_id," ",entity_type," ",cuisine_id," ",location," ",cuisine)
        print()

        ## if we didn't find the restaurant for which user has provided the cuisine name
        if(cuisine_id==None):
            dispatcher.utter_message("Sorry we couldn't find any restaurants that serves {} cuisine in {}".format(cuisine,location))
            return [UserUtteranceReverted()] 
        else:
            ## search the restaurts by calling zomatoApi api
            restaurants=zomatoApi.searchRestaurants(entity_id,entity_type, cuisine_id,"")

            ## check if restaurants found
            if(len(restaurants)>0):
                dispatcher.utter_message("Here are the few restaurants that matches your preferences 😋")
                dispatcher.utter_custom_json({"payload":"cardsCarousel","data":restaurants})
                return []
                
            dispatcher.utter_message("Sorry we couldn't find any restaurants that serves {} cuisine in {} 😞".format(cuisine,location))
            return [UserUtteranceReverted()] 
            
           
class ActionSearchBestRestaurants(Action):
    """
    Search the best restaurants using location.
    
    Required Parameters: Location
    """
    def name(self) -> Text:
        return "action_search_best_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print()
        print("======Inside Action Search Best Restaurants====")
        print()

        ## extract the required slots
        location=tracker.get_slot("location")
        cuisine=tracker.get_slot("cuisine")
        lat=tracker.get_slot("latitude")
        lon=tracker.get_slot("longitude")
        entity_id=tracker.get_slot("location_id")
        entity_type=tracker.get_slot("location_type")
        city_id=tracker.get_slot("city_id")

        ## extract the entities
        locationEntity=next(tracker.get_latest_entity_values("location"), None)
        cuisineEntity=next(tracker.get_latest_entity_values("cuisine"), None)
        user_locationEntity=next(tracker.get_latest_entity_values("user_location"), None)
        latEntity=next(tracker.get_latest_entity_values("latitude"), None)
        lonEntity=next(tracker.get_latest_entity_values("longitude"), None)

        ## if we latitude & longitude entities are found, set it to slot
        if(latEntity and lonEntity):
            lat=latEntity
            lon=lonEntity

        ## if user wants to search the best restaurants in his current location
        if(user_locationEntity or (latEntity and lonEntity) ):
            ##check if we already have the user location coordinates stoed in slots
            if(lat==None and lon==None):
                dispatcher.utter_message("Sure, please allow me to access your location 🧐")
                dispatcher.utter_custom_json({"payload":"location"})
                return []
            else:
                locationEntities=zomatoApi.getLocationDetailsbyCoordinates(lat,lon)
                location=locationEntities["title"]
                city_id=locationEntities["city_id"]
                entity_id=locationEntities["entity_id"]
                entity_type=locationEntities["entity_type"]
                
                ## store the user provided details to slot
                SlotSet("location", locationEntities["title"])
                SlotSet("city_id", locationEntities["city_id"])
                SlotSet("location_id", locationEntities["entity_id"])
                SlotSet("location_type", locationEntities["entity_type"])

        ## if user wants to search best restaurants by location name
        if(locationEntity):
            locationEntities=zomatoApi.getLocationDetailsbyName(locationEntity)
            entity_id=locationEntities["entity_id"]
            entity_type=locationEntities["entity_type"]
            city_id=locationEntities["city_id"]

        print("Entities: ",entity_id," ",entity_type," ",city_id," ",locationEntity)
        
        ## search the best restaurts by calling zomatoApi api
        restaurants=zomatoApi.getLocationDetails(entity_id,entity_type)
        
        ## check if restaurants details found
        if(len(restaurants)>0):
                dispatcher.utter_message("Here are few top rated restaurants that I have found 🤩")
                dispatcher.utter_custom_json({"payload":"cardsCarousel","data":restaurants["best_restaurants"]})
                return []
                
        dispatcher.utter_message("Sorry we couldn't find any best restaurants ☹️".format(cuisine,location))
        return [UserUtteranceReverted()]
        

class ActionSearchRestaurantsWithoutCuisine(Action):
    """
    Search the best restaurants using location and user is fine with any cuisine.
    
    Required Parameters: Location
    """
    def name(self) -> Text:
        return "action_search_restaurants_without_cuisine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("====Inside ActionSearchRestaurants Without Cuisine====")
        print()
        location=tracker.get_slot("location")
        cuisine=tracker.get_slot("cuisine")
        lat=tracker.get_slot("latitude")
        lon=tracker.get_slot("longitude")
        entity_id=tracker.get_slot("location_id")
        entity_type=tracker.get_slot("location_type")
        city_id=tracker.get_slot("city_id")

        locationEntity=next(tracker.get_latest_entity_values("location"), None)
        cuisineEntity=next(tracker.get_latest_entity_values("cuisine"), None)
        user_locationEntity=next(tracker.get_latest_entity_values("user_location"), None)
        
        ##set the cuisine to any of the cuisine name or you leave it empyt
        cuisine_id=""
        restaurants=zomatoApi.searchRestaurants(entity_id,entity_type, cuisine_id,"")
        dispatcher.utter_message("Here are the few restaurants I have found 😋!!!")
        dispatcher.utter_custom_json({"payload":"cardsCarousel","data":restaurants})

class ActionAskCuisine(Action):
    """
    Prompt user for cuisine with the top cuisines in the user provided location

    Required Parameters: Location
    """
    def name(self) -> Text:
        return "action_ask_cuisine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print()
        print("====Inside ActionAskCuisine====")
        print()
        location=tracker.get_slot("location")
        cuisine=tracker.get_slot("cuisine")
        lat=tracker.get_slot("latitude")
        lon=tracker.get_slot("longitude")
        
        locationEntity=next(tracker.get_latest_entity_values("location"), None)
        cuisineEntity=next(tracker.get_latest_entity_values("cuisine"), None)
        user_locationEntity=next(tracker.get_latest_entity_values("user_location"), None)
        latEntity=next(tracker.get_latest_entity_values("latitude"), None)
        lonEntity=next(tracker.get_latest_entity_values("longitude"), None)

        location=tracker.get_slot("location")
        cuisine=tracker.get_slot("cuisine")
        lat=tracker.get_slot("latitude")
        lon=tracker.get_slot("longitude")
        entity_id=tracker.get_slot("location_id")
        entity_type=tracker.get_slot("location_type")
        city_id=tracker.get_slot("city_id")

       
        if(latEntity and lonEntity):
            lat=latEntity
            lon=lonEntity

        if(user_locationEntity or (latEntity and lonEntity) ):
            if(lat==None and lon==None):
                dispatcher.utter_message("Sure, please allow me to access your location 🧐")
                dispatcher.utter_custom_json({"payload":"location"})
                return []
            else:
                locationEntities=zomatoApi.getLocationDetailsbyCoordinates(lat,lon)
                location=locationEntities["title"]
                city_id=locationEntities["city_id"]
                entity_id=locationEntities["entity_id"]
                entity_type=locationEntities["entity_type"]

                SlotSet("location", locationEntities["title"])
                SlotSet("city_id", locationEntities["city_id"])
                SlotSet("location_id", locationEntities["entity_id"])
                SlotSet("location_type", locationEntities["entity_type"])


        if(locationEntity):
            locationEntities=zomatoApi.getLocationDetailsbyName(locationEntity)
            entity_id=locationEntities["entity_id"]
            entity_type=locationEntities["entity_type"]
            city_id=locationEntities["city_id"]
            SlotSet("location", locationEntities["title"])

        
        print("locationDetails: ",locationEntities)
        print()

        ## check if the restaurants are available in the user provided location
        if(locationEntities["restaurants_available"]=="no"):
            dispatcher.utter_message("Sorry, No restaurants available in the location you have  provided 🤯")
            return [UserUtteranceReverted()] 

        else:
            locationDetails=zomatoApi.getLocationDetails(locationEntities["entity_id"],locationEntities["entity_type"])

            dispatcher.utter_template("utter_ask_cuisine", tracker)
            dispatcher.utter_custom_json({"payload":"quickReplies","data":locationDetails["top_cuisines"]})
        
            return [SlotSet("city_id", locationEntities["city_id"]),SlotSet("location_id", locationEntities["entity_id"]),SlotSet("location_type", locationEntities["entity_type"])]

        
