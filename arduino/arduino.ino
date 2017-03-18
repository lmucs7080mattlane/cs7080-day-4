#include <Firmata.h>
#include <pitches.h>

const int LED_PIN = 13;
const int BUTTON_PIN = 9;
const int BUZZER_PIN = 8;

const int TONE_LOOP_NUM_NOTES = 5;
const int TONE_LOOP_NOTES[TONE_LOOP_NUM_NOTES] = {NOTE_C5, NOTE_D5, NOTE_E5, NOTE_F5, NOTE_G5};

// Firmata commands
const byte FIRMATA_ALERT = 0x01;
const byte FIRMATA_CHECK_BUTTON_STRING = 0x02;
const byte FIRMATA_CHECK_BUTTON_INTEGER = 0x03;

int alert = 0;

void firmata_init(){
    Firmata.setFirmwareVersion(1, 0);
    Firmata.attach(START_SYSEX, firmata_sysex_callback);
    Firmata.begin(57600);
}

void turn_led_on(){
    digitalWrite(LED_PIN, HIGH);
}

void turn_led_off(){
    digitalWrite(LED_PIN, LOW);
}

void play_tone(int note, int milliseconds){
    tone(BUZZER_PIN, note, milliseconds);
}

int current_beep_count = 0;
int current_beep_tone = 0;
void occasionally_beep(int beep_modulo, int beep_duration){
    if(current_beep_count++ % beep_modulo == 0){
        play_tone(TONE_LOOP_NOTES[current_beep_tone++], beep_duration);
    }
    current_beep_count = current_beep_count % beep_modulo;
    current_beep_tone = current_beep_tone % TONE_LOOP_NUM_NOTES;
}

void firmata_sysex_callback(byte command, byte argc, byte *argv)
{  
    switch (command) {
        case FIRMATA_ALERT:
            // First and only byte should be the alert Boolean parameter
            if (argv[0]) {
                alert = 1;
                turn_led_on();
            }
            else {
                alert = 0;
                turn_led_off();
            }
            break;
        case FIRMATA_CHECK_BUTTON_STRING:
            if (digitalRead(BUTTON_PIN) == HIGH) {
                Firmata.sendString("1Button is pressed");
            }
            else {
                Firmata.sendString("1Button is not pressed");
            }
            break;
        case FIRMATA_CHECK_BUTTON_INTEGER:
            String msgPrefix = "2";
            String msg = msgPrefix + digitalRead(BUTTON_PIN);
            int str_len = msg.length() + 1;
            char char_array[str_len];
            msg.toCharArray(char_array, str_len);
            Firmata.sendString(char_array);
            break;
    }
}

void setup(){
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    firmata_init();
}

void loop(){
    while(Firmata.available()) {
        Firmata.processInput();
    }
    if(alert){
        occasionally_beep(2, 20);
    }
    delay(200);
}
