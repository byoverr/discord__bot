import requests
from pprint import pprint


class Weather():
    def __init__(self, name_of_city):
        self.name_of_city = name_of_city
        weather_server = ' https://api.weather.yandex.ru/v2/informers?'
        pos = f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b' \
              f'&geocode={name_of_city}&format=json'
        res = requests.get(pos).json()
        lonn, latt = res['response']["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'].split()
        weather_params = {

            "lat": latt,
            "lon": lonn,
            "lang": "ru_RU",
        }
        headers = {"X-Yandex-API-Key": "04d2b3be-c32f-4568-91ff-4a95ab1509e6"}
        response = requests.get(weather_server, params=weather_params, headers=headers).json()

        self.weather_tomorrow = response["forecast"]["parts"][1]
        self.condition_tomorrow = self.weather_conditions(self.weather_tomorrow)
        self.wind_dir_tomorrow = self.wind_direction(self.weather_tomorrow)
        self.weather_daytime_tomorrow = self.daytime(self.weather_tomorrow)
        self.win_speed_tomorrow = self.wind_sped(self.wind_dir_tomorrow, self.weather_tomorrow)
        self.temp_min_tomorrow = self.weather_tomorrow["temp_min"]
        self.temp_max_tomorrow = self.weather_tomorrow["temp_max"]
        self.feels_weather_tomorrow = self.weather_tomorrow["feels_like"]

        self.weather = response["fact"]
        self.wind_dir = self.wind_direction(self.weather)
        self.weather_daytime = self.daytime(self.weather)
        self.condition = self.weather_conditions(self.weather)
        self.wind_speed = self.wind_sped(self.wind_dir, self.weather)
        self.temp = self.weather["temp"]
        self.feels_weather = self.weather["feels_like"]
        self.pressure_mm = self.weather["pressure_mm"]

    def wind_direction(self, weather):
        if weather["wind_dir"] == 'n':
            return 'Ветер Северный'
        elif weather["wind_dir"] == 'nw':
            return 'Ветер Северо-Западный'
        elif weather["wind_dir"] == 'w':
            return 'Ветер Западный'
        elif weather["wind_dir"] == 'sw':
            return 'Ветер Юго-Западный'
        elif weather["wind_dir"] == 's':
            return 'Ветер Южный'
        elif weather["wind_dir"] == 'se':
            return 'Ветер Юго-Восточный'
        elif weather["wind_dir"] == 'e':
            return 'Ветер Восточный'
        elif weather["wind_dir"] == 'ne':
            return 'Ветер Северо-Восточный'
        else:
            return 'Штиль'

    def daytime(self, weather):
        if weather["daytime"] == 'd':
            return 'Светлое время суток'
        else:
            return 'Темное время суток'

    def weather_conditions(self, weather):
        if weather["condition"] == 'clear':
            return 'ясно'
        elif weather["condition"] == 'partly-cloudy':
            return 'малооблачно'
        elif weather["condition"] == 'cloudy':
            return 'облачно с прояснениями'
        elif weather["condition"] == 'overcast':
            return 'пасмурно'
        elif weather["condition"] == 'drizzle':
            return 'морось'
        elif weather["condition"] == 'light-rain':
            return 'небольшой дождь'
        elif weather["condition"] == 'rain':
            return 'дождь'
        elif weather["condition"] == 'moderate-rain':
            return 'умеренно сильный дождь'
        elif weather["condition"] == 'heavy-rain':
            return 'сильный дождь'
        elif weather["condition"] == 'continuous-heavy-rain':
            return 'длительный сильный дождь'
        elif weather["condition"] == 'showers':
            return 'ливень'
        elif weather["condition"] == 'wet-snow':
            return 'дождь со снегом'
        elif weather["condition"] == 'light-snow':
            return 'небольшой снег'
        elif weather["condition"] == 'snow':
            return 'снег'
        elif weather["condition"] == 'snow-showers':
            return 'снегопад'
        elif weather["condition"] == 'hail':
            return 'град'
        elif weather["condition"] == 'thunderstorm':
            return 'гроза'
        elif weather["condition"] == 'thunderstorm-with-rain':
            return 'дождь с грозой'
        elif weather["condition"] == 'thunderstorm-with-hail':
            return 'гроза с градом'

    def wind_sped(self, dir, weather):
        if dir != 'Штиль':
            return f'Скорость ветра {weather["wind_speed"]} м/с ,' \
                         f' возможны порывы ветра до {weather["wind_gust"]} м/с'
        else:
            return ''

    def form_answer_today(self):
        return f'Сейчас в **{self.name_of_city}**\n' \
               f'{self.weather_daytime}, {self.condition}.\n' \
               f'На улице {self.temp} градусов, ощущается, как {self.feels_weather}.\n' \
               f'{self.wind_dir}. {self.wind_speed}.\n' \
               f'Давление {self.pressure_mm} мм ртутного столба'

    def form_answer_tomorrow(self):
        return f'Завтра в **{self.name_of_city}**\n' \
               f'{self.weather_daytime_tomorrow}. Будет {self.condition_tomorrow}.\n' \
               f'Температура будет колебаться от {self.temp_min_tomorrow} до {self.temp_max_tomorrow} градусов,' \
               f' ощущаться как {self.feels_weather_tomorrow}.\n' \
               f'Ожидается {self.wind_dir_tomorrow}, {self.win_speed_tomorrow}'