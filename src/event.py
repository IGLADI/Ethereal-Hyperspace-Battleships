import random
import asyncio
import time
import discord
from data import RESOURCE_NAMES
from ui.simple_banner import NormalBanner, ErrorBanner

class Event:
    def __init__(self, id, description, category):
        self._id = id
        self._description = description
        self._category = category
        self._participants = []
        self._duration = 600 # in seconds
        self._prize = [random.choices(RESOURCE_NAMES, weights=[0, 0, 0, 50, 30, 20])[0], int((random.randint(1, 100)/2)+10)]
        self._completed = False

    @property
    def description(self):
        return self._description
    
    @property
    def category(self):
        return self._category
    
    @property
    def participants(self):
        return self._participants
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def prize(self):
        return self._prize
    
    @property
    def completed(self):
        return self._completed
    

class LocateEvent(Event):
    def __init__(self, id):
        super().__init__(id, "Ruebñ's fleet lost connection with a scout ship, can you locate it for him? It should be somewhere between (-100,-100) and (100,100).", EVENT_CATEGORY["locacte"])
        self._x_pos = random.randint(-100, 100)
        self._y_pos = random.randint(-100, 100)

class EventManager:
    def __init__(self, guild):
        self._events = {}
        self._guild = guild
        self._channel = discord.utils.get(guild.text_channels, name="events")

    @property
    def events(self):
        return self._events
    
    @events.setter
    def events(self, event):
        self._events += event

    def start_event_timer(self):
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.event_timer())

    async def event_timer(self):
        event_id = 0
        while True:
            event_id += 1
            # 1 = LocateEvent | 2 = SolveEvent
            # TODO MAKE 9
            if random.randint(1, 1) == 1:
                event = LocateEvent(event_id)
                self._events[event_id] = event
                banner = NormalBanner(
                    text=f"@everyone, a new event started!\n {event.description}.\n You have 10minutes!\n Prize: {event.prize[1]} tons of {event.prize[0]}\n You can join by typing /join_event.",
                    user=self._guild.me,
                )
                await self._channel.send(embed=banner.embed)
                await self.end_timer(event_id)
            # Every 30 minutes
            await asyncio.sleep(1800)

    async def end_timer(self, event_id):
        await asyncio.sleep(self._events[event_id].duration)
        if self._events[event_id].completed == False:
            banner = ErrorBanner(
                text=f"The event ended! The task was not successful...\nBetter luck next time!\n",
                user=self._guild.me,
            )
            await self._channel.send(embed=banner.embed)
        self._events.pop(event_id)

EVENT_CATEGORY = {
    "locacte": "locate",
}