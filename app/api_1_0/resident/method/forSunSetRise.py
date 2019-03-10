import math
import datetime

def transfer_time(value):
    if (value is None):
        return None
    else:
        hours, remainder = divmod(value, 3600)
        minutes, seconds = divmod(remainder, 60)
        if(hours == 0):
            hours = str(hours)+'0'
        if(minutes == 0):
            minutes = str(minutes)+'0'
        if(seconds == 0):
            seconds = str(seconds)+'0'
        return  '{}:{}:{}'.format(hours, minutes, seconds)


def sun_time(longitude,latitude):
    coords = {'longitude' : longitude, 'latitude' : latitude }

# Sunrise time UTC (decimal, 24 hour format)
    TimeSunrise = getSunriseTime( coords )['decimal'] + 8

# Sunset time UTC (decimal, 24 hour format)
    TimeSunset = getSunsetTime( coords )['decimal'] + 8

    if TimeSunset >= 24:
        TimeSunset = TimeSunset-24
    if TimeSunrise >= 24:
        TimeSunrise = TimeSunrise-24

    TimeSunrise = transfer_time(int(TimeSunrise * 3600))
    TimeSunset = transfer_time(int(TimeSunset * 3600))

    print("TimeSunrise:",TimeSunrise)
    print("TimeSunset:",TimeSunset)

    return TimeSunrise,TimeSunset

def getSunriseTime(coords):
    return calcSunTime( coords, True )

def getSunsetTime(coords):
    return calcSunTime( coords, False )

def getCurrentUTC():
    now = datetime.datetime.now()
    return  now.day, now.month, now.year 


def calcSunTime(coords, isRiseTime, zenith = 90.8 ):

    # isRiseTime == False, returns sunsetTime

    day, month, year = getCurrentUTC()

    longitude = coords['longitude']
    latitude = coords['latitude']

    TO_RAD = math.pi/180

    #1. first calculate the day of the year
    N1 = math.floor(275 * month / 9)
    N2 = math.floor((month + 9) / 12)
    N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30

    #2. convert the longitude to hour value and calculate an approximate time
    lngHour = longitude / 15

    if isRiseTime:
        t = N + ((6 - lngHour) / 24)
    else: #sunset
        t = N + ((18 - lngHour) / 24)

    #3. calculate the Sun's mean anomaly
    M = (0.9856 * t) - 3.289

    #4. calculate the Sun's true longitude
    L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
    L = forceRange( L, 360 ) #NOTE: L adjusted into the range [0,360)

    #5a. calculate the Sun's right ascension

    RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
    RA = forceRange( RA, 360 ) #NOTE: RA adjusted into the range [0,360)

    #5b. right ascension value needs to be in the same quadrant as L
    Lquadrant  = (math.floor( L/90)) * 90
    RAquadrant = (math.floor(RA/90)) * 90
    RA = RA + (Lquadrant - RAquadrant)

    #5c. right ascension value needs to be converted into hours
    RA = RA / 15

    #6. calculate the Sun's declination
    sinDec = 0.39782 * math.sin(TO_RAD*L)
    cosDec = math.cos(math.asin(sinDec))

    #7a. calculate the Sun's local hour angle
    cosH = (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*latitude))) / (cosDec * math.cos(TO_RAD*latitude))

    if cosH > 1:
        return {'status': False, 'msg': 'the sun never rises on this location (on the specified date)'}

    if cosH < -1:
        return {'status': False, 'msg': 'the sun never sets on this location (on the specified date)'}

    #7b. finish calculating H and convert into hours

    if isRiseTime:
        H = 360 - (1/TO_RAD) * math.acos(cosH)
    else: #setting
        H = (1/TO_RAD) * math.acos(cosH)

    H = H / 15

    #8. calculate local mean time of rising/setting
    T = H + RA - (0.06571 * t) - 6.622

    #9. adjust back to UTC
    UT = T - lngHour
    UT = forceRange( UT, 24) # UTC time in decimal format (e.g. 23.23)

    #10. Return
    hr = forceRange(int(UT), 24)
    min = round((UT - int(UT))*60,0)

    return {
        'status': True,
        'decimal': UT,
        'hr': hr,
        'min': min 
    }

def forceRange(  v, max ):
    # force v to be >= 0 and < max
    if v < 0:
        return v + max
    elif v >= max:
        return v - max
    
    return v