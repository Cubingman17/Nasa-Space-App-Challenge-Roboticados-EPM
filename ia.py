bpm = int(input('BPM average: '))
spO2 = int(input('Actual spO2: '))
sleep = 0
reaction = 0

def bpm_value():
    bpm_status = ''
    if bpm < 50:
        bpm_status = 'critical'
        
    elif bpm >= 50 and bpm < 60:
        bpm_status = 'atention'
    
    elif bpm >= 60 and bpm <= 100:
        if bpm < 80:
            bpm_status = 'normal'
        else:
            bpm_status = 'normal: nervous/stressed'
            
    elif bpm > 100 and bpm <= 120:
        bpm_status = 'atention'
        
    elif bpm > 120 and bpm <= 150:
        bpm_status = 'bad'
        
    elif bpm > 150:
        bpm_status = 'critical'
        
    return(bpm_status)

def spO2_value():
    spO2_status = ''
    if spO2 >= 95:
        spO2_status = 'normal'
        
    elif spO2 < 95 and spO2 >= 90:
        spO2_status = 'atention'
    
    elif spO2 < 90 and spO2 >= 85:
        spO2_status = 'bad'
    
    elif spO2 < 85:
        spO2_status = 'critical'
        
    return spO2_status

def sleep_value():
    sleep_status = ''
    if sleep >= 8:
        sleep_status = 'normal'
        
    elif sleep >= 7 and sleep < 8:
        sleep_status = 'normal: a little deficient'
    return sleep_status