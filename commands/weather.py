import asyncio
import datetime as dt
import io
import logging
import os
from pprint import pprint

import aiohttp
import discord
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from PIL import Image

import helpers.database as database
import helpers.embed as embed
import helpers.themeparks as themeparks

BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
load_dotenv()
API_KEY = os.getenv("API_KEY")
CITY = "Chessington"
UNIT = "Imperial"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



async def get_parK_forecast(interaction, themepark):
    await interaction.response.defer()

    logging.getLogger('matplotlib.font_manager').disabled = True
    
    async with aiohttp.ClientSession() as session:
        destinations = database.get_user_destination_ids(interaction.user.id)
        matches = await themeparks.search_for_destinations(
            session, themepark, destinations
        )

        if len(matches) != 1:
            error_embed = embed.create_error_embed("Error")
            return await interaction.followup.send(embed=error_embed) 
        
        entity_data = await themeparks.get_entity(session, matches[0]["id"])
        
        # print(entity_data['name'])

        if "location" not in entity_data:
            return interaction.followup.send("No location found!")

        lon = entity_data["location"]['longitude']
        lat = entity_data["location"]['latitude']
    
        url = (
            f"{BASE_URL}&appid={API_KEY}"
            f"&lat={lat}&lon={lon}&units={UNIT}&cnt=40"
        )
        # print(url)
        
        weather_embed = embed.create_embed(
            title="Weather forecast.",
            description=''
        ) 

        # It was something i looked up lemme find it
        # https://www.geeksforgeeks.org/saving-a-plot-as-an-image-in-python/
        # Pass the io.BytesIO() instance
        # https://discordpy.readthedocs.io/en/stable/faq.html?highlight=frequently#how-do-i-use-a-local-image-file-for-an-embed-image
        
        async with session.get(url) as response:
            weather = await response.json()
            # pprint(weather)
            image_code = weather['list'][0]['weather'][0]['icon']
            image_link = f'http://openweathermap.org/img/w/{image_code}.png'
            embed.add_icon(weather_embed, image_link)

            plt.figure()

            plt.title("Forecast")
            plt.xlabel('Day')
            plt.ylabel('Temp')
            plt.grid()

            days = []
            temps = []
            
            #Graphing the weather for 
            for forecast in weather['list']:
                days.append(dt.datetime.fromtimestamp(forecast['dt']))
                temps.append(forecast['main']['temp'])
                # print(forecast['main']['temp'])
            
            plt.plot(days, temps)
            fig = plt.gcf()

            buf = io.BytesIO()
            fig.savefig(buf)
            buf.seek(0)

            file = discord.File(buf, filename="graph.png")
            weather_embed.set_image(url="attachment://graph.png")
            
        return await interaction.followup.send(embed=weather_embed, file=file)
    
# asyncio.run(get_parK_forecast())
