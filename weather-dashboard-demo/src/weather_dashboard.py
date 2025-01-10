import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv

#Load Environment Variables
load_dotenv()

#Weather Dashboard Class
class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.s3_client = boto3.client('s3')
        
    def create_bucket_if_not_exists(self):
        """Creating an S3 Bucket if it does not exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} already exists.")
        except:
            print(f"Bucket {self.bucket_name} does not exist. Creating it now.")

        try:
            """Simpler Creation for the Bucket"""
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} created successfully.")
        except Exception as e:
            print(f"Error creating bucket: {e}")
    
    def fetch_weather(self, city):
        """Fetching weather data from OpenWeather API"""
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "imperial"
        } 
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def save_to_s3(self, weather_data, city):
        """Saving weather data to S3 Bucket"""
        if not weather_data:
            return False
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"weather-data/{city}-{timestamp}.json"
        
        try:
            weather_data['timestamp'] = timestamp
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(weather_data),
                ContentType='application/json'
            )
            print(f"Weather data saved to S3: {file_name}")
            return True
        except Exception as e:
            print(f"Error saving weather data to S3: {e}")
            return False

def main():
    """Main Function"""
    
    dashboard = WeatherDashboard()
    
    #Create S3 Bucket if it does not exist
    dashboard.create_bucket_if_not_exists()
    
    cities = ["Los Angeles", "Dallas", "Orlando"]
    
    for city in cities:
        print(f"Fetching weather data for {city}")
        weather_data = dashboard.fetch_weather(city)
        if weather_data:
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humudity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            
            print(f"Temperature: {temp}°F")
            print(f"Feels Like: {feels_like}°F")
            print(f"Humidity: {humudity}%")
            print(f"Description: {description}")
            
            #Save weather data to S3
            success = dashboard.save_to_s3(weather_data, city)
            if success:
                print("Weather data saved to S3 successfully.")
            else:
                print(f"Failed to save weather data to S3 for {city}.")

if __name__ == "__main__":
    main()
            